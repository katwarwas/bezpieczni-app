from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from database import engine
from basic.views import router as basic_router
from backend.admin.views import router as admin_router
from backend.post.views import router as post_router
from backend.admin import models as admin_models
from backend.post import models as post_models
from backend.exceptions import http_exception_handler
from starlette.exceptions import HTTPException 


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

app.add_exception_handler(HTTPException, http_exception_handler)
