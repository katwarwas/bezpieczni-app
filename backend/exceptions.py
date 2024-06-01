from fastapi import Request
from backend.admin.views import templates
from starlette.exceptions import HTTPException 

async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse(
        "htmx/exceptions.html",
        {"request": request, "status_code": exc.status_code, "detail": "Page " + exc.detail},
        status_code=exc.status_code,)

    return templates.TemplateResponse(
        "htmx/exceptions.html",
        {"request": request, "status_code": exc.status_code, "detail": exc.detail},
        status_code=exc.status_code,
    )