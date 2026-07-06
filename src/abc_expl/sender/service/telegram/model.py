from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TgButtonType(Enum):
    CALLBACK = "callback"
    URL = "url"


class TgStatus(str, Enum):
    SEND = "send"
    DELIVERED = "delivered"
    FAILED = "failed"


class TgParseMode(str, Enum):
    HTML = "html"


class TgButtonDTO(BaseModel):
    button_text: str
    button_type: str = TgButtonType.CALLBACK.value
    callback_data: Optional[str] = None
    url: Optional[str] = None


class TgMediaPhotoDTO(BaseModel):
    media: Dict[str, str]
    caption: str = ""


class TgMessageDTO(BaseModel):
    chat_id: int
    message_text: str
    buttons: List[TgButtonDTO] = Field(default_factory=list)
    parse_mode: str = TgParseMode.HTML.value
    media: Optional[List[TgMediaPhotoDTO]] = None
    photo: Optional[Any] = None
