from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from config import settings

# 构建异步 MySQL 数据库 URL
ASYNC_MYSQL_URL = (
    f"mysql+aiomysql://{settings.MYSQL.user}:{settings.MYSQL.password}"
    f"@{settings.MYSQL.host}:{settings.MYSQL.port}/{settings.MYSQL.db}"
)

SYNC_MYSQL_URL = (
    f"mysql+pymysql://{settings.MYSQL.user}:{settings.MYSQL.password}"
    f"@{settings.MYSQL.host}:{settings.MYSQL.port}/{settings.MYSQL.db}"
)

# 创建异步 Engine 和 Session
async_engine = create_async_engine(ASYNC_MYSQL_URL, echo=True, future=True)
async_session = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
)
sync_engine = create_engine(SYNC_MYSQL_URL, echo=True, future=True)
sync_session = sessionmaker(
    sync_engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


def get_sync_session():
    """Synchronous session dependency."""
    try:
        session = sync_session()
        yield session
    finally:
        session.rollback()
        session.close()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]
SessionDep = Annotated[Session, Depends(get_sync_session)]
