from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from src.handlers import (
    router, 
    http_error_handler, 
    request_validation_error_handler
)


def get_app() -> FastAPI:
    app = FastAPI()

    app.include_router(router)

    app.add_exception_handler(
        RequestValidationError, 
        request_validation_error_handler
    )
    app.add_exception_handler(HTTPException, http_error_handler)

    return app
