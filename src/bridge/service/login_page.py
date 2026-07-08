from fastapi.responses import RedirectResponse
from loguru import logger
from src.bridge.service.vpn_service import VPNService
from fastapi import Request, Response, status
from src.bridge.routers.settings import service_login_page_settings


class AuthChecker:
    def __init__(
        self,
        login_page_url: str,
        auth_cookie_name: str = service_login_page_settings.ACCESS_TOKEN,
    ):
        self.login_page_url = login_page_url
        self.auth_cookie_name = auth_cookie_name

    async def check_connection(self, request: Request) -> bool:
        try:
            await VPNService.check_connection(request.url.hostname)

            if self.auth_cookie_name not in request.cookies:
                logger.warning(f"Auth cookie '{self.auth_cookie_name}' not found")
                return False

            return True

        except Exception as e:
            logger.error(f"Connection check failed: {str(e)}")
            return False

    def redirect_to_login(self) -> RedirectResponse:
        return RedirectResponse(
            url=self.login_page_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT
        )

    def set_auth_cookie(self, response: Response, token: str) -> None:
        response.set_cookie(
            key=self.auth_cookie_name,
            value=token,
            httponly=True,
            secure=True,
            samesite="strict",
        )
