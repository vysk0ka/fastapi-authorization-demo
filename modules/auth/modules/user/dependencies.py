"""
Фабричные функции и тип-аннотации зависимостей для модуля пользователей.
"""

from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from modules.database import get_session

from .repositories import UserRepository


def get_user_repository(session: Annotated[Session, Depends(get_session)]):
    """FastAPI-зависимость: возвращает UserRepository для текущей сессии."""
    return UserRepository(session)


UsersRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
"""Инъекция UserRepository через систему зависимостей FastAPI."""