from pydantic import BaseSettings, PostgresDsn


class Settings(BaseSettings):
    app_host: str = 'localhost'
    app_port: int = 8000

    is_debug: bool = False
    db_url: PostgresDsn = 'postgresql+asyncpg://postgres:password@localhost:5432/postgres'


settings = Settings(
    _env_file='.env',
    _env_file_encoding='utf-8'
)
