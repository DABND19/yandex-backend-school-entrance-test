from http import HTTPStatus

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from src.schemas import ErrorSchema


def request_validation_error_handler(
    request: Request, 
    exc: RequestValidationError
) -> JSONResponse:
    status_code = HTTPStatus.BAD_REQUEST
    payload = ErrorSchema(code=status_code, message='Validation Error')
    return JSONResponse(jsonable_encoder(payload), status_code)


def http_error_handler(
    request: Request, 
    exc: HTTPException
) -> JSONResponse:
    payload = ErrorSchema(code=exc.status_code, message=exc.detail)
    return JSONResponse(jsonable_encoder(payload), exc.status_code)
