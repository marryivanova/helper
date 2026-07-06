from json import dumps
from typing import Optional, Tuple

from loguru import logger
from requests import RequestException, get
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from src.abc_expl.sender.service.modal import MessageModel
from src.abc_expl.sender.service.settings import settings


class TwilioSendMessageSIDService:
    def __init__(self, message: MessageModel):
        self._message = message
        self._twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    def work(self) -> Tuple[Optional[str], str]:
        """Основной метод отправки."""
        validation_error = self._validate_template()
        if validation_error:
            return None, validation_error

        return self._send_message()

    def _validate_template(self) -> Optional[str]:
        """Проверка шаблона через Twilio API."""
        url = f"{settings.TWILIO_API_URL}{self._message.twilio_sid_message}"
        auth = (settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        try:
            response = get(url, auth=auth, timeout=15)
            response.raise_for_status()
            template_data = response.json()
        except RequestException as e:
            logger.error(f"Ошибка при валидации шаблона Twilio: {e}")
            return "Ошибка сети при проверке шаблона"

        required_vars = template_data.get("variables", {}) or {}
        provided_vars = self._message.content_variables or {}

        if len(required_vars) != len(provided_vars):
            return f"Неверное количество переменных. Требуется: {len(required_vars)}"

        return None

    def _send_message(self) -> Tuple[Optional[str], str]:
        logger.info(f"Запуск отправки Twilio SID: {self._message.twilio_sid_message}")

        phone = self._message.client_phone_number.lstrip("+")
        to_number = f"whatsapp:+{phone}"

        try:
            response = self._twilio_client.messages.create(
                to=to_number,
                content_variables=dumps(self._message.content_variables),
                content_sid=self._message.twilio_sid_message,
                from_=self._message.twilio_messaging_service_sid,
            )

            logger.info(f"📱 Twilio статус отправки: {response.status}, SID: {response.sid}")
            return response.sid, "OK"

        except TwilioRestException as error:
            logger.warning(f"Ошибка Twilio: {error.msg}")
            return None, "Ошибка на стороне Twilio. Попробуйте позже."
        except Exception as e:
            logger.exception("Непредвиденная ошибка при отправке в Twilio")
            return None, "Внутренняя ошибка сервиса"
