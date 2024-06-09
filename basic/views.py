from fastapi import APIRouter, Request
from sqlalchemy import desc
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from database import DbSession
from backend.post.models import Posts
from backend.admin.models import Users
from .services import image_base64
from math import ceil
from backend.post.services import remove_html_tags
from .exceptions import post_exception


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
    if posts is None:
        raise post_exception()
    for post in posts:
        clean_post_content = remove_html_tags(post.content)[:200]
        post.title = post.title[:100]
        post.content = clean_post_content
    pages = ceil(db.query(Posts).count() / 12)
    if pages is None:
        raise post_exception()
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


@router.get("/map", response_class=HTMLResponse)
async def mapa(request: Request):
    return templates.TemplateResponse("subpages/map.html", {"request": request})


@router.get("/map-actor-country", response_class=HTMLResponse)
async def map_actor_country(request: Request):
    content = '''<iframe id="map" src="/static/map2/map-actor-country.html" width="80%" height="500px"></iframe>'''
    return HTMLResponse(content=content)


@router.get("/map-motive", response_class=HTMLResponse)
async def map_actor_country(request: Request):
    content = '''<iframe id="map" src="/static/map2/map-motive.html" width="80%" height="500px"></iframe>'''
    return HTMLResponse(content=content)


@router.get("/map-type", response_class=HTMLResponse)
async def map_actor_country(request: Request):
    content = '''<iframe id="map" src="/static/map2/map-type.html" width="80%" height="500px"></iframe>'''
    return HTMLResponse(content=content)


@router.get("/links", response_class=HTMLResponse)
async def links(request: Request):
    return templates.TemplateResponse("subpages/links.html", {"request": request})


@router.get("/open-navbar")
async def open_navbar():
    return FileResponse("templates/htmx/open-navbar.html")


@router.get("/close-navbar")
async def close_navbar():
    return FileResponse("templates/htmx/close-navbar.html")


@router.get('/phishing')
async def phishing():
    return FileResponse("templates/htmx/phishing.html")


@router.get('/malware')
async def malware():   
    return FileResponse("templates/htmx/malware.html")


@router.get('/ddos')
async def ddos():
    return FileResponse("templates/htmx/ddos.html")


@router.get('/mitm')
async def mitm():
    return FileResponse("templates/htmx/mitm.html")


@router.get('/sql')
async def sql():
    return FileResponse("templates/htmx/sql.html")


@router.get('/zero-day')
async def zero_day():
    return FileResponse("templates/htmx/zero-day.html")
