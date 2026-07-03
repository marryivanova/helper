from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import JSONResponse

from src.jwt_auth import settings
from src.jwt_auth.auth.models import AuthUser, CreateUserInternal, RegisterUser, UserReturnData
from src.jwt_auth.auth.service import AuthHandler, UserService

router = APIRouter(tags=["Auth"])


@router.post("/login")
async def login(user_data: AuthUser, service: UserService = Depends()):
    data = await service.login_user(user_data.email, user_data.password)
    response = JSONResponse(content={"message": "Вход успешен"})

    response.set_cookie(
        key="Authorization",
        value=data["token"],
        httponly=True,
        max_age=settings.app.access_token_expire,
        secure=True,
        samesite="lax",
    )
    return response


@router.post("/register", response_model=UserReturnData, status_code=status.HTTP_201_CREATED)
async def registration(
    user_input: RegisterUser, service: UserService = Depends()
) -> UserReturnData:
    hashed_pwd = AuthHandler.get_password_hash(user_input.password)

    user_to_db = CreateUserInternal(email=user_input.email, hashed_password=hashed_pwd)

    return await service.register_user(user_data=user_to_db)
