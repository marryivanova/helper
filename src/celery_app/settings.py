from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):

    celery_broker_url: str = "redis://localhost:6379/0"
    celery_redis_url: str = "redis://localhost:6379/1"

    @property
    def url(self) -> str:
        return f"redis://{self.host}:{self.port}"


class FlowerSettings(BaseSettings):

    port: int = 5555
    auth: str = "admin:password"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="_",
    )

    redis: RedisSettings = RedisSettings()
    flower: FlowerSettings = FlowerSettings()


settings = Settings()
