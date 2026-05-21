"""Репозиторий для работы с записями refresh-токенов в базе данных."""

import uuid
from datetime import datetime, timezone

from sqlmodel import Session, col, delete

from ..entities import RefreshToken


class RefreshTokenRepository:
    """
    Инкапсулирует все операции с таблицей refresh_tokens.

    Все методы работают в рамках переданной сессии; commit/rollback
    выполняются снаружи через контекстный менеджер transaction().
    """

    def __init__(self, session: Session):
        self.session = session

    def add(
        self,
        *,
        id: uuid.UUID | None = None,
        family_id: uuid.UUID,
        user_id: uuid.UUID,
        token_hash: str,
        expires_at: datetime,
    ) -> RefreshToken:
        """
        Создаёт новую запись refresh-токена.

        Args:
            id: опциональный UUID токена; если не передан — генерируется автоматически.
            family_id: идентификатор семьи токенов текущего сеанса.
            user_id: идентификатор пользователя-владельца.
            token_hash: HMAC-хеш строки токена.
            expires_at: время истечения токена.

        Returns:
            Созданный и сброшенный (flush) экземпляр RefreshToken.
        """
        token_id = id if id else uuid.uuid4()

        token = RefreshToken(
            id=token_id,
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            family_id=family_id,
        )

        self.session.add(token)
        self.session.flush()

        return token

    def get_by_id(self, token_id: uuid.UUID) -> RefreshToken | None:
        """
        Возвращает токен по его идентификатору.

        Args:
            token_id: UUID токена (claim jti).

        Returns:
            RefreshToken или None, если запись не найдена.
        """
        return self.session.get(RefreshToken, token_id)

    def delete_by_id(self, token_id: uuid.UUID) -> RefreshToken | None:
        """
        Удаляет токен по идентификатору.

        Args:
            token_id: UUID токена.

        Returns:
            Удалённый RefreshToken или None, если токен не найден.
        """
        token = self.get_by_id(token_id)

        if not token:
            return None

        self.session.delete(token)

        return token

    def mark_as_used(self, token_id: uuid.UUID) -> RefreshToken | None:
        """
        Помечает токен как использованный, устанавливая used_at = now (UTC).

        Args:
            token_id: UUID токена.

        Returns:
            Обновлённый RefreshToken или None, если токен не найден.
        """
        token = self.get_by_id(token_id)

        if token:
            token.used_at = datetime.now(timezone.utc)
            self.session.add(token)
            self.session.flush()

        return token

    def invalidate_family(self, family_id: uuid.UUID) -> None:
        """
        Удаляет все токены семьи — используется при обнаружении повторного
        использования refresh-токена (возможная кража).

        Args:
            family_id: идентификатор семьи токенов для инвалидации.
        """
        statement = delete(RefreshToken).where(col(RefreshToken.family_id) == family_id)
        self.session.exec(statement)
