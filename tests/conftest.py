import asyncio

from alembic.command import upgrade
import pytest

from market.config import settings
from market.db.utils import create_alembic_config, tmp_database


@pytest.fixture(scope='session')
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope='session')
def template_db_url() -> str:
    with tmp_database(settings.db_url) as db_url:
        alembic = create_alembic_config(db_url)
        upgrade(alembic, 'head')
        yield db_url
