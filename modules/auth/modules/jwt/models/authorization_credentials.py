"""Расширенная модель Bearer-реквизитов с верифицированным payload."""

from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel


class JWTAuthorizationCredentials[TPayload: BaseModel](HTTPAuthorizationCredentials):
    """
    Расширяет стандартный HTTPAuthorizationCredentials, добавляя десериализованный
    и верифицированный payload JWT в виде типизированной Pydantic-модели.

    Параметры типа:
        TPayload: модель payload (JWTAccessPayload или JWTRefreshPayload).

    Атрибуты (наследуются):
        scheme: схема авторизации (всегда "Bearer").
        credentials: исходная строка токена.
    Поля:
        payload: верифицированный payload, десериализованный в TPayload.
    """

    payload: TPayload
