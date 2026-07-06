import pytest
from src.abc_expl.sender.service.modal import MessageModel


@pytest.fixture
def base_message():
    """Базовое сообщение для тестов"""
    return MessageModel(
        sender="Admin",
        text="Привет! Это тестовое сообщение.",
        client_name="Test",
        messenger="telegram",
        telegram_id=12345678,
        send_telegram=True,
    )