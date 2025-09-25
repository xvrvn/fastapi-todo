import os
import sys
from logging.config import fileConfig

from alembic import context

# 添加项目根目录到 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 导入数据库和模型
from sqlmodel import SQLModel

import src.auth.models  # noqa: F401
import src.tasks.models  # noqa: F401
from src.database import engine, settings

# Alembic 配置
config = context.config
fileConfig(config.config_file_name)  # type: ignore

# 使用 SQLModel.metadata 作为目标元数据
target_metadata = SQLModel.metadata


def run_migrations_offline():
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
