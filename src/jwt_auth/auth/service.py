import uuid
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import insert, select

from src.jwt_auth import settings
from src.jwt_auth.auth.models import CreateUserInternal, UserReturnData
from src.jwt_auth.database.core import DatabaseManager
from src.jwt_auth.database.core_redis import RedisConnector

from src.jwt_auth.database.model import User


class AuthHandler:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        return cls.pwd_context.hash(password)

    @classmethod
    def verify_password(cls, raw_password: str, hashed_password: str) -> bool:
        return cls.pwd_context.verify(raw_password, hashed_password)

    @classmethod
    def create_access_token(cls, user_id: uuid.UUID):
        token = jwt.encode(
            {"sub": str(user_id)},
            settings.secret_key.get_secret_value(),
            algorithm="HS256",
        )
        return token, str(uuid.uuid4())


class UserManager:
    def __init__(self, db: DatabaseManager = Depends(DatabaseManager)):
        self.db = db
        self.redis = RedisConnector

    async def get_user_by_email(self, email: str) -> Optional[User]:
        async with self.db.get_session() as session:
            result = await session.execute(select(User).where(User.email == email))
            return result.scalar_one_or_none()

    async def create_user(self, user_data: CreateUserInternal) -> User:
        async with self.db.get_session() as session:
            stmt = insert(User).values(**user_data.model_dump()).returning(User)
            result = await session.execute(stmt)
            user = result.scalar_one()
            await session.commit()
            return user

    async def store_access_token(self, token: str, user_id: uuid.UUID, session_id: str) -> None:
        async with self.redis.get_client() as client:
            await client.set(f"auth:{user_id}:{session_id}", token)


class UserService:
    def __init__(
        self,
        manager: UserManager = Depends(UserManager),
        handler: AuthHandler = Depends(AuthHandler),
    ):
        self.manager = manager
        self.handler = handler

    async def login_user(self, email: str, password: str) -> dict:
        exist_user = await self.manager.get_user_by_email(email=email)

        if not exist_user or not self.handler.verify_password(password, exist_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Wrong email or password",
            )

        token, session_id = self.handler.create_access_token(user_id=exist_user.id)
        await self.manager.store_access_token(
            token=token, user_id=exist_user.id, session_id=session_id
        )

        return {"token": token, "session_id": session_id}

    async def register_user(self, user_data: CreateUserInternal) -> UserReturnData:
        db_user = await self.manager.create_user(user_data)
        return UserReturnData.model_validate(db_user)
