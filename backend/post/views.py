from fastapi import APIRouter, Request, Response, Form, Depends, HTTPException
from database import DbSession
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse
from starlette import status
from typing import Annotated, Optional
from backend.admin.services import get_current_user
from .models import Posts
from backend.admin.schemas import User
from .exceptions import title_exception
from sqlalchemy import desc
from backend.admin.models import Users


router = APIRouter(
    tags=["Post"],
)

templates = Jinja2Templates(directory="templates", autoescape=False)

CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("/add/post", response_class=HTMLResponse, dependencies=[Depends(get_current_user)])
async def add_post_html(request: Request):
    return templates.TemplateResponse("admin/add_post.html", {"request": request})


@router.post("/add/post", dependencies=[Depends(get_current_user)])
async def add_post(db: DbSession, current_user: CurrentUser, request: Request, title: Optional[str] = Form(None), content: str = Form(...)):
    try:
        if not title:
            raise HTTPException(status_code=422, detail="Tytuł jest wymagany.")
        post = Posts()
        post.title = title
        post.content = content
        post.user_id = current_user.id

        db.add(post)
        db.commit()
        db.refresh(post)
        return '<div id="info><p>Post został dodany</p></div>'
    except HTTPException as e:
        return f'<div id="info"><p>Błąd: {e.detail}</p></div>'
    

@router.get("/admin/news", response_class=HTMLResponse)
async def posts(request: Request, db: DbSession):
    posts = db.query(Posts).order_by(desc(Posts.created_at)).all()
    return templates.TemplateResponse("admin/news_admin.html", {"request": request, "posts": posts})


@router.get("/admin/news/{id}", response_class=HTMLResponse)
async def posts(request: Request, db: DbSession, id: int):
    post = db.query(Posts).filter(Posts.id == id).one_or_none()
    author = db.query(Users).filter(Users.id == post.user_id).one_or_none()
    return templates.TemplateResponse("admin/actual_news_admin.html", {"request": request, "post": post, "author": author})
