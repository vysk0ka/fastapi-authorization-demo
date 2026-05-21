"""
Роутер модуля аутентификации.

Регистрирует эндпоинты под префиксом /auth и передаёт управление в AuthController.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from modules.auth.controller import AuthController
from modules.auth.models.error import ErrorResponse
from modules.auth.models.login import AuthLoginBody, AuthLoginResponse
from modules.auth.models.register import AuthRegisterBody, AuthRegisterResponse
from modules.auth.modules.jwt import JWTRefreshCredentialsDep

router = APIRouter(prefix="/auth", tags=["auth"])

_401 = {status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse}}
_409 = {status.HTTP_409_CONFLICT: {"model": ErrorResponse}}


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=AuthRegisterResponse,
    responses={**_409},
)
async def register(
    body: AuthRegisterBody, controller: Annotated[AuthController, Depends()]
):
    """
    Регистрация нового пользователя.

    Создаёт учётную запись и сразу выдаёт пару токенов (access + refresh).

    - **409 Conflict** — email или username уже заняты.
    """
    return controller.register(body)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=AuthLoginResponse,
    responses={**_401},
)
async def login(body: AuthLoginBody, controller: Annotated[AuthController, Depends()]):
    """
    Вход в систему по имени пользователя и паролю.

    - **401 Unauthorized** — пользователь не найден или пароль неверен.
    """
    return controller.login(body)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    responses={**_401},
)
async def logout(
    credentials: JWTRefreshCredentialsDep,
    controller: Annotated[AuthController, Depends()],
):
    """
    Выход из системы — инвалидация текущего refresh-токена.

    Требует валидный refresh-токен в заголовке `Authorization: Bearer <token>`.

    - **401 Unauthorized** — токен отсутствует, истёк, имеет неверную подпись
      или не прошёл HMAC-проверку.
    """
    return controller.logout(credentials)


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    responses={**_401},
)
async def refresh(
    credentials: JWTRefreshCredentialsDep,
    controller: Annotated[AuthController, Depends()],
):
    """
    Обновление пары токенов по действующему refresh-токену (Refresh Token Rotation).

    Требует валидный refresh-токен в заголовке `Authorization: Bearer <token>`.

    - **401 Unauthorized** — токен не найден, уже использован, истёк или не прошёл
      HMAC-проверку. При обнаружении повторного использования инвалидируется
      вся семья токенов (защита от кражи).
    """
    return controller.refresh(credentials)
