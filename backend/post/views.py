from fastapi import APIRouter, Request, Form, Depends, HTTPException, UploadFile, File
from database import DbSession
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import Annotated, Optional
from backend.admin.services import get_current_user
from .models import Posts
from backend.admin.schemas import User
from sqlalchemy import desc
from backend.admin.models import Users
from config import s3
from math import ceil
from uuid import uuid4
from .exceptions import post_exception, admin_exception
from datetime import datetime
from .services import remove_html_tags
from backend.limiter import limiter

router = APIRouter(
    tags=["Post"],
)


templates = Jinja2Templates(directory="templates", autoescape=False)

CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("/add/post", response_class=HTMLResponse, dependencies=[Depends(get_current_user)])
@limiter.limit("20/minute")
async def add_post_html(request: Request):
    return templates.TemplateResponse("admin/add_post.html", {"request": request})


@router.post("/add/post", dependencies=[Depends(get_current_user)])
@limiter.limit("20/minute")
async def add_post(db: DbSession, current_user: CurrentUser, request: Request, file: Optional[UploadFile] = File(None), title: Optional[str] = Form(None), content: str = Form(...)):
    try:
        if not title or not file:
            raise HTTPException(status_code=422, detail="Tytuł i zdjęcie są wymagane.")
        
        contents = await file.read()
        if len(contents) >= 26214400:
            content = """<p>Plik może mieć maksymalnie 8MB</p>"""
            return HTMLResponse(content=content)
        
        post = Posts()
        post.title = title
        post.content = content
        post.user_id = current_user.id

        while True:
            new_uuid = str(uuid4())
            new_img_url = "https://cyberbucket-s3.s3.eu-north-1.amazonaws.com/" + new_uuid
            existing_post = db.query(Posts).filter_by(img_url=new_img_url).first()
            if not existing_post:
                file.filename = new_uuid
                s3.put_object(Bucket='cyberbucket-s3', Key=file.filename, Body=contents)
                post.img_url = new_img_url
                break

        db.add(post)
        db.commit()
        db.refresh(post)
        
        content = """<p>Artykuł został dodany poprawnie</p>"""
        return HTMLResponse(content=content)
        
    except HTTPException as e:
        content = f'<p><strong>Błąd:</strong> {e.detail}</p>'
        return HTMLResponse(content=content)
  

@router.get("/admin/news/page-{page}", response_class=HTMLResponse,dependencies=[Depends(get_current_user)])
@limiter.limit("20/minute")
async def posts(request: Request, db: DbSession, page: int = 0):
    posts = db.query(Posts).order_by(desc(Posts.created_at)).limit(12).offset((page-1)*12).all()
    if posts is None:
        raise post_exception()
    for post in posts:
        clean_post_content = remove_html_tags(post.content)[:200]
        post.title = post.title[:100]
        post.content = clean_post_content
    pages = ceil(db.query(Posts).count() / 12)
    if pages is None:
        raise post_exception()
    return templates.TemplateResponse("admin/news_admin.html", {"request": request, "posts": posts, "pages": pages, "actual_page": page})


@router.get("/admin/news/{id}", response_class=HTMLResponse, dependencies=[Depends(get_current_user)])
@limiter.limit("20/minute")
async def posts(request: Request, db: DbSession, id: int, current_user: CurrentUser):
    post = db.query(Posts).filter(Posts.id == id).one_or_none()
    author = db.query(Users).filter(Users.id == post.user_id).execution_options(include_deleted=True).one_or_none()

    if author.id == current_user.id or current_user.role_id == 1:
        return templates.TemplateResponse("admin/actual_news_admin.html", {"request": request, "post": post, "author": author, "author_post": True})
    return templates.TemplateResponse("admin/actual_news_admin.html", {"request": request, "post": post, "author": author,"author_post": False})


@router.get("/update/news-{id}", response_class=HTMLResponse, dependencies=[Depends(get_current_user)])
@limiter.limit("20/minute")
async def update_post(request:Request, db: DbSession, id: int):
    post = db.query(Posts).filter(Posts.id == id).one_or_none()
    if post is None:
            raise post_exception()
    return templates.TemplateResponse('admin/edit_post.html', {'request': request, 'post': post })


@router.patch("/update/news-{id}", response_class=HTMLResponse, dependencies=[Depends(get_current_user)])
@limiter.limit("20/minute")
async def update_post(request:Request, db: DbSession, id: int, file: Optional[UploadFile] = File(None), title: Optional[str] = Form(None), content: str = Form(...)):
     try:
        if not title:
            raise HTTPException(status_code=422, detail="Tytuł i zdjęcie są wymagane.")
        
        post = db.query(Posts).filter(Posts.id == id).one_or_none()
        if post is None:
            raise post_exception()

        post.title = title
        post.content = content
        post.updated_at = datetime.utcnow()
        if file:
            contents = await file.read()
            if len(contents) >= 26214400:
                content = """Plik może mieć maksymalnie 8MB"""
                return HTMLResponse(content=content)
            while True:
                new_uuid = str(uuid4())
                new_img_url = "https://cyberbucket-s3.s3.eu-north-1.amazonaws.com/" + new_uuid
                existing_post = db.query(Posts).filter_by(img_url=new_img_url).first()
                if not existing_post:
                    file.filename = new_uuid
                    s3.put_object(Bucket='cyberbucket-s3', Key=file.filename, Body=contents)
                    post.img_url = new_img_url
                    break


        db.commit()
        db.refresh(post)

        redirect = templates.TemplateResponse('main.html', {'request': request})
        redirect.headers['HX-Redirect'] = f"/admin/news/{post.id}"
        return redirect
     except HTTPException as e:
        content = f'Błąd: {e.detail}'
        return HTMLResponse(content=content)
     

@router.delete("/post-{id}", dependencies=[Depends(get_current_user)])
@limiter.limit("20/minute")
async def delete_post(request:Request, db: DbSession, id: int, current_user: CurrentUser):
    post = db.query(Posts).filter(Posts.id == id).one_or_none()
    if post.user_id != current_user.id:
        raise admin_exception()
    if post is None:
        raise post_exception()
    db.delete(post)
    db.commit()

    redirect = templates.TemplateResponse('main.html', {'request': request})
    redirect.headers['HX-Redirect'] = f"/admin/news/page-1"
    return redirect
