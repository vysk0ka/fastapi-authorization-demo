"""SQLModel-сущность пользователя, хранимая в таблице users."""

import uuid

from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    """
    Запись пользователя в базе данных.

    Поля:
        id: уникальный идентификатор пользователя (UUID).
        username: уникальное имя пользователя; используется для входа.
        email: уникальный адрес электронной почты; исключён из сериализации.
        hashed_password: хеш пароля (Argon2); исключён из сериализации.

    Связи:
        refresh_tokens: все refresh-токены, принадлежащие пользователю.
    """

    __tablename__ = "users"  # type: ignore[assignment]

    refresh_tokens: list["RefreshToken"] = Relationship(back_populates="user")  # type: ignore  # noqa: F821

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(exclude=True, index=True, unique=True)
    hashed_password: str = Field(exclude=True)
