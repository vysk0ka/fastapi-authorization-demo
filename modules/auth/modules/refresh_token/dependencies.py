"""
Фабричные функции и тип-аннотации зависимостей для модуля refresh-токенов.
"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from modules.database import get_session
from settings import Settings, get_settings

from .repositories import RefreshTokenRepository
from .services import HMACService


@lru_cache
def _build_refresh_token_hmac_service(secret: str):
    """Создаёт и кеширует HMACService с заданным секретом."""
    return HMACService(secret)


def get_refresh_token_hmac_service(
    settings: Annotated[Settings, Depends(get_settings)],
):
    """FastAPI-зависимость: возвращает кешированный HMACService."""
    return _build_refresh_token_hmac_service(settings.refresh_token_hmac_secret)


def get_refresh_token_repository(session: Annotated[Session, Depends(get_session)]):
    """FastAPI-зависимость: возвращает RefreshTokenRepository для текущей сессии."""
    return RefreshTokenRepository(session)


RefreshTokensRepositoryDep = Annotated[
    RefreshTokenRepository, Depends(get_refresh_token_repository)
]
"""Инъекция RefreshTokenRepository через систему зависимостей FastAPI."""

RefreshTokenHMACServiceDep = Annotated[
    HMACService, Depends(get_refresh_token_hmac_service)
]
"""Инъекция HMACService для вычисления и верификации хешей refresh-токенов."""
