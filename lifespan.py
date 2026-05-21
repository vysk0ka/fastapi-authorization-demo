"""
Управление жизненным циклом приложения FastAPI.

При старте выполняет инициализацию базы данных (создание таблиц).
Используется как аргумент `lifespan` при создании экземпляра FastAPI.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from modules.database import setup_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Запускает инициализацию БД перед началом обработки запросов."""
    setup_database()
    yield
