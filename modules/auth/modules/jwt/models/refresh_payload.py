"""Модель payload для refresh JWT."""

import uuid

from pydantic import BaseModel


class JWTRefreshPayload(BaseModel):
    """
    Полезная нагрузка refresh-токена.

    Поля:
        sub: идентификатор пользователя (UUID).
        jti: уникальный идентификатор конкретного токена (JWT ID).
             Используется для поиска записи токена в БД и защиты от повторного использования.
    """

    sub: uuid.UUID
    jti: uuid.UUID
