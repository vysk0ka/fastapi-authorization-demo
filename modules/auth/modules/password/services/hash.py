"""Сервис хеширования и верификации паролей через passlib."""

from passlib.context import CryptContext


class HashService:
    """
    Сервис хеширования паролей на основе passlib CryptContext.

    Алгоритм хеширования определяется переданным CryptContext
    """

    def __init__(self, context: CryptContext):
        self.context = context

    def to_hashed(self, source: str) -> str:
        """
        Хеширует строку (пароль) и возвращает хеш.

        Args:
            source: строка в открытом виде.

        Returns:
            Хеш пароля для сохранения в базе данных.
        """
        return self.context.hash(source)

    def verify(self, plain: str, hashed: str) -> bool:
        """
        Проверяет соответствие открытого пароля его хешу.

        Args:
            plain: пароль в открытом виде (из запроса пользователя).
            hashed: хеш пароля из базы данных.

        Returns:
            True, если пароль соответствует хешу. Иначе False
        """
        return self.context.verify(plain, hashed)
