"""
Фабричные функции и тип-аннотации зависимостей JWT-модуля.

Экспортирует готовые FastAPI-зависимости для инъекции JWTStrategy
и верифицированных Bearer-реквизитов в обработчики эндпоинтов и контроллеры.
"""

from datetime import timedelta
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Security

from settings import Settings, get_settings

from .guards import make_jwt_bearer
from .models import JWTAccessPayload, JWTAuthorizationCredentials, JWTRefreshPayload
from .services import JWTBaseService, JWTConfig, JWTStrategy


@lru_cache
def build_service():
    """Создаёт и кеширует единственный экземпляр JWTBaseService."""
    return JWTBaseService()


def get_service():
    """FastAPI-зависимость, возвращающая кешированный JWTBaseService."""
    return build_service()


@lru_cache
def build_strategy(
    *, secret: str, algorithm: str, expire_minutes: int, jwt_service: JWTBaseService
):
    """
    Создаёт и кеширует JWTStrategy для заданного набора параметров.

    Кеш работает по совокупности всех аргументов, поэтому access- и refresh-стратегии
    хранятся как отдельные экземпляры.
    """
    config = JWTConfig(
        secret=secret,
        algorithm=algorithm,
        expires_delta=timedelta(minutes=expire_minutes),
    )

    return JWTStrategy(config, jwt_service)


def get_access_strategy(
    settings: Annotated[Settings, Depends(get_settings)],
    jwt_service: Annotated[JWTBaseService, Depends(get_service)],
):
    """FastAPI-зависимость: возвращает JWTStrategy для access-токенов."""
    return build_strategy(
        secret=settings.access_token_secret,
        algorithm=settings.jwt_algorithm,
        expire_minutes=settings.access_token_expire_minutes,
        jwt_service=jwt_service,
    )


def get_refresh_strategy(
    settings: Annotated[Settings, Depends(get_settings)],
    jwt_service: Annotated[JWTBaseService, Depends(get_service)],
):
    """FastAPI-зависимость: возвращает JWTStrategy для refresh-токенов."""
    return build_strategy(
        secret=settings.refresh_token_secret,
        algorithm=settings.jwt_algorithm,
        expire_minutes=settings.refresh_token_expire_minutes,
        jwt_service=jwt_service,
    )


JWTAccessDep = Annotated[JWTStrategy, Depends(get_access_strategy)]
"""Инъекция JWTStrategy для подписи/верификации access-токенов."""

JWTRefreshDep = Annotated[JWTStrategy, Depends(get_refresh_strategy)]
"""Инъекция JWTStrategy для подписи/верификации refresh-токенов."""

JWTAccessCredentialsDep = Annotated[
    JWTAuthorizationCredentials[JWTAccessPayload],
    Security(make_jwt_bearer(get_access_strategy, JWTAccessPayload)),
]
"""
Security-зависимость: извлекает и верифицирует access Bearer-токен из запроса,
возвращает JWTAuthorizationCredentials[JWTAccessPayload].
"""

JWTRefreshCredentialsDep = Annotated[
    JWTAuthorizationCredentials[JWTRefreshPayload],
    Security(make_jwt_bearer(get_refresh_strategy, JWTRefreshPayload)),
]
"""
Security-зависимость: извлекает и верифицирует refresh Bearer-токен из запроса,
возвращает JWTAuthorizationCredentials[JWTRefreshPayload].
"""
