from fastapi import APIRouter

from .exceptions import (
    request_validation_error_handler,
    http_error_handler
)


router = APIRouter()
