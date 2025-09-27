from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from .config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)
async_session_maker = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def get_session() -> AsyncSession:  # type: ignore
    async with async_session_maker() as session:
        yield session  # type: ignore


async def init_db():
    import src.auth.models  # noqa
    import src.tasks.models  # noqa

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
