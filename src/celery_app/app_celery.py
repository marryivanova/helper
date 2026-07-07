from celery import Celery
from celery.schedules import crontab
from kombu import Exchange, Queue
from loguru import logger

from src.celery_app.settings import settings

# Инициализация приложения
app = Celery(
    main="celery_app",
    broker=settings.redis.celery_broker_url,
    backend=settings.redis.celery_redis_url,
    include=["celery_app.tasks"],
)

# ============ 1. СЕРИАЛИЗАЦИЯ ============
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    result_expires=3600,  # результаты хранятся 1 час
)

# ============ 2. ВРЕМЯ ============
app.conf.update(
    timezone="UTC",
    enable_utc=True,
)

# ============ 3. НАДЕЖНОСТЬ ============
app.conf.update(
    task_acks_late=True,  # подтверждение после выполнения
    task_reject_on_worker_lost=True,  # возвращать задачу при падении воркера
    task_track_started=True,  # отслеживать статус "запущена"
    task_always_eager=False,  # всегда асинхронно
)

# ============ 4. ТАЙМАУТЫ ============
app.conf.update(
    task_time_limit=30 * 60,  # 30 минут - жесткий лимит
    task_soft_time_limit=25 * 60,  # 25 минут - мягкий лимит
)

# ============ 5. ПОДКЛЮЧЕНИЕ К БРОКЕРУ ============
app.conf.update(
    broker_connection_retry=True,
    broker_connection_max_retries=100,
    broker_connection_retry_on_startup=True,
)

# ============ 6. ОЧЕРЕДИ И МАРШРУТИЗАЦИЯ ============
app.conf.update(
    task_queues=(
        Queue("default", Exchange("default"), routing_key="default"),
        Queue("high_priority", Exchange("high_priority"), routing_key="high_priority"),
        Queue("low_priority", Exchange("low_priority"), routing_key="low_priority"),
    ),
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",
    task_routes={
        # Задачи с высоким приоритетом
        "send_message_task": {"queue": "high_priority"},
        "send_emergency_notification": {"queue": "high_priority"},
        "process_payment": {"queue": "high_priority"},
        # Обычные задачи
        "schedule_message_task": {"queue": "default"},
        "process_upload": {"queue": "default"},
        "generate_report": {"queue": "default"},
        # Задачи с низким приоритетом
        "heavy_computation_task": {"queue": "low_priority"},
        "cleanup_old_data": {"queue": "low_priority"},
        "batch_export": {"queue": "low_priority"},
    },
)

# ============ 7. МОНИТОРИНГ (FLOWER) ============
app.conf.update(
    task_send_sent_event=True,
    task_send_received_event=True,
    task_send_started_event=True,
    task_send_success_event=True,
    task_send_failure_event=True,
    task_send_retry_event=True,
    task_send_revoked_event=True,
    flower_port=settings.flower.port,
    flower_basic_auth=settings.flower.auth,
)

# ============ 8. БЕЗОПАСНОСТЬ (для Redis) ============
app.conf.update(
    redis_socket_connect_timeout=5,
    redis_socket_timeout=5,
    redis_retry_on_timeout=True,
    redis_max_connections=50,
)

# ============ 9. ПЛАНИРОВЩИК (BEAT) ============
app.conf.beat_schedule = {
    "cleanup-temp-files": {
        "task": "src.tasks.cleanup.delete_temp_files",
        "schedule": crontab(hour=3, minute=0),  # каждую ночь в 3:00
        "args": (),
        "options": {"queue": "low_priority"},
    },
    "send-daily-report": {
        "task": "src.tasks.reports.send_daily_report",
        "schedule": crontab(hour=9, minute=0),  # каждый день в 9:00
        "args": (),
        "options": {"queue": "default"},
    },
    "health-check": {
        "task": "src.tasks.monitoring.health_check",
        "schedule": 60.0,  # каждые 60 секунд
        "args": (),
        "options": {"queue": "high_priority"},
    },
    "clear-old-results": {
        "task": "celery.backend_cleanup",
        "schedule": crontab(hour=4, minute=30),
        "args": (),
    },
}

# ============ 10. АВТООБНАРУЖЕНИЕ ЗАДАЧ ============
app.autodiscover_tasks(
    [
        "src.tasks.email",
        "src.tasks.images",
    ]
)

# ============ 11. ЛОГГИРОВАНИЕ ============
logger.info(f"Celery app configured with broker: {settings.redis.celery_broker_url}")
logger.info(f"Queues configured: {[q.name for q in app.conf.task_queues]}")
logger.info(f"Beat schedule configured with {len(app.conf.beat_schedule)} tasks")
