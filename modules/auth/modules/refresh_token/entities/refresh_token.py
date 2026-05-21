"""SQLModel-сущность refresh-токена, хранимая в таблице refresh_tokens."""

import uuid
from datetime import datetime, timezone

from sqlmodel import Field, Relationship, SQLModel

from modules.auth.modules.user import User


class RefreshToken(SQLModel, table=True):
    """
    Запись refresh-токена в базе данных.

    Реализует стратегию Refresh Token Rotation с поддержкой обнаружения
    повторного использования через поле used_at и группировки токенов
    одного сеанса через family_id.

    Поля:
        id: уникальный идентификатор токена (совпадает с claim jti в JWT).
        family_id: идентификатор семьи токенов одного сеанса; при обнаружении
                   повторного использования токена инвалидируется вся семья.
        user_id: внешний ключ на таблицу users.
        token_hash: HMAC-SHA256 хеш строки токена для верификации без хранения токена.
        expires_at: время истечения токена.
        used_at: время первого использования для обновления; None — токен ещё не использован.
        created_at: время создания записи (UTC).
    """

    __tablename__ = "refresh_tokens"  # type: ignore[assignment]

    user: User = Relationship(back_populates="refresh_tokens")

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    family_id: uuid.UUID = Field(index=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)

    token_hash: str = Field(index=True, unique=True)

    expires_at: datetime
    used_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
