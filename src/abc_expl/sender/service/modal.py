from typing import Any, List, Optional, Union

from pydantic import BaseModel, Field


class MessageModel(BaseModel):
    sender: str
    text: str
    messenger: str

    client_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

    send_whatsapp: Union[str, bool] = False
    send_telegram: Union[str, bool] = False
    send_twilio: Union[str, bool] = False

    twilio_sid_message: Optional[str] = None
    twilio_variables: List[Any] = Field(default_factory=list)

    telegram_id: Optional[int] = None
    telegram_media: Optional[List[dict]] = None
    telegram_buttons: Optional[List[Any]] = []
    telegram_photo: Optional[str] = None


class StatusSender(BaseModel):

    sender: str
    status: str
