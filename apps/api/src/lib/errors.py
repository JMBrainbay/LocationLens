from __future__ import annotations

from typing import Any, Sequence

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


def _friendly_validation_message(issues: Sequence[Any]) -> str:
    if not issues:
        return "We could not read that request. Check query parameters and try again."
    first = issues[0] if isinstance(issues[0], dict) else {}
    loc = first.get("loc") or ()
    parts = [str(x) for x in loc if x not in ("body", "query", "path", "header")]
    field = " → ".join(parts) if parts else "request"
    msg = str(first.get("msg", "Invalid value")).strip()
    return f"Invalid {field}: {msg}."


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
        ApiErrorPayload(
            code="internal_error",
            message="Something went wrong on the server. If you are debugging, check the API terminal output.",
        ),
    )


async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    issues = exc.errors()
    return to_error_response(
        422,
        ApiErrorPayload(
            code="validation_error",
            message=_friendly_validation_message(issues),
            details={"issues": issues},
        ),
    )
