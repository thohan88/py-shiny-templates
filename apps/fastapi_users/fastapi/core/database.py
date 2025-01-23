from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.engine import make_url
from collections.abc import AsyncGenerator
from ...config import settings
import os

class Base(DeclarativeBase):
    pass

engine = create_async_engine(settings.db_url)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def destroy_db():
    db_path = make_url(settings.db_url).database
    if os.path.exists(db_path):
        os.remove(db_path)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session