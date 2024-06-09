from fastapi import Request
from backend.admin.views import templates
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as starletteHTTPException

async def http_exception_handler(request: Request, exc: starletteHTTPException):

    return templates.TemplateResponse(
        "htmx/exceptions.html",
        {"request": request, "status_code": exc.status_code, "detail": exc.detail},
        status_code=exc.status_code,
    )

async def custom_http_exception_handler(request: Request, exc: RequestValidationError):
    return templates.TemplateResponse(
        "htmx/exceptions.html",
        {"request": request, "status_code": 422, "detail": "Invalid input provided."},
        status_code=422,
    )


async def custom_exception_handler(request: Request, exc: Exception):
    return templates.TemplateResponse(
        "htmx/exceptions.html",
        {"request": request, "status_code": 500, "detail": "Internal Server Error."},
        status_code=500,
    )