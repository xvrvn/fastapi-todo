import asyncio
import os
import sys
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

from alembic import context

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 导入模型
import src.auth.models  # noqa: F401
import src.tasks.models  # noqa: F401
from src.database import settings

config = context.config
fileConfig(config.config_file_name)  # type: ignore

target_metadata = SQLModel.metadata  # type: ignore


def run_migrations_offline():
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = create_async_engine(settings.DATABASE_URL, future=True)

    async def do_run_migrations():
        async with connectable.begin() as connection:
            await connection.run_sync(
                lambda sync_conn: context.configure(
                    connection=sync_conn,
                    target_metadata=target_metadata,
                    compare_type=True,
                )
            )
            await connection.run_sync(lambda sync_conn: context.run_migrations())

    asyncio.run(do_run_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
