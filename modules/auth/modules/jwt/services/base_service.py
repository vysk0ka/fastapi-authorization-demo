"""
Базовый сервис низкоуровневых операций с JWT.

Отвечает только за кодирование и декодирование токенов без знания
конкретных секретов или алгоритмов — они передаются явно при каждом вызове.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException, status

from jwt import decode, encode
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError


class JWTBaseService:
    """Низкоуровневый JWT-сервис: подписывает и верифицирует токены."""

    def sign(
        self,
        *,
        payload: dict[str, Any],
        secret: str,
        algorithm: str,
        expires_delta: timedelta,
    ) -> tuple[str, datetime]:
        """
        Подписывает payload и возвращает JWT-строку вместе с временем истечения.

        Добавляет стандартный claim `exp` к переданному payload.

        Args:
            payload: данные для включения в токен.
            secret: секретный ключ подписи.
            algorithm: алгоритм подписи (например, "HS256").
            expires_delta: время жизни токена.

        Returns:
            Кортеж (jwt_string, expire_datetime).
        """
        to_encode = payload.copy()

        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})

        return encode(to_encode, secret, algorithm), expire

    def verify(self, token: str, secret: str, algorithm: str) -> dict[str, Any]:
        """
        Декодирует и верифицирует JWT, возвращая его payload.

        Args:
            token: JWT-строка.
            secret: секретный ключ подписи.
            algorithm: ожидаемый алгоритм подписи.

        Returns:
            Словарь с данными payload.

        Raises:
            HTTPException(401): если токен истёк или имеет неверную подпись/структуру.
        """
        try:
            payload = decode(token, secret, algorithms=[algorithm])

            return payload
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="The token has expired"
            )
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
