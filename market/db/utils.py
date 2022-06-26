from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional
import uuid

from alembic.config import Config
from sqlalchemy.engine import make_url
from sqlalchemy_utils import create_database, drop_database


WORKDIR = Path(__file__).parents[1]


def create_alembic_config(db_url: str) -> Config:
    config_path = Path(WORKDIR, 'alembic.ini').absolute()
    config = Config(str(config_path))

    script_location = Path(WORKDIR, config.get_main_option('script_location'))
    config.set_main_option('script_location', str(script_location))

    config.set_main_option('sqlalchemy.url', db_url)

    return config


@contextmanager
def tmp_database(db_url: str, template_db: Optional[str] = None) -> Generator[str, None, None]:
    tmp_db_name = f'{uuid.uuid4()}.pytest'
    tmp_db_url = make_url(db_url)
    tmp_db_url = tmp_db_url._replace(database=tmp_db_name)

    sync_tmp_db_url = tmp_db_url._replace(drivername='postgresql')
    create_database(sync_tmp_db_url, template=template_db)

    try:
        yield str(tmp_db_url)
    finally:
        drop_database(sync_tmp_db_url)
