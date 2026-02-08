from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.config import config

engine = create_async_engine(
    config.postgres.data.database_url,
    echo=config.app.debug,
    pool_size=config.postgres.data.pool_size,
    max_overflow=config.postgres.data.pool_max_overflow,
    pool_recycle=config.postgres.data.pool_recycle,
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
