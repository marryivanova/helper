from unittest.mock import Mock, patch

import pytest

from src.abc_expl.main import Sender
from src.abc_expl.sender.service.modal import MessageModel


@pytest.mark.parametrize(
    "sender, text, client_name, messenger, telegram_id, send_telegram, expected_result",
    [
        # Тест 1: Отправка в Telegram
        (
            "Admin",
            "Test message to Telegram",
            "TestClient",
            "telegram",
            123456789,
            True,
            {"status": "success", "platform": "telegram", "message": "Test message to Telegram"},
        ),
        # Тест 2: Отправка в другой мессенджер (не Telegram)
        (
            "User",
            "Test message to WhatsApp",
            "Client1",
            "whatsapp",
            987654321,
            False,
            {"status": "success", "platform": "whatsapp", "message": "Test message to WhatsApp"},
        ),
        # Тест 3: Пустой текст сообщения
        (
            "Admin",
            "",
            "TestClient",
            "telegram",
            123456789,
            True,
            {"status": "error", "message": "Message text is empty"},
        ),
        # Тест 4: Отсутствует telegram_id
        (
            "Admin",
            "Test message",
            "TestClient",
            "telegram",
            None,
            True,
            {"status": "error", "message": "telegram_id is required for Telegram"},
        ),
        # Тест 5: Длинное сообщение
        (
            "Admin",
            "A" * 1000,
            "TestClient",
            "telegram",
            123456789,
            True,
            {"status": "success", "platform": "telegram", "message": "A" * 1000},
        ),
        # Тест 6: Специальные символы в сообщении
        (
            "Admin",
            "!@#$%^&*()_+{}:<>?",
            "TestClient",
            "telegram",
            123456789,
            True,
            {"status": "success", "platform": "telegram", "message": "!@#$%^&*()_+{}:<>?"},
        ),
        # Тест 7: Кириллица в сообщении
        (
            "Admin",
            "Привет мир! Это тестовое сообщение с кириллицей.",
            "TestClient",
            "telegram",
            123456789,
            True,
            {
                "status": "success",
                "platform": "telegram",
                "message": "Привет мир! Это тестовое сообщение с кириллицей.",
            },
        ),
        # Тест 8: send_telegram = False, но messenger = telegram
        (
            "Admin",
            "Test message",
            "TestClient",
            "telegram",
            123456789,
            False,
            {"status": "error", "message": "Telegram sending is disabled"},
        ),
        # Тест 9: Неизвестный мессенджер
        (
            "Admin",
            "Test message",
            "TestClient",
            "unknown_messenger",
            123456789,
            True,
            {"status": "error", "message": "Unknown messenger: unknown_messenger"},
        ),
        # Тест 10: Длинное имя клиента
        (
            "Admin",
            "Test message",
            "A" * 200,
            "telegram",
            123456789,
            True,
            {"status": "success", "platform": "telegram", "message": "Test message"},
        ),
    ],
)
def test_sender_parameters(
    sender, text, client_name, messenger, telegram_id, send_telegram, expected_result
):
    """Тестирование Sender с различными параметрами"""
    with patch("src.abc_expl.main.Sender.call_sender") as mock_send:
        mock_send.return_value = expected_result

        msg = MessageModel(
            sender=sender,
            text=text,
            client_name=client_name,
            messenger=messenger,
            telegram_id=telegram_id,
            send_telegram=send_telegram,
        )

        result = Sender(msg).call_sender()

        assert result == expected_result


def test_sender_positive_telegram_send_with_mock():
    """Позитивный тест: успешная отправка сообщения в Telegram (с моком)"""
    msg = MessageModel(
        sender="Admin",
        text="Привет! Это тестовое сообщение.",
        client_name="Test Client",
        messenger="telegram",
        telegram_id=123456789,
        send_telegram=True,
    )

    with patch(
        "src.abc_expl.sender.service.telegram.service_sender.TelegramSendMessageService.send_message"
    ) as mock_send:
        mock_send.return_value = {
            "status": "success",
            "message_id": 12345,
            "chat_id": 123456789,
            "text": "Привет! Это тестовое сообщение.",
        }

        sender = Sender(msg)

        result = sender.call_sender()

        mock_send.assert_called_once()

        assert result is not None
        assert result["status"] == "success"
        assert result["message_id"] == 12345
        assert result["chat_id"] == 123456789
        assert result["text"] == "Привет! Это тестовое сообщение."

        print(f"✅ Тест с моком успешно пройден! Результат: {result}")
