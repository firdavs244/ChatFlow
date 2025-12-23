"""
ChatFlow - Celery Configuration
"""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "chatflow",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.services.tasks.notification_tasks",
        "app.services.tasks.file_tasks",
        "app.services.tasks.cleanup_tasks",
    ],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    worker_prefetch_multiplier=1,
    worker_concurrency=4,
)

# Scheduled tasks (Celery Beat)
celery_app.conf.beat_schedule = {
    "cleanup-expired-tokens": {
        "task": "app.services.tasks.cleanup_tasks.cleanup_expired_tokens",
        "schedule": 3600.0,  # Every hour
    },
    "cleanup-old-messages": {
        "task": "app.services.tasks.cleanup_tasks.cleanup_old_messages",
        "schedule": 86400.0,  # Every day
    },
    "update-user-stats": {
        "task": "app.services.tasks.cleanup_tasks.update_user_stats",
        "schedule": 300.0,  # Every 5 minutes
    },
}

