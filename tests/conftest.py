import asyncio
from pathlib import Path
import uuid

from alembic.config import Config
import pytest
from sqlalchemy.engine import make_url
from sqlalchemy_utils import create_database, drop_database

from src.config import settings


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope='class')
def mock_database_url() -> str:
    tmp_db_name = f'{uuid.uuid4()}.pytest'
    tmp_db_url = make_url(settings.db_url)
    tmp_db_url = tmp_db_url._replace(database=tmp_db_name)

    sync_tmp_db_url = tmp_db_url._replace(drivername='postgresql')
    create_database(sync_tmp_db_url)

    try:
        yield str(tmp_db_url)
    finally:
        drop_database(sync_tmp_db_url)


@pytest.fixture(scope='class')
def alembic_config(mock_database_url: str) -> Config:
    config_path = Path('alembic.ini').absolute()
    config = Config(str(config_path))

    script_location = Path(config.get_main_option('script_location'))
    if not script_location.is_absolute():
        script_location = script_location.absolute()
        config.set_main_option('script_location', str(script_location))

    config.set_main_option('sqlalchemy.url', str(mock_database_url))
    return config