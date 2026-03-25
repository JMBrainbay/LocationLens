from __future__ import annotations

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ApiErrorPayload(BaseModel):
    code: str
    message: str
    details: dict | None = None


class ApiError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400, details: dict | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details


def to_error_response(status_code: int, payload: ApiErrorPayload) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": payload.model_dump(exclude_none=True)},
    )


async def api_error_handler(_: Request, exc: ApiError) -> JSONResponse:
    return to_error_response(
        exc.status_code,
        ApiErrorPayload(code=exc.code, message=exc.message, details=exc.details),
    )


async def unhandled_error_handler(_: Request, exc: Exception) -> JSONResponse:
    return to_error_response(
        500,
        ApiErrorPayload(code="internal_error", message="Unexpected server error"),
    )


async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return to_error_response(
        422,
        ApiErrorPayload(code="validation_error", message="Request validation failed", details={"issues": exc.errors()}),
    )
