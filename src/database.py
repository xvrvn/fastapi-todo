from sqlmodel import Session, SQLModel, create_engine

from .config import settings

engine = create_engine(settings.DATABASE_URL, echo=False)


def get_session():
    with Session(engine) as session:
        yield session


def init_db():
    import src.auth.models
    import src.tasks.models  # noqa: F401

    SQLModel.metadata.create_all(engine)
