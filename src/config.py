from pydantic import BaseSettings, PostgresDsn


class Settings(BaseSettings):
    is_debug: bool = True
    db_url: PostgresDsn = 'postgresql+asyncpg://postgres:password@localhost:5432/postgres'


settings = Settings(
    _env_file='.env',
    _env_file_encoding='utf-8'
)
