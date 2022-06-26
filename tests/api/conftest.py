from typing import AsyncGenerator
import uuid

from httpx import AsyncClient
import pytest
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from market.app import get_app
from market.db.connection import get_session
from market.db.utils import tmp_database


@pytest.fixture()
def migrated_database_url(template_db_url: str):
    template_db = make_url(template_db_url).database
    with tmp_database(template_db_url, template_db) as db_url:
        yield db_url


@pytest.fixture()
def get_mock_session(migrated_database_url: str):
    engine = create_async_engine(migrated_database_url)
    Session = sessionmaker(bind=engine, class_=AsyncSession, 
                           autocommit=False, autoflush=False)
    async def get_session() -> AsyncGenerator[AsyncSession, None]:
        async with Session() as session:
            yield session
    yield get_session


@pytest.fixture()
async def api_client(get_mock_session) -> AsyncClient:
    app = get_app()
    app.dependency_overrides[get_session] = get_mock_session
    base_url = f'http://{uuid.uuid4()}'
    async with AsyncClient(app=app, base_url=base_url) as client:
        yield client
