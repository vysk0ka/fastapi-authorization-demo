"""
Точка входа приложения.

Создаёт экземпляр FastAPI, подключает lifespan-обработчик для инициализации
базы данных при запуске и регистрирует роутер модуля аутентификации.
"""

from fastapi import FastAPI

from modules.auth import router as auth_router
from lifespan import lifespan

app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)

