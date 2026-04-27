"""
Celery 應用配置
"""
from celery import Celery
from app.core.config import settings

# 創建 Celery 應用
celery_app = Celery(
    "ai_leadgen",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.scraper_tasks",
        "app.tasks.email_tasks",
        "app.tasks.campaign_tasks",
        "app.tasks.optimizer_tasks",
    ]
)

# Celery 配置
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # 定時任務
    beat_schedule={
        "run-optimizer-daily": {
            "task": "app.tasks.optimizer_tasks.run_daily_optimization",
            "schedule": 86400.0,  # 每天
        },
        "check-campaigns-hourly": {
            "task": "app.tasks.campaign_tasks.check_and_process_campaigns",
            "schedule": 3600.0,  # 每小時
        },
        "warmup-emails-daily": {
            "task": "app.tasks.email_tasks.warmup_email_accounts",
            "schedule": 86400.0,  # 每天
        },
    },
    
    # 任務配置
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_time_limit=3600,  # 1 小時
    task_soft_time_limit=3000,  # 50 分鐘
    
    # 重試配置
    task_default_retry_delay=60,
    task_max_retries=3,
)
