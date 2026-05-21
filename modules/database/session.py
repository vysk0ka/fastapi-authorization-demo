"""
Управление сессиями SQLModel и транзакциями.
"""

from contextlib import contextmanager
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from .engine import engine


def get_session():
    """
    Генератор FastAPI-зависимости, открывающий сессию БД на время обработки запроса.

    Yields:
        Session: активная сессия SQLModel.
    """
    with Session(engine) as session:
        yield session


@contextmanager
def transaction(session: Session):
    """
    Контекстный менеджер для выполнения операций в рамках одной транзакции.

    При успешном выходе из блока вызывает commit().
    При любом исключении выполняет rollback() и перебрасывает исключение.

    Args:
        session: активная сессия SQLModel.

    Yields:
        Session: та же сессия, переданная на вход.
    """
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise


SessionDep = Annotated[Session, Depends(get_session)]
"""Тип-аннотация для инъекции сессии БД через систему зависимостей FastAPI."""
