from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.config import settings


engine = create_async_engine(settings.db_url, echo=settings.is_debug)
Session = sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    autocommit=False, 
    autoflush=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with Session() as session:
        yield session
