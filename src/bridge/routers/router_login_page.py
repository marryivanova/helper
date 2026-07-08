import urllib

import httpx
import typing as t
from loguru import logger
from fastapi.responses import RedirectResponse
from fastapi import Request, HTTPException, Depends, APIRouter

from src.bridge.service.login_page import AuthChecker
from src.bridge.service.vpn_service import VPNService
from src.bridge.routers.settings import service_login_page_settings
from src.bridge.models.schemas import (
    ErrorResponse,
    TokenResponseCheckLoginPage,
    BaseResponse,
)

router = APIRouter(tags=["Login Page"])

VPN_CHECK_TIMEOUT = 2.0
TOKEN_VALIDATION_TIMEOUT = 3.0

COOKIE_COMMON_ARGS = dict(
    httponly=True,
    secure=not service_login_page_settings.DEBUG,
    samesite="lax",
    path="/",
)


def _set_original_url_cookie(response: RedirectResponse, original_url: str) -> None:
    """Set the original URL as a cookie in the response."""
    response.set_cookie(
        key="original_url",
        value=original_url,
        max_age=300,
        **COOKIE_COMMON_ARGS,
    )


class VPNRouter:
    """Handles VPN-related endpoints for connection verification."""

    @staticmethod
    @router.get(
        "/vpn-connect-check",
        response_model=BaseResponse,
        summary="Verify VPN connection status",
        description="Determines if the request originates from the internal network.",
    )
    async def check_connection(request: Request) -> BaseResponse:
        """Endpoint to verify VPN/internal network connection."""
        return await VPNService.check_connection(request)

    @staticmethod
    @router.get(
        "/vpn-connect-check/unconnected",
        summary="VPN status",
        description="Displays VPN connection status.",
        responses={
            403: {"description": "Not connected to internal network"},
            200: {"description": "Successfully connected"},
        },
    )
    async def frontend_check(request: Request, responses=403):
        """
        Renders appropriate UI based on VPN connection status.
        Returns 403 error page if not connected to internal network.
        """
        vpn_check = await VPNService.check_connection(request)

        if not vpn_check.success:
            raise HTTPException(status_code=403, detail="Access denied")

        return dict(status_code=200, connect="Successfully connected")


class LoginPageRouter:
    """Handles authentication and VPN status verification endpoints."""

    @staticmethod
    async def _check_vpn_connection(request: Request) -> t.Optional[bool]:
        """
        Internal method to verify VPN connection with timeout handling.
        Returns:
            bool: True if connected to internal network
            None: If check timed out
            False: If connection failed or error occurred
        """
        try:
            async with httpx.AsyncClient(timeout=VPN_CHECK_TIMEOUT) as client:
                response = await VPNService.check_connection(request)
                return response.success
        except httpx.TimeoutException:
            logger.warning("VPN check timeout")
            return None
        except Exception as e:
            logger.warning(f"VPN connection check failed: {str(e)}")
            return False

    @staticmethod
    async def _validate_token(token: str, validate_url: str) -> t.Optional[bool]:
        """
        Validates JWT token with external authentication service.
        Returns:
            bool: Token validity status
            None: If validation timed out
            False: If validation failed
        """
        try:
            async with httpx.AsyncClient(timeout=TOKEN_VALIDATION_TIMEOUT) as client:
                response = await client.get(
                    validate_url, headers={"Authorization": f"Bearer {token}"}
                )
                response.raise_for_status()
                data = response.json()
                return data.get("token_is_valid", False)
        except httpx.TimeoutException:
            logger.warning("Token validation timeout")
            return None
        except Exception as e:
            logger.warning(f"Token validation failed: {str(e)}")
            return False

    @staticmethod
    @router.get(
        "/check-status-vpn-connect",
        response_model=TokenResponseCheckLoginPage,
        summary="Verify authentication and VPN status",
        description="Comprehensive check of user authentication and network status.",
        responses={
            302: {"description": "Redirect to login when not authenticated"},
            401: {"model": ErrorResponse, "description": "Unauthorized access"},
            500: {"model": ErrorResponse, "description": "Internal server error"},
        },
    )
    async def check_status(
        request: Request,
        auth_checker: AuthChecker = Depends(
            lambda: AuthChecker(
                login_page_url=service_login_page_settings.URL_LOGIN_PAGE,
                auth_cookie_name=service_login_page_settings.SABER_ACCESS_TOKEN,
            )
        ),
    ):
        """
        Performs comprehensive status check:
        1. Verifies authentication token presence
        2. Validates token with auth service
        3. Checks VPN/internal network connection
        """
        try:
            token_present = auth_checker.auth_cookie_name in request.cookies
            if not token_present:
                return RedirectResponse(
                    url=auth_checker.login_page_url, status_code=302
                )

            token = request.cookies.get(auth_checker.auth_cookie_name)
            token_valid = await LoginPageRouter._validate_token(
                token, service_login_page_settings.URL_VALIDATE_TOKEN
            )

            if token_valid is False:
                return RedirectResponse(
                    url=auth_checker.login_page_url, status_code=302
                )

            vpn_connected = await LoginPageRouter._check_vpn_connection(request)

            if vpn_connected is False:
                logger.info("External network detected, redirecting to VPN check")
                return RedirectResponse(url="/vpn-connect-check/frontend")

            authenticated = token_valid is True
            status_ok = authenticated and (vpn_connected is True)

            return TokenResponseCheckLoginPage(
                status=status_ok,
                message="Status check completed",
                authenticated=authenticated,
                token_present=token_present,
                token_valid=token_valid,
                vpn_connected=vpn_connected,
            )

        except Exception as e:
            logger.error(f"Status check failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500, detail="Internal server error during status check"
            )


class MainRouter:
    """Handles core application routes and access control."""

    @staticmethod
    def _set_auth_cookies(
        response: RedirectResponse, tokens: dict, set_refresh: bool = True
    ) -> None:
        """
        Configures secure authentication cookies in the response.
        Args:
            response: RedirectResponse object to set cookies on
            tokens: Dictionary containing access and refresh tokens
            set_refresh: Whether to set the refresh token cookie
        """
        response.set_cookie(
            key="access_token",
            value=tokens["access_token"],
            max_age=tokens.get("expires_in", 3600),
            **COOKIE_COMMON_ARGS,
        )

        if set_refresh and "refresh_token" in tokens:
            response.set_cookie(
                key="refresh_token", value=tokens["refresh_token"], **COOKIE_COMMON_ARGS
            )

    @staticmethod
    @router.get(
        "/",
        summary="Application entry point",
        response_model=BaseResponse,
        description="Main gateway with authentication and network access checks.",
    )
    async def get_info(request: Request) -> t.Union[BaseResponse, RedirectResponse]:
        """
        Primary endpoint handling:
        1. Authentication verification
        2. Network access validation
        3. Appropriate redirection based on access status
        """
        try:
            access_token = request.cookies.get("access_token") or request.cookies.get(
                service_login_page_settings.SABER_ACCESS_TOKEN
            )

            if not access_token:
                return RedirectResponse(
                    f"{service_login_page_settings.URL_LOGIN_PAGE}/?redirect={urllib.parse.quote(str(request.url))}"
                )

            vpn_check = await VPNService.check_connection(request)

            if not vpn_check or not vpn_check.data:
                logger.error("Invalid VPN check response")
                return RedirectResponse(url="/vpn-connect-check/frontend")

            vpn_data = vpn_check.data
            access_granted = vpn_data.get("access_granted", False)

            if not access_granted:
                logger.info("No VPN/corporate access - showing frontend stub")
                return RedirectResponse(url="/vpn-connect-check/frontend")

            return BaseResponse(
                success=True, message="Access granted", data={"status": "authenticated"}
            )

        except HTTPException as e:
            logger.error(f"HTTP error: {str(e)}", exc_info=True)
            return BaseResponse(
                success=False, message=str(e.detail), error="http_error"
            )
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return BaseResponse(
                success=False, message="Internal server error", error="internal_error"
            )
