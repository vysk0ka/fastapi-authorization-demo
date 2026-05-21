"""
HMAC-сервис для защиты refresh-токенов от подделки на стороне сервера.

Хранение только HMAC-хеша (а не самого токена) в БД означает, что
даже при утечке БД злоумышленник не сможет напрямую использовать токены.
"""

import hashlib
import hmac


class HMACService:
    """
    Сервис вычисления и верификации HMAC-SHA256 хешей строк.

    Используется для защиты refresh-токенов: в базе данных хранится только
    HMAC-хеш токена, а не сам токен.
    """

    def __init__(self, secret: str):
        """
        Args:
            secret: секретный ключ HMAC из настроек приложения.
        """
        self.secret = secret.encode()

    def compute(self, plain: str) -> str:
        """
        Вычисляет HMAC-SHA256 хеш строки.

        Args:
            plain: входная строка (refresh-токен).

        Returns:
            Шестнадцатеричная строка хеша.
        """
        encoded = plain.encode()

        return hmac.new(self.secret, encoded, hashlib.sha256).hexdigest()

    def verify(self, value: str, expected: str) -> bool:
        """
        Проверяет, соответствует ли строка ожидаемому HMAC-хешу.

        Использует hmac.compare_digest для защиты от timing-атак.

        Args:
            value: строка для проверки.
            expected: ожидаемый хеш из базы данных.

        Returns:
            True, если хеши совпадают.
        """
        actual_hash = self.compute(value)

        return hmac.compare_digest(actual_hash, expected)
