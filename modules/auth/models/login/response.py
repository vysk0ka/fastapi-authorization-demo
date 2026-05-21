"""Схема ответа эндпоинта POST /auth/login."""

from pydantic import BaseModel


class AuthLoginResponse(BaseModel):
    """
    Ответ на успешный вход в систему.

    Поля:
        access_token: короткоживущий JWT для авторизации запросов.
        refresh_token: долгоживущий JWT для обновления access-токена.
    """

    access_token: str
    refresh_token: str
