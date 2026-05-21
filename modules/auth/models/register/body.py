"""Схема тела запроса для эндпоинта POST /auth/register."""

from pydantic import BaseModel, EmailStr, Field


class AuthRegisterBody(BaseModel):
    """
    Тело запроса на регистрацию нового пользователя.

    Поля:
        username: желаемое имя пользователя (должно быть уникальным).
        email: адрес электронной почты (должен быть уникальным, валидируется Pydantic).
        password: пароль в открытом виде (исключён из сериализации ответа).
    """

    username: str
    email: EmailStr
    password: str = Field(exclude=True)
