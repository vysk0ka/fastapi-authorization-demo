"""Схема тела запроса для эндпоинта POST /auth/register."""

import re

from pydantic import BaseModel, EmailStr, Field, field_validator


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
    password: str = Field(exclude=True, min_length=8, max_length=32)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        if re.search(r"\s", v):
            raise ValueError("Password must not contain any space symbols")
        return v
