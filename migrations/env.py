import sqlmodel
from alembic import context

from modules.auth.modules.refresh_token import RefreshToken  # noqa: F401
from modules.auth.modules.user import User  # noqa: F401
from modules.database.engine import engine

_ = (User, RefreshToken)  # Необходимо, чтобы форматтер не удалял импорты

target_metadata = sqlmodel.SQLModel.metadata


def run_migrations_online():
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
