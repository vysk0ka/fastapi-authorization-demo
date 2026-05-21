"""
Фабрика HTTP Bearer-гардов для верификации JWT.

Создаёт экземпляры FastAPI Security-зависимостей, которые извлекают токен
из заголовка Authorization, верифицируют его через JWTStrategy и возвращают
типизированные JWTAuthorizationCredentials.
"""

from typing import Annotated, Callable

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel

from modules.auth.modules.jwt.services import JWTStrategy
from modules.auth.modules.jwt.models import JWTAuthorizationCredentials


def make_jwt_bearer[TPayload: BaseModel](
    strategy_factory: Callable[..., JWTStrategy], payload_model: type[TPayload]
):
    """
    Создаёт FastAPI-совместимый HTTP Bearer-гард для конкретного типа JWT.

    Параметры типа:
        TPayload: Pydantic-модель ожидаемого payload (JWTAccessPayload / JWTRefreshPayload).

    Args:
        strategy_factory: фабричная функция (FastAPI-зависимость), возвращающая JWTStrategy.
        payload_model: класс модели для десериализации payload.

    Returns:
        Экземпляр JWTBearer — FastAPI Security-зависимость, которая при вызове
        возвращает JWTAuthorizationCredentials[TPayload].
    """

    class JWTBearer(HTTPBearer):
        async def __call__(  # type: ignore[override]
            self,
            request: Request,
            strategy: Annotated[JWTStrategy, Depends(strategy_factory)],
        ) -> JWTAuthorizationCredentials[TPayload] | None:
            """
            Извлекает Bearer-токен из запроса, верифицирует его и возвращает
            JWTAuthorizationCredentials с десериализованным payload.

            Raises:
                HTTPException(401): если токен отсутствует или не прошёл верификацию.
            """
            credentials = await super().__call__(request)

            if credentials is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is required"
                )

            payload = strategy.verify(
                token=credentials.credentials, model=payload_model
            )

            return JWTAuthorizationCredentials(
                **credentials.model_dump(), payload=payload
            )

    return JWTBearer()
