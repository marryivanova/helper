from src.abc_expl.sender.service.modal import MessageModel
from src.abc_expl.sender.service.settings import settings
from src.abc_expl.sender.service.telegram.model import (
    TgButtonDTO,
    TgButtonType,
    TgMediaPhotoDTO,
    TgParseMode,
)
from src.abc_expl.sender.service.telegram.tg_core import TelegramSDK, TgMessageDTO, TgStatus


class TelegramSendMessageService:
    """Send message via Telegram."""

    _model_message: MessageModel
    _token: str
    _url: str

    def __init__(self, message: MessageModel):
        self._message = message
        self.telegram = TelegramSDK(telegram_token=settings.TELEGRAM_API_TOKEN)

    def send_message(self, message: MessageModel):
        try:
            self._create_telegram_message()
        except ValueError as error:
            status = error
        else:
            status = self.telegram.send(message=self.telegram_message)

        if status != TgStatus.SEND.value:
            if self._message.direction == "en":
                return f"Not sent from Telegram - {status}"
            return f"Не доставлено через Telegram - {status}"

        if self._message.direction == "en":
            return "Send from Telegram"
        return "Отправлено через Telegram"

    def _create_telegram_message(self) -> None:
        self.telegram_message = TgMessageDTO(
            chat_id=self._message.telegram_id,
            message_text=self._message.text,
            buttons=self._get_buttons(),
            parse_mode=TgParseMode.HTML.value,
        )

        if self._message.telegram_media:
            telegram_media = []
            for media in self._message.telegram_media:
                telegram_media.append(
                    TgMediaPhotoDTO(
                        media=media.get("media"),
                        caption=media.get("caption", ""),
                    )
                )
            self.telegram_message.media = telegram_media

        if self._message.telegram_photo:
            self.telegram_message.photo = self._message.telegram_photo

    def _get_buttons(self) -> list:
        telegram_buttons = []
        for button in self._message.telegram_buttons:
            if isinstance(button, list):
                button = button[0]
            tg_button = TgButtonDTO(
                button_text=button.get("text"),
                button_type=button.get("button_type", TgButtonType.CALLBACK.value),
                data=button.get("callback_data"),
            )
            telegram_buttons.append(tg_button)
        return telegram_buttons
