import requests
from loguru import logger

from src.abc_expl.sender.service.modal import MessageModel
from src.abc_expl.sender.service.settings import settings


class WazzupSendMessageService:
    """Service for send message to wazzup."""

    _message: MessageModel
    _url: str
    _headers: dict

    def __init__(self, message: MessageModel) -> None:
        """Init."""
        self._message = message
        self._url = settings.URL_WAZZAP
        self._headers = dict(Authorization=f"Basic {settings.WAZZAP_TOKEN}")

    def work(self) -> str:
        """Send message."""
        params_for_send_message = dict(
            channelId=self._message.wazzup_phone_id,
            chatType="whatsapp",
            chatId=self._message.client_phone_number,
            text=self._message.message_text,
        )
        response = requests.post(
            self._url, headers=self._headers, json=params_for_send_message, timeout=30
        )
        logger.debug(f"\nОтправили сообщение\n" f"{response.text}")

        if response.status_code != 201:
            logger.error(
                f"{self._message.function_call_name} || do not send message to wazzup {response.text} --- Wazzup"
            )
            if self._message.direction == "en":
                return "Not sent"
            return "Не доставлено"

        logger.success(f"Send message successfully")
        if self._message.direction == "en":
            return f"Sent via Wazzup to {self._message.client_phone_number}"
        return f"Отправлено через Wazzup на номер {self._message.client_phone_number}"
