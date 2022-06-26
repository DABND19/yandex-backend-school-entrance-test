from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from market import __version__ as api_version
from market.handlers import (
    router, 
    http_error_handler, 
    request_validation_error_handler
)
from market.schemas import ErrorSchema


def get_app() -> FastAPI:
    app = FastAPI(
        title='Mega Market API',
        version=api_version,
        description='Вступительное задание в Летнюю Школу Бэкенд Разработки Яндекса 2022', 
        responses={
        '4XX': {'model': ErrorSchema},
    })

    app.include_router(router)

    app.add_exception_handler(
        RequestValidationError, 
        request_validation_error_handler
    )
    app.add_exception_handler(HTTPException, http_error_handler)

    return app
