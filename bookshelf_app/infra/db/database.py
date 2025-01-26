# pylint: disable=not-callable
from datetime import datetime
from typing import Iterator

from sqlalchemy import Boolean, DateTime, create_engine, func, text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from bookshelf_app.config import get_settings

# SQLALCHEMY_DATABASE_URL = "sqlite:///./fastapi_app.db"
SQLALCHEMY_DATABASE_URL = get_settings().db_connection

# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_modified: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)


class DeletableBase(Base):
    __abstract__ = True

    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)


def get_session() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)


def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def truncate_tables():
    # truncate all tables
    for table in reversed(Base.metadata.sorted_tables):
        for session in get_session():
            session.execute(text(f"TRUNCATE {table.name} CASCADE;"))
            session.commit()


def truncate_table(table_name: str):
    for session in get_session():
        session.execute(text(f"TRUNCATE {table_name} CASCADE;"))
        session.commit()
