"""
Kafka Producer and Consumer
"""
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from typing import Optional, Dict, Any, Callable
import json
import asyncio
from functools import wraps
import threading
import time

from app.core.config import settings
from app.core.logging import logger


class KafkaProducerClient:
    """Kafka producer client"""
    
    def __init__(self):
        self._producer: Optional[KafkaProducer] = None
    
    def get_producer(self) -> KafkaProducer:
        """Get or create Kafka producer"""
        if self._producer is None:
            self._producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS.split(','),
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                max_request_size=settings.KAFKA_MAX_REQUEST_SIZE,
                batch_size=settings.KAFKA_BATCH_SIZE,
                acks=1,  # Wait for leader acknowledgment
                compression_type='gzip',
            )
        return self._producer
    
    def send_message(
        self,
        topic: str,
        message: Dict[str, Any],
        key: Optional[str] = None
    ) -> bool:
        """Send message to Kafka topic"""
        try:
            producer = self.get_producer()
            future = producer.send(
                topic,
                value=message,
                key=key
            )
            # Wait for message to be sent
            record_metadata = future.get(timeout=10)
            logger.info(
                f"Message sent to topic {record_metadata.topic} "
                f"partition {record_metadata.partition} "
                f"offset {record_metadata.offset}"
            )
            return True
        except KafkaError as e:
            logger.error(f"Failed to send message to Kafka: {e}")
            return False
    
    def close(self):
        """Close producer"""
        if self._producer:
            self._producer.close()
            self._producer = None


class KafkaConsumerClient:
    """Kafka consumer client"""
    
    def __init__(self, topics: list, group_id: Optional[str] = None):
        self.topics = topics
        self.group_id = group_id or settings.KAFKA_GROUP_ID
        self._consumer: Optional[KafkaConsumer] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
    
    def get_consumer(self) -> KafkaConsumer:
        """Get or create Kafka consumer"""
        if self._consumer is None:
            self._consumer = KafkaConsumer(
                *self.topics,
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS.split(','),
                group_id=self.group_id,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
                auto_offset_reset='earliest',
                enable_auto_commit=False,
                max_poll_records=100,
                max_poll_interval_ms=900000,
                heartbeat_interval_ms=5000,
            )
        return self._consumer
    
    def start_consuming(self, message_handler: Callable[[Dict[str, Any]], None]):
        """Start consuming messages in a separate thread"""
        if self._running:
            logger.warning("Consumer is already running")
            return
        
        self._running = True
        
        def consume_loop():
            consumer = self.get_consumer()
            try:
                while self._running:
                    message_pack = consumer.poll(timeout_ms=1000)
                    for topic_partition, messages in message_pack.items():
                        for message in messages:
                            try:
                                message_handler(message.value)
                                # Commit offset after successful processing
                                consumer.commit()
                            except Exception as e:
                                logger.error(f"Error processing message: {e}")
            except Exception as e:
                logger.error(f"Consumer error: {e}")
            finally:
                consumer.close()
        
        self._thread = threading.Thread(target=consume_loop, daemon=True)
        self._thread.start()
        logger.info(f"Started Kafka consumer for topics: {self.topics}")
    
    def stop_consuming(self):
        """Stop consuming messages"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        if self._consumer:
            self._consumer.close()
            self._consumer = None
        logger.info("Stopped Kafka consumer")


# Global producer instance
kafka_producer = KafkaProducerClient()


# Message sending helper
def send_kafka_message(topic: str, message: Dict[str, Any], key: Optional[str] = None) -> bool:
    """Send message to Kafka topic"""
    return kafka_producer.send_message(topic, message, key)


# Test execution result notification
def notify_test_execution_result(
    test_id: str,
    test_type: str,
    status: str,
    result: Dict[str, Any],
    project_id: Optional[str] = None
):
    """Send test execution result notification to Kafka"""
    message = {
        "test_id": test_id,
        "test_type": test_type,  # api_test, functional_case, test_plan
        "status": status,  # success, failed, running
        "result": result,
        "project_id": project_id,
        "timestamp": time.time()
    }
    return send_kafka_message("test_execution_results", message, key=test_id)

