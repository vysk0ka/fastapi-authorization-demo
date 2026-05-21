"""
Конфигурация и стратегия подписи/верификации JWT.

JWTConfig хранит параметры одного типа токенов (access или refresh).
JWTStrategy связывает конфигурацию с JWTBaseService и предоставляет
удобный интерфейс без необходимости передавать секрет/алгоритм при каждом вызове.
"""

from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from pydantic import BaseModel

from .base_service import JWTBaseService


@dataclass(frozen=True)
class JWTConfig:
    """
    Неизменяемая конфигурация для конкретного типа JWT-токенов.

    Поля:
        secret: секретный ключ подписи.
        algorithm: алгоритм подписи (например, "HS256").
        expires_delta: время жизни токена.
    """

    secret: str
    algorithm: str
    expires_delta: timedelta


class JWTStrategy:
    """
    Стратегия работы с JWT-токенами определённого типа.

    Инкапсулирует JWTConfig и делегирует операции JWTBaseService,
    скрывая детали конфигурации от вызывающего кода.
    """

    def __init__(self, config: JWTConfig, jwt_service: JWTBaseService):
        self.config = config
        self.jwt_service = jwt_service

    def sign(self, *, payload: dict[str, Any]):
        """
        Подписывает payload, используя сохранённую конфигурацию.

        Args:
            payload: данные для включения в токен.

        Returns:
            Кортеж (jwt_string, expire_datetime).
        """
        return self.jwt_service.sign(
            payload=payload,
            secret=self.config.secret,
            algorithm=self.config.algorithm,
            expires_delta=self.config.expires_delta,
        )

    def verify[TPayload: BaseModel](
        self, *, token: str, model: type[TPayload]
    ) -> TPayload:
        """
        Верифицирует токен и десериализует payload в указанную Pydantic-модель.

        Args:
            token: JWT-строка.
            model: класс Pydantic-модели для валидации payload.

        Returns:
            Экземпляр model с данными из токена.

        Raises:
            HTTPException(401): если токен недействителен или истёк.
        """
        payload = self.jwt_service.verify(
            token, self.config.secret, self.config.algorithm
        )
        return model.model_validate(payload)
