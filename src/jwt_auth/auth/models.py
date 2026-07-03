import datetime
import uuid
from typing import Annotated, NamedTuple

from pydantic import BaseModel, ConfigDict, EmailStr, StringConstraints


class UserRegistration(BaseModel):
    username: str
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=8, max_length=128)]


class RegisterUser(BaseModel):
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=8, max_length=128)]


class AuthUser(BaseModel):
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=8, max_length=128)]


class CreateUserInternal(BaseModel):
    email: EmailStr
    hashed_password: str


class UserReturnData(BaseModel):
    id: uuid.UUID
    email: EmailStr
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class CreateTokenTuple(NamedTuple):
    encoded_jwt: str
    session_id: str


class GetUserByID(BaseModel):
    id: uuid.UUID


class GetUserByEmail(BaseModel):
    email: EmailStr
