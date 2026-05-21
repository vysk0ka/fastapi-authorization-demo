"""Репозиторий для работы с записями пользователей в базе данных."""

import uuid

from sqlmodel import Session, select

from ..entities import User


class UserRepository:
    """
    Инкапсулирует все операции с таблицей users.

    Все методы работают в рамках переданной сессии; commit/rollback
    выполняются снаружи через контекстный менеджер transaction().
    """

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        """
        Возвращает пользователя по UUID.

        Args:
            user_id: идентификатор пользователя.

        Returns:
            User или None, если пользователь не найден.
        """
        return self.session.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        """
        Возвращает пользователя по адресу электронной почты.

        Args:
            email: адрес электронной почты.

        Returns:
            User или None.
        """
        statement = select(User).where(User.email == email)
        result = self.session.exec(statement).first()

        return result

    def get_by_username(self, username: str) -> User | None:
        """
        Возвращает пользователя по имени пользователя.

        Args:
            username: имя пользователя.

        Returns:
            User или None.
        """
        statement = select(User).where(User.username == username)
        result = self.session.exec(statement).first()

        return result

    def create(
        self,
        *,
        username: str,
        email: str,
        password_hash: str,
    ) -> User:
        """
        Создаёт нового пользователя.

        Args:
            username: уникальное имя пользователя.
            email: уникальный адрес электронной почты.
            password_hash: хеш пароля (Argon2).

        Returns:
            Созданный и сброшенный (flush) экземпляр User.
        """
        user = User(
            username=username,
            email=email,
            hashed_password=password_hash,
        )

        self.session.add(user)
        self.session.flush()

        return user
