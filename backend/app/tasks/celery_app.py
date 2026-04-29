"""
Celery 應用配置
"""
from celery import Celery
from app.core.config import settings

# 創建 Celery 應用
# 如果設置了 UPSTASH，則使用 Upstash Redis
if settings.UPSTASH_REDIS_REST_URL and settings.UPSTASH_REDIS_REST_TOKEN:
    # 使用 Upstash Redis (需要配置 broker 和 backend)
    # Upstash 提供標准 Redis 兼容接口
    broker_url = f"redis://:{settings.UPSTASH_REDIS_REST_TOKEN}@{settings.UPSTASH_REDIS_REST_URL.replace('https://', '')}"
    result_backend = broker_url
else:
    broker_url = settings.CELERY_BROKER_URL
    result_backend = settings.CELERY_RESULT_BACKEND

celery_app = Celery(
    "ai_leadgen",
    broker=broker_url,
    backend=result_backend,
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
