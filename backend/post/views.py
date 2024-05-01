from fastapi import APIRouter, Request, Response, Form, Depends
from database import DbSession
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse
from starlette import status
from typing import Annotated
from backend.admin.services import get_current_user
from .models import Posts
from backend.admin.schemas import User


router = APIRouter(
    tags=["Post"],
)

templates = Jinja2Templates(directory="templates")

CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("/add/post", response_class=HTMLResponse, dependencies=[Depends(get_current_user)])
async def add_post_html(request: Request):
    return templates.TemplateResponse("admin/add_post.html", {"request": request})


@router.post("/add/post", dependencies=[Depends(get_current_user)])
async def add_post(db: DbSession, current_user: CurrentUser, request: Request, title: str = Form(...), content: str = Form(...)):
    post = Posts()
    post.title = title
    post.content = content
    post.user_id = current_user.id

    db.add(post)
    db.commit()
    db.refresh(post)

    return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
