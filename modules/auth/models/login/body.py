"""Схема тела запроса для эндпоинта POST /auth/login."""

from pydantic import BaseModel, Field


class AuthLoginBody(BaseModel):
    """
    Тело запроса на вход в систему.

    Поля:
        username: имя пользователя.
        password: пароль в открытом виде (исключён из сериализации ответа).
    """

    username: str
    password: str = Field(exclude=True)
