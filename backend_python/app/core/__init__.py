"""
Core modules
"""
from app.core.config import settings, get_settings
from app.core.redis import redis_client, get_redis
from app.core.kafka import kafka_producer, send_kafka_message, notify_test_execution_result
from app.core.minio import minio_client, get_minio
from app.core.celery_app import celery_app, get_celery_app

__all__ = [
    "settings",
    "get_settings",
    "redis_client",
    "get_redis",
    "kafka_producer",
    "send_kafka_message",
    "notify_test_execution_result",
    "minio_client",
    "get_minio",
    "celery_app",
    "get_celery_app",
]
