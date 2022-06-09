import humps
from pydantic import BaseModel, BaseConfig


class BaseSchema(BaseModel):
    class Config(BaseConfig):
        orm_mode = True
        alias_generator = humps.camelize


class ErrorSchema(BaseSchema):
    code: int
    message: str
