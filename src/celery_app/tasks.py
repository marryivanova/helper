from loguru import logger

from src.celery_app.app_celery import app


@app.task(
    name="send_message_task",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def send_message_task(self, recipient: str, message: str):

    try:
        logger.info(f"Sending message to {recipient}")
        pass
        return {"status": "sent", "recipient": recipient}
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        raise self.retry(exc=e, countdown=60)


@app.task(name="schedule_message_task")
def schedule_message_task(recipient: str, message: str, delay: int):
    """Отложенная отправка сообщения"""
    logger.info(f"Scheduling message to {recipient} with delay {delay}s")
    pass
    return {"status": "scheduled", "recipient": recipient, "delay": delay}
