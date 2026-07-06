from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # API токен Telegram
    TELEGRAM_API_TOKEN: SecretStr

    # Twilio ключи
    TWILIO_ACCOUNT_SID: SecretStr
    TWILIO_AUTH_TOKEN: SecretStr

    # Wazzup
    WAZZAP_TOKEN: SecretStr
    URL_WAZZAP: str = "https://api.wazzup24.com/v2/send_message"

    # API Endpoints
    TELEGRAM_API_URL: str = "https://api.telegram.org/bot"
    TWILIO_API_URL: str = "https://content.twilio.com/v1/Content/"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
