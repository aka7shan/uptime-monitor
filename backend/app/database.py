import asyncio

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from .config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


async def init_db(retries: int = 15, delay: float = 2.0) -> None:
    """Create tables, retrying until Postgres is reachable on startup."""
    from . import models  # noqa: F401  register models on Base metadata

    last_error: Exception | None = None
    for _ in range(retries):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            return
        except Exception as exc:  # noqa: BLE001  broad on purpose during boot
            last_error = exc
            await asyncio.sleep(delay)
    raise RuntimeError(f"Database not ready after {retries} attempts: {last_error}")
