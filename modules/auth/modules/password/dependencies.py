"""
Фабричные функции и тип-аннотации зависимостей для сервиса хеширования паролей.
"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from passlib.context import CryptContext

from .services import HashService


@lru_cache
def _build_password_hash_service():
    """Создаёт и кеширует HashService с алгоритмом Argon2."""
    context = CryptContext(schemes=["argon2"], deprecated="auto")

    return HashService(context)


def get_password_hash_service():
    """FastAPI-зависимость: возвращает кешированный HashService."""
    return _build_password_hash_service()


PasswordHashServiceDep = Annotated[HashService, Depends(get_password_hash_service)]
"""Инъекция HashService (Argon2) для хеширования и верификации паролей."""
