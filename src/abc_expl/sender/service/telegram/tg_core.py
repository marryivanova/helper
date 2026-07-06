import requests

from src.abc_expl.sender.service.settings import settings
from src.abc_expl.sender.service.telegram.model import TgMessageDTO, TgStatus


class TelegramSDK:
    def __init__(self, telegram_token: str):
        self._token = telegram_token
        self._base_url = f"{settings.TELEGRAM_API_URL}{self._token}"

    def send(self, message: TgMessageDTO) -> str:
        url = f"{self._base_url}/sendMessage"

        payload = dict(
            chat_id=message.chat_id,
            text=message.message_text,
            parse_mode=message.parse_mode,
        )

        if message.buttons:
            payload["reply_markup"] = {
                "inline_keyboard": [
                    [{"text": b.button_text, "callback_data": b.data}] for b in message.buttons
                ]
            }

        try:
            response = requests.post(url, json=payload, timeout=10)
            data = response.json()

            if data.get("ok"):
                return TgStatus.SEND.value
            else:
                return data.get("description", "Unknown error")
        except Exception as e:
            return str(e)

    def send_photo(self, chat_id: int, photo_url: str, caption: str = ""):
        url = f"{self._base_url}/sendPhoto"
        payload = {"chat_id": chat_id, "photo": photo_url, "caption": caption}
        return requests.post(url, json=payload)
