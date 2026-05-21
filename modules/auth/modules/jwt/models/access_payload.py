"""Модель payload для access JWT."""

import uuid

from pydantic import BaseModel


class JWTAccessPayload(BaseModel):
    """
    Полезная нагрузка access-токена.

    Поля:
        sub: идентификатор пользователя (UUID), стандартный claim RFC 7519.
    """

    sub: uuid.UUID
