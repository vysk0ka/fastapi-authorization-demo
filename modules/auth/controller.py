"""
Контроллер аутентификации.

Содержит бизнес-логику регистрации, входа, выхода и обновления токенов.
Все зависимости внедряются через систему DI FastAPI.
"""

import uuid

from fastapi import status
from fastapi.exceptions import HTTPException

from modules.database import SessionDep, transaction

from .models.login import AuthLoginBody, AuthLoginResponse
from .models.register import AuthRegisterBody, AuthRegisterResponse
from .modules.jwt import (
    JWTAccessDep,
    JWTAuthorizationCredentials,
    JWTRefreshDep,
    JWTRefreshPayload,
)
from .modules.password import PasswordHashServiceDep
from .modules.refresh_token import (
    RefreshTokenHMACServiceDep,
    RefreshTokensRepositoryDep,
)
from .modules.user import User, UsersRepositoryDep


class AuthController:
    """
    Контроллер, реализующий операции аутентификации пользователей.

    Зависимости:
        users: репозиторий пользователей.
        refresh_tokens: репозиторий refresh-токенов.
        access: стратегия подписи/верификации access JWT.
        refresh: стратегия подписи/верификации refresh JWT.
        password_hash_service: сервис хеширования паролей (Argon2).
        refresh_token_hash_service: сервис HMAC-хеширования refresh-токенов.
        session: сессия базы данных.
    """

    def __init__(
        self,
        users: UsersRepositoryDep,
        refresh_tokens: RefreshTokensRepositoryDep,
        access: JWTAccessDep,
        refresh: JWTRefreshDep,
        password_hash_service: PasswordHashServiceDep,
        refresh_token_hash_service: RefreshTokenHMACServiceDep,
        session: SessionDep,
    ):
        self.users = users
        self.refresh_tokens = refresh_tokens
        self.jwt_access = access
        self.jwt_refresh = refresh
        self.password_hash_service = password_hash_service
        self.refresh_token_hash_service = refresh_token_hash_service
        self.session = session

    def _issue_tokens_for(self, user: User, family_id: uuid.UUID) -> tuple[str, str]:
        """
        Создаёт новую пару access/refresh токенов для пользователя и сохраняет
        HMAC-хеш refresh-токена в базе данных.

        Args:
            user: пользователь, для которого выпускаются токены.
            family_id: идентификатор семьи токенов (используется для инвалидации
                       всей цепочки при обнаружении повторного использования).

        Returns:
            Кортеж (access_token, refresh_token) в виде строк JWT.
        """
        token_id = uuid.uuid4()

        payload = {"sub": str(user.id)}
        refresh_payload = {**payload, "jti": str(token_id)}

        access_token, _ = self.jwt_access.sign(payload=payload)
        refresh_token, expires_at = self.jwt_refresh.sign(payload=refresh_payload)

        refresh_token_hash = self.refresh_token_hash_service.compute(refresh_token)

        self.refresh_tokens.add(
            id=token_id,
            family_id=family_id,
            user_id=user.id,
            token_hash=refresh_token_hash,
            expires_at=expires_at,
        )

        return access_token, refresh_token

    def register(self, body: AuthRegisterBody) -> AuthRegisterResponse:
        """
        Регистрирует нового пользователя.

        Проверяет уникальность email и username, создаёт запись пользователя
        с хешированным паролем и сразу выдаёт пару токенов.

        Args:
            body: данные формы регистрации.

        Returns:
            AuthRegisterResponse с парой access/refresh токенов.

        Raises:
            HTTPException(409): если email или username уже зарегистрированы.
        """
        if self.users.get_by_email(body.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
            )

        if self.users.get_by_username(body.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Username already taken"
            )

        family_id = uuid.uuid4()
        password_hash = self.password_hash_service.to_hashed(body.password)

        with transaction(self.session):
            user = self.users.create(
                username=body.username, email=body.email, password_hash=password_hash
            )

            access_token, refresh_token = self._issue_tokens_for(user, family_id)

        return AuthRegisterResponse(
            access_token=access_token, refresh_token=refresh_token
        )

    def login(self, body: AuthLoginBody) -> AuthLoginResponse:
        """
        Аутентифицирует пользователя по username и паролю.

        Args:
            body: учётные данные пользователя.

        Returns:
            AuthLoginResponse с парой access/refresh токенов.

        Raises:
            HTTPException(401): если пользователь не найден или пароль неверен.
        """
        user = self.users.get_by_username(body.username)

        if not user or not self.password_hash_service.verify(
            body.password, user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        family_id = uuid.uuid4()

        with transaction(self.session):
            access_token, refresh_token = self._issue_tokens_for(user, family_id)

        return AuthLoginResponse(access_token=access_token, refresh_token=refresh_token)

    def logout(self, credentials: JWTAuthorizationCredentials[JWTRefreshPayload]):
        """
        Инвалидирует refresh-токен пользователя (выход из системы).

        Находит запись токена по jti из payload, проверяет HMAC-подпись
        и удаляет токен из базы данных.

        Args:
            credentials: верифицированные Bearer-реквизиты с refresh-payload.

        Returns:
            dict: {"ok": True}.

        Raises:
            HTTPException(401): если токен не найден или HMAC-проверка не прошла.
        """
        token_id = credentials.payload.jti

        with transaction(self.session):
            token = self.refresh_tokens.get_by_id(token_id)

            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
                )

            is_valid_token = self.refresh_token_hash_service.verify(
                credentials.credentials, token.token_hash
            )

            if not is_valid_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
                )

            self.refresh_tokens.delete_by_id(token_id)

            return {"ok": True}

    def refresh(self, credentials: JWTAuthorizationCredentials[JWTRefreshPayload]):
        """
        Обновляет пару токенов по действующему refresh-токену (Refresh Token Rotation).

        Алгоритм:
        1. Ищет токен по jti; если не найден — 401.
        2. Если токен уже использован (used_at != None) — инвалидирует всю семью и 401
           (защита от повторного использования украденного токена).
        3. Проверяет HMAC-подпись токена.
        4. Помечает текущий токен как использованный и выпускает новую пару.

        Args:
            credentials: верифицированные Bearer-реквизиты с refresh-payload.

        Returns:
            dict: {"access_token": str, "refresh_token": str}.

        Raises:
            HTTPException(401): при любом нарушении валидации токена.
        """
        token_id = credentials.payload.jti
        token = self.refresh_tokens.get_by_id(token_id)

        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        if token.used_at is not None:
            with transaction(self.session):
                self.refresh_tokens.invalidate_family(token.family_id)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        if not self.refresh_token_hash_service.verify(
            credentials.credentials, token.token_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        user = self.users.get_by_id(token.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        with transaction(self.session):
            self.refresh_tokens.mark_as_used(token_id)
            access_token, refresh_token = self._issue_tokens_for(user, token.family_id)

        return {"access_token": access_token, "refresh_token": refresh_token}
