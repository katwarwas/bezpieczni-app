from fastapi import APIRouter, Request
from sqlalchemy import desc
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from database import DbSession
from backend.post.models import Posts
from backend.admin.models import Users
from .services import image_base64
from backend.post.services import get_photos_in_range, get_photo
from math import ceil
from uuid import uuid4


router = APIRouter(
    tags=["basic"]
)

templates = Jinja2Templates(directory="templates", autoescape=False)


@router.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})


@router.get("/cyberattacks", response_class=HTMLResponse)
async def cyberattacks_page(request: Request):
    return templates.TemplateResponse("subpages/cyber_attacks.html", {"request": request})


@router.get("/news/page-{page}", response_class=HTMLResponse)
async def posts(request: Request, db: DbSession, page: int = 0):
    posts = db.query(Posts).order_by(desc(Posts.created_at)).limit(12).offset((page-1)*12).all()
    pages = ceil(db.query(Posts).count() / 12)
    return templates.TemplateResponse("subpages/news.html", {"request": request, "posts": posts, "pages": pages, "actual_page": page})


@router.get("/news/{id}", response_class=HTMLResponse)
async def posts(request: Request, db: DbSession, id: int):
    post = db.query(Posts).filter(Posts.id == id).one_or_none()
    author = db.query(Users).filter(Users.id == post.user_id).one_or_none()
    return templates.TemplateResponse("subpages/actual_news.html", {"request": request, "post": post, "author": author})


@router.get("/analysis", response_class=HTMLResponse)
async def analysis_page(request: Request):
    fig = image_base64()
    return templates.TemplateResponse("subpages/analysis.html", {"request": request, "fig": fig})