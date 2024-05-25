from fastapi import APIRouter, Request, Response, Form, Depends
from typing import Annotated
from database import DbSession
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from starlette.responses import RedirectResponse
from starlette import status
from .services import hash_password, get_by_email, generate_random_password, get_current_user, get_current_admin
from ..general.send_email import simple_send
from .exception import get_user_exist_exception
from .models import Users
from ..post.models import Posts
from ..post.views import CurrentUser
from config import settings


router = APIRouter(
    tags=["Admin"]
)

templates = Jinja2Templates(directory="templates")



@router.get("/dashboard", response_class=HTMLResponse, dependencies=[Depends(get_current_user)])
async def admin_page(request: Request, db: DbSession, current_user: CurrentUser,):
    posts_number = db.query(Posts).count()
    my_posts_number = db.query(Posts).filter(Posts.user_id == current_user.id).count()
    if current_user.role_id == 1:
        return templates.TemplateResponse("admin/dashboard.html", {"request": request, "posts_number" : posts_number, "my_posts_number": my_posts_number, "admin": True})
    return templates.TemplateResponse("admin/dashboard.html", {"request": request, "posts_number" : posts_number, "my_posts_number": my_posts_number})


@router.get("/login", response_class=HTMLResponse)
async def login_html(request: Request):
    return templates.TemplateResponse("admin/login.html", {"request": request})
    

@router.post("/login")
async def login(db: DbSession, email: str = Form(...), password: str = Form(...)):
    user = Users()
    user.email = email
    user.password = password
    user = get_by_email(db=db, email=user.email)

    if not user or not user.check_password(password):
        content = "<p>Blędne hasło lub email.</p>"
        return HTMLResponse(content=content)
    
    redirect = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

    redirect.set_cookie(
        key="jwt",
        value=user.refresh_token,
        httponly=True,
        # secure=True,
        samesite=None,
        max_age=60 * 60 * settings.refresh_token_expire_hours,
    )

    return redirect


@router.get("/logout", response_class=HTMLResponse, dependencies=[Depends(get_current_user)])
async def logout(response: Response, request: Request):
    redirect = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    redirect.delete_cookie(key="jwt")
    return redirect



@router.get("/open-navbar-admin", dependencies=[Depends(get_current_user)])
async def open_navbar():
    return FileResponse("templates/htmx/open-navbar-admin.html")
    

@router.get("/close-navbar-admin", dependencies=[Depends(get_current_user)])
async def close_navbar():
    return FileResponse("templates/htmx/close-navbar-admin.html")

@router.get("/register", response_class=HTMLResponse, dependencies=[Depends(get_current_admin)])
async def register_html(request: Request):
    return templates.TemplateResponse("admin/register.html", {"request": request})


@router.post("/register", dependencies=[Depends(get_current_admin)])
async def register(db: DbSession, 
                   name: str = Form(...), 
                   surname: str = Form(...), 
                   email: str = Form(...), 
                   role: int = Form(...)):
    if get_by_email(db=db, email=email):
        content = '''<p>Użytkownik o tym e-mailu już istnieje! Użyj innego e-maila.</p>'''
        return HTMLResponse(content=content)
    
    random_password = generate_random_password()
    password = hash_password(random_password)

    user = get_by_email(db=db, email=email, include_deleted=True)
    if user:
        if user.deleted_at is not None:
            user.undelete()
            user.name = name
            user.surname = surname
            user.role_id = role
            user.password = password
            db.commit()
            db.refresh(user)
            await simple_send([user.email], random_password)
            content = '''<p>Zarejestrowano.</p>'''
            return HTMLResponse(content=content)
        raise get_user_exist_exception()

    user_in = Users()
    user_in.name = name
    user_in.surname = surname
    user_in.email = email
    user_in.role_id = role
    user_in.password = password

    db.add(user_in)
    db.commit()
    db.refresh(user_in)

    await simple_send([user_in.email], random_password)
    content =  '''<p>Zarejestrowano.</p>'''
    return HTMLResponse(content=content)


@router.get("/user-list", dependencies=[Depends(get_current_admin)])
async def user_list(request: Request, db: DbSession):
    users = db.query(Users).all()
    return templates.TemplateResponse("htmx/user-list.html", {"request": request, "users": users})


@router.get("/edit-user/{id}", dependencies=[Depends(get_current_user)])
async def edit_user(request: Request, db: DbSession, id: int):
    user = db.query(Users).filter(Users.id == id).one_or_none()
    if user.role_id != 1:
        return HTMLResponse(status_code=401)
    if user is None:
        raise get_user_exist_exception()
    return templates.TemplateResponse("htmx/update-user.html", {"request": request, "user": user})
    


@router.patch("/user/{id}", dependencies=[Depends(get_current_admin)])
async def update_user(db: DbSession, id: int,name: str = Form(...), 
                   surname: str = Form(...), 
                   email: str = Form(...), 
                   role: int = Form(...), change_password: bool = Form(False)):
    user = db.query(Users).filter(Users.id == id).one_or_none()
    if not user:
        raise get_user_exist_exception()
    
    user.name = name
    user.surname = surname
    user.email = email
    user.role_id = role
    if change_password:
        print('tak')
        random_password = generate_random_password()
        password = hash_password(random_password)
        user.password = password
        await simple_send([user.email], random_password)
        db.commit()
        db.refresh(user)
        content =  '''<p>Zaaktualizowano dane.</p>'''
        return HTMLResponse(content=content)
    db.commit()
    db.refresh(user)
    content =  '''<p>Zaaktualizowano dane.</p>'''
    return HTMLResponse(content=content)


@router.delete("/user/{id}", dependencies=[Depends(get_current_admin)])
async def delete_user(db: DbSession, id: int):
    user = db.query(Users).filter(Users.id == id).one_or_none()

    if user is None:
        raise get_user_exist_exception()

    user.delete()
    db.commit()
    return HTMLResponse(status_code=200)

