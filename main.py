from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from database import engine
from backend.basic.views import router as basic_router
from backend.admin.views import router as admin_router
from backend.post.views import router as post_router
from backend.admin import models as admin_models
from backend.post import models as post_models
from backend.admin.models import init_roles
from backend.exceptions import http_exception_handler, custom_http_exception_handler, custom_exception_handler, rate_limit_exceeded_handler
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from backend.limiter import limiter
from slowapi.errors import RateLimitExceeded


admin_models.Base.metadata.create_all(bind=engine)
post_models.Base.metadata.create_all(bind=engine)

app = FastAPI()


origins = ['http://localhost:3000']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins
)
app.add_middleware(GZipMiddleware)

app.include_router(basic_router)
app.include_router(admin_router)
app.include_router(post_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, custom_http_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, custom_exception_handler)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

@app.on_event("startup")
def on_startup():
    init_roles()

@app.get("/trigger-500")
async def trigger_500():
    raise Exception("This is a test for a 500 error")


