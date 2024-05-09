from fastapi import APIRouter, Request, Response, Form, Depends
from database import DbSession
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse
from starlette import status
from .services import hash_password, get_by_email, generate_random_password, get_current_user
from ..general.send_email import simple_send
from .exception import get_user_exist_exception
from .models import Users
from config import settings


router = APIRouter(
    tags=["Admin"]
)

templates = Jinja2Templates(directory="templates")


@router.get("/dashboard", response_class=HTMLResponse, dependencies=[Depends(get_current_user)])
async def admin_page(request: Request):
    return templates.TemplateResponse("admin/dashboard.html", {"request": request})


@router.get("/register", response_class=HTMLResponse)
async def register_html(request: Request):
    return templates.TemplateResponse("admin/register.html", {"request": request})


@router.post("/register")
async def register(db: DbSession, 
                   name: str = Form(...), 
                   surname: str = Form(...), 
                   email: str = Form(...), 
                   role: int = Form(...)):
    if get_by_email(db=db, email=email):
        return """<div id="info">Użytkownik o tym e-mailu już istnieje! Użyj innego e-maila.</div>"""
    
    random_password = generate_random_password()
    password = hash_password(random_password)

    user = get_by_email(db=db, email=email, include_deleted=True)
    if user:
        if user.deleted_at is not None:
            user.undelete()
            user.role = role
            user.password = password
            db.commit()
            db.refresh(user)
            await simple_send([user_in.email], random_password)
            return """<div id=info>Zarejestrowano.</div>"""
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

    return """<div id=info>Zarejestrowano.</div>"""



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
