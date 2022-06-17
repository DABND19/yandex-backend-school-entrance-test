from pathlib import Path

from alembic.config import Config


WORKDIR = Path(__file__).parents[1]


def create_alembic_config(db_url: str) -> Config:
    config_path = Path(WORKDIR, 'alembic.ini').absolute()
    config = Config(str(config_path))

    script_location = Path(WORKDIR.parent, config.get_main_option('script_location'))
    config.set_main_option('script_location', str(script_location))

    config.set_main_option('sqlalchemy.url', db_url)

    return config


if __name__ == '__main__':
    from market.config import settings
    create_alembic_config(settings.db_url)
