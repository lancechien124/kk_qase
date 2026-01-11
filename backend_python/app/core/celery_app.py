"""
Celery Configuration for Task Scheduling
"""
from celery import Celery
from celery.schedules import crontab
from typing import Dict, Any
import os

from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "metersphere",
    broker=f"redis://{settings.REDIS_URL.split('//')[-1]}",  # Use Redis as broker
    backend=f"redis://{settings.REDIS_URL.split('//')[-1]}",  # Use Redis as result backend
    include=[
        "app.tasks.test_execution",
        "app.tasks.report_generation",
        "app.tasks.scheduled_tasks",
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    task_soft_time_limit=3300,  # 55 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    result_expires=3600,  # 1 hour
    broker_connection_retry_on_startup=True,
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    # Test plan scheduled execution
    "execute-scheduled-test-plans": {
        "task": "app.tasks.scheduled_tasks.execute_scheduled_test_plans",
        "schedule": crontab(minute="*/5"),  # Every 5 minutes
    },
    # Cleanup old reports
    "cleanup-old-reports": {
        "task": "app.tasks.scheduled_tasks.cleanup_old_reports",
        "schedule": crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    # Generate daily statistics
    "generate-daily-statistics": {
        "task": "app.tasks.scheduled_tasks.generate_daily_statistics",
        "schedule": crontab(hour=1, minute=0),  # Daily at 1 AM
    },
}


@celery_app.task(bind=True, name="app.tasks.test_execution.execute_api_test")
def execute_api_test_task(self, test_case_id: str, environment_id: str = None):
    """Execute API test asynchronously"""
    # This will be implemented in app/tasks/test_execution.py
    pass


@celery_app.task(bind=True, name="app.tasks.test_execution.execute_test_plan")
def execute_test_plan_task(self, plan_id: str, environment_id: str = None):
    """Execute test plan asynchronously"""
    # This will be implemented in app/tasks/test_execution.py
    pass


@celery_app.task(bind=True, name="app.tasks.report_generation.generate_test_report")
def generate_test_report_task(self, report_id: str):
    """Generate test report asynchronously"""
    # This will be implemented in app/tasks/report_generation.py
    pass


def get_celery_app() -> Celery:
    """Get Celery app instance"""
    return celery_app

