from datetime import datetime
import re

import humps
from pydantic import BaseModel, BaseConfig, validator


DATETIME_ISO8601_PATTERN = re.compile(
    r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z'
)


def datetime_iso8601_decoder(value: str) -> datetime:
    if not DATETIME_ISO8601_PATTERN.match(value):
        raise ValueError('Invalida date format')
    return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')


def datetime_iso8601_validator(*fields: str):
    @validator(*fields, pre=True, allow_reuse=True)
    def wrapper(value: str) -> datetime:
        return datetime_iso8601_decoder(value)
    return wrapper


def datetime_iso8601_encoder(value: datetime) -> str:
    return f'{value.isoformat(timespec="milliseconds")}Z'


class BaseSchema(BaseModel):
    class Config(BaseConfig):
        orm_mode = True
        alias_generator = humps.camelize
        use_enum_values = True
        allow_population_by_field_name = True
        json_encoders = {
            datetime: datetime_iso8601_encoder
        }


class ErrorSchema(BaseSchema):
    code: int
    message: str
