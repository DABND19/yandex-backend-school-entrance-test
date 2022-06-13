from typing import AsyncGenerator
import uuid

from alembic.command import upgrade
from alembic.config import Config
from httpx import AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.app import get_app
from src.db.connection import get_session


@pytest.fixture(scope='class')
def migrated_database_url(alembic_config: Config):
    upgrade(alembic_config, 'head')
    yield alembic_config.get_main_option('sqlalchemy.url')


@pytest.fixture(scope='class')
def get_mock_session(migrated_database_url: str):
    engine = create_async_engine(migrated_database_url)
    Session = sessionmaker(bind=engine, class_=AsyncSession, 
                           autocommit=False, autoflush=False)
    async def get_session() -> AsyncGenerator[AsyncSession, None]:
        async with Session() as session:
            yield session
    yield get_session


@pytest.fixture(scope='class')
async def api_client(get_mock_session) -> AsyncClient:
    app = get_app()
    app.dependency_overrides[get_session] = get_mock_session
    base_url = f'http://{uuid.uuid4()}'
    async with AsyncClient(app=app, base_url=base_url) as client:
        yield client
