"""
Middleware Usage Examples

This file demonstrates how to use the middleware components in the application.
"""

# Redis Usage Example
async def redis_example():
    """Example of using Redis for session, cache, and distributed lock"""
    from app.core.redis import redis_client
    
    # Session storage
    await redis_client.set_session("session_123", "user_456", {"role": "admin"})
    session = await redis_client.get_session("session_123")
    await redis_client.delete_session("session_123")
    
    # Cache
    await redis_client.set_cache("user:123", {"name": "John", "email": "john@example.com"}, expire=3600)
    user_data = await redis_client.get_cache("user:123")
    await redis_client.delete_cache("user:123")
    
    # Distributed lock
    async with await redis_client.lock_context("resource_lock", timeout=10, expire=30):
        # Critical section code here
        pass


# Kafka Usage Example
def kafka_example():
    """Example of using Kafka for message sending"""
    from app.core.kafka import send_kafka_message, notify_test_execution_result
    
    # Send general message
    send_kafka_message(
        topic="test_topic",
        message={"key": "value", "data": "test"},
        key="message_key"
    )
    
    # Send test execution result notification
    notify_test_execution_result(
        test_id="test_123",
        test_type="api_test",
        status="success",
        result={"passed": 10, "failed": 0},
        project_id="project_456"
    )


# MinIO Usage Example
def minio_example():
    """Example of using MinIO for file operations"""
    from app.core.minio import minio_client
    
    # Upload file
    file_data = b"file content"
    file_path = minio_client.upload_file(
        file_path="project/123/test.txt",
        file_data=file_data,
        content_type="text/plain"
    )
    
    # Download file
    downloaded_data = minio_client.download_file(file_path)
    
    # List files
    files = minio_client.list_files("project/123/")
    
    # Get presigned URL
    from datetime import timedelta
    url = minio_client.get_presigned_url(file_path, expires=timedelta(hours=1))
    
    # Delete file
    minio_client.delete_file(file_path)


# Celery Usage Example
def celery_example():
    """Example of using Celery for async tasks"""
    from app.tasks.test_execution import execute_api_test_task, execute_test_plan_task
    from app.tasks.report_generation import generate_test_report_task
    
    # Execute API test asynchronously
    task = execute_api_test_task.delay("test_case_123", "env_456")
    result = task.get(timeout=60)  # Wait for result
    
    # Execute test plan asynchronously
    task = execute_test_plan_task.delay("plan_123", "env_456")
    
    # Generate report asynchronously
    task = generate_test_report_task.delay("report_123")

