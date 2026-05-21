"""
Конфигурация приложения через переменные окружения.

Значения считываются из файла .env при первом вызове get_settings().
Повторные вызовы возвращают кешированный экземпляр (lru_cache).
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Настройки приложения.

    Поля:
        database_url: строка подключения к базе данных (SQLAlchemy DSN).
        access_token_secret: секрет для подписи access-токенов.
        access_token_expire_minutes: время жизни access-токена в минутах.
        refresh_token_secret: секрет для подписи refresh-токенов.
        refresh_token_expire_minutes: время жизни refresh-токена в минутах.
        refresh_token_hmac_secret: секрет HMAC для дополнительной защиты refresh-токена.
        jwt_algorithm: алгоритм подписи JWT (например, HS256).
    """

    database_url: str

    access_token_secret: str
    access_token_expire_minutes: int

    refresh_token_secret: str
    refresh_token_expire_minutes: int
    refresh_token_hmac_secret: str

    jwt_algorithm: str

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def _build_settings():
    """Создаёт и кеширует экземпляр Settings."""
    return Settings()  # type: ignore


def get_settings():
    """Возвращает кешированный экземпляр Settings. Используется как FastAPI-зависимость."""
    return _build_settings()  # type: ignore
