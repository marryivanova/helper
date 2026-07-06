from abc import ABC, abstractmethod
from typing import Optional

from loguru import logger

from src.abc_expl.sender.service.modal import MessageModel
from src.abc_expl.sender.service.telegram.service_sender import TelegramSendMessageService
from src.abc_expl.sender.service.twilo import TwilioSendMessageSIDService
from src.abc_expl.sender.service.wazzap import WazzupSendMessageService


class MessageSender(ABC):
    """Abstract base class for message senders."""

    @abstractmethod
    def send(self, message: MessageModel) -> tuple[Optional[str], str]:
        pass


class SenderStatus(ABC):
    """Abstract base class for message senders."""

    @abstractmethod
    def get_status(self, status_deliver) -> tuple[Optional[str], str]:
        pass


class TwilioMessageSender(MessageSender):
    """Twilio message sender implementation."""

    def send(self, message: MessageModel) -> tuple:
        """Send message via Twilio."""
        logger.debug(f"📤 Отправка через Twilio")
        return TwilioSendMessageSIDService(message=message).work()


class TelegramMessageSender(MessageSender):
    """Telegram message sender implementation."""

    def send(self, message: MessageModel) -> tuple[Optional[str], str]:
        """Send message via Telegram."""
        logger.debug(f"📤 Отправка через Telegram")
        return None, TelegramSendMessageService(message=message).send_message(message=message)


class WazzupMessageSender(MessageSender):
    """Wazzup message sender implementation."""

    def send(self, message: MessageModel) -> tuple[Optional[str], str]:
        """Send message via Wazzup."""
        logger.debug(f"📤 Отправка через Wazzup: {message.function_call_name}")
        return None, WazzupSendMessageService(message=message).work()
