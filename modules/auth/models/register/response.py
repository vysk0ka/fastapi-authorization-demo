"""Схема ответа эндпоинта POST /auth/register."""

from pydantic import BaseModel


class AuthRegisterResponse(BaseModel):
    """
    Ответ на успешную регистрацию пользователя.

    Поля:
        access_token: короткоживущий JWT для авторизации запросов.
        refresh_token: долгоживущий JWT для обновления access-токена.
    """

    access_token: str
    refresh_token: str
