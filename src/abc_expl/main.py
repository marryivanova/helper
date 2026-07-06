from time import sleep

from loguru import logger

from src.abc_expl.sender.interface_sender import (
    TelegramMessageSender,
    TwilioMessageSender,
    WazzupMessageSender,
)
from src.abc_expl.sender.service.modal import MessageModel


class ValidationError(Exception):
    pass


class Sender:
    def __init__(self, message: MessageModel) -> None:
        self._message = message
        self._twilio_sid = None

    def call_sender(self) -> str:
        try:
            self._validate_message()
            status = self._process_sending()
            logger.info(f"📤 Результат: {status}")
            return status
        except ValidationError as e:
            return str(e)
        except Exception as e:
            logger.exception("Непредвиденная ошибка")
            return self._format_error(f"Системная ошибка: {e}")

    def _validate_message(self) -> None:
        if not self._message.client_name:
            raise ValidationError(self._format_error("У клиента не указано имя"))

    @staticmethod
    def _is_success(status: str) -> bool:
        return status and "Not sent" not in status and "Не доставлено" not in status

    @staticmethod
    def _format_error(message: str) -> str:
        return f"Не доставлено - {message}"

    def _process_sending(self) -> str:
        if self._message.phone:
            if not self._message.send_whatsapp:
                return self._format_error("Отключена рассылка в WhatsApp")
            sleep(3)
            self._twilio_sid, status = TwilioMessageSender().send(self._message)
            return status if self._twilio_sid else self._format_error(status)

        return self._route_to_messenger()

    def _route_to_messenger(self) -> str:
        # 1. Попытка Telegram
        if self._should_use_telegram():
            status = TelegramMessageSender().send(self._message)[1]
            if self._is_success(status):
                return status
            logger.warning(f"Telegram failed: {status}. Trying alternatives.")

        # 2. Wazzup
        if self._message.messenger == "wz":
            return WazzupMessageSender().send(self._message)[1]

        # 3. Twilio/WhatsApp
        if self._message.send_whatsapp and self._message.client_phone_number:
            self._twilio_sid, status = TwilioMessageSender().send(self._message)
            return status if self._twilio_sid else self._format_error(status)

        # 4. Email
        if self._message.messenger == "123":
            self._message.message_text = f"Вам на почту {self._message.emails} отправлено письмо."
            return TwilioMessageSender().send(self._message)[1]

        return self._format_error("Нет доступных каналов для отправки")

    def _should_use_telegram(self) -> bool:
        return (
            self._message.messenger in ["telegram", None]
            and self._message.telegram_id
            and self._message.send_telegram
        )


if __name__ == "__main__":
    msg = MessageModel(
        sender="Admin",
        text="Привет! Это тестовое сообщение.",
        client_name="Test",
        messenger="telegram",
        telegram_id=12345678,
        send_telegram=True,
    )
    print(Sender(msg).call_sender())
