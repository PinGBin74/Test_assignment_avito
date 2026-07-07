import datetime

from fastapi import Request
from fastapi.responses import JSONResponse

from src.exceptions import AppError


def utc_now_naive() -> datetime.datetime:
    """Returns the current UTC time as a naive datetime object."""
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}},
    )
