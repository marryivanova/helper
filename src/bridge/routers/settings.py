from pydantic_settings import BaseSettings


class BaseServiceSettings(BaseSettings):
    HOST: str
    PORT: str
    DEBUG: bool

    class Config:
        extra = "ignore"
        env_file = ".env"
        env_file_encoding = "utf-8"


class ServiceLoginPageSettings(BaseServiceSettings):
    URL_LOGIN_PAGE: str
    ACCESS_TOKEN: str
    VPN_CHECK_URL: str
    URL_VALIDATE_TOKEN: str


service_login_page_settings = ServiceLoginPageSettings()
