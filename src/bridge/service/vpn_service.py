import ipaddress
from fastapi import APIRouter, HTTPException

from loguru import logger
from src.bridge.models.schemas import BaseResponse, PrepareResponseData

router = APIRouter(tags=["Login Page"])


def _is_local_ip(ip: str) -> bool:
    """Check if the IP address is private/local."""
    try:
        ip_obj = ipaddress.IPv4Address(ip)
        return ip_obj.is_private
    except ValueError:
        return False


class VPNService:
    """Handles VPN related operations."""

    @staticmethod
    async def check_connection(request) -> BaseResponse:
        """Check connection and determine access."""
        try:
            ip = request.headers.get("X-Real-IP")
            if not ip:
                logger.warning("No IP address provided in headers")
                return BaseResponse(
                    success=False,
                    message="IP address not provided",
                )

            is_local = _is_local_ip(ip)
            logger.info(f"Connection from IP: {ip}, is_local: {is_local}")

            return BaseResponse(
                success=is_local,
                message=(
                    "Access granted"
                    if is_local
                    else "Access denied: External network requires VPN"
                ),
                data=PrepareResponseData(
                    origin="internal" if is_local else "external",
                    vpn_active=False,
                    client_ip=ip,
                    access_granted=is_local,
                ),
            )

        except Exception as e:
            logger.error(f"Connection check failed: {str(e)}")
            return BaseResponse(
                success=False, message="Connection check error", error=str(e)
            )

    @staticmethod
    async def enforce_vpn_policy(request) -> None:
        """Enforce access policy."""
        response = await VPNService.check_connection(request)
        if not response.success:
            raise HTTPException(
                status_code=403,
                detail="Access denied: External network requires VPN",
            )
