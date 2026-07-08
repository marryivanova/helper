import typing as t
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, IPvAnyAddress, SecretStr


class TokenResponseCheckLoginPage(BaseModel):
    status: bool
    message: str
    authenticated: bool
    token_present: bool
    token_valid: Optional[bool] = None
    vpn_connected: Optional[bool] = None


class ErrorResponse(BaseModel):
    detail: str


class BaseResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class PrepareResponseData(t.TypedDict):
    origin: str
    vpn_active: bool
    client_ip: str
    access_granted: bool


class TokenRequest(BaseModel):
    username: str
    password: SecretStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserInfo(BaseModel):
    preferred_username: str
    email: Optional[str] = None
    full_name: Optional[str] = None


class VPNData(BaseModel):
    origin: t.Literal["internal", "external"]
    vpn_active: bool
    client_ip: IPvAnyAddress
    access_granted: bool


class VPNResponse(BaseModel):
    success: bool
    message: str
    data: VPNData
    error: Optional[str] = Field(None, examples=[None])
