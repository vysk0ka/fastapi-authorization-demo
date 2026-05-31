"""
Движок базы данных SQLAlchemy и инициализация схемы.
"""

from sqlmodel import create_engine

from settings import get_settings

engine = create_engine(get_settings().database_url)
"""Глобальный экземпляр движка SQLAlchemy, созданный на основе DATABASE_URL из настроек."""
