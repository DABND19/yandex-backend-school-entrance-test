from fastapi import APIRouter

from .api import router as shop_router
from .exceptions import (
    request_validation_error_handler,
    http_error_handler
)


router = APIRouter()
router.include_router(shop_router)
