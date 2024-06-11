from fastapi import APIRouter, Request
from sqlalchemy import desc
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from database import DbSession
from backend.post.models import Posts
from backend.admin.models import Users
from math import ceil
from backend.post.services import remove_html_tags
from .exceptions import post_exception
from backend.limiter import limiter
from markupsafe import escape

router = APIRouter(
    tags=["basic"]
)


templates = Jinja2Templates(directory="templates", autoescape=False)


@router.get("/", response_class=HTMLResponse)
@limiter.limit("20/minute")
async def main_page(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})


@router.get("/cyberattacks", response_class=HTMLResponse)
@limiter.limit("20/minute")
async def cyberattacks_page(request: Request):
    return templates.TemplateResponse("subpages/cyber_attacks.html", {"request": request})


@router.get("/news/page-{page}", response_class=HTMLResponse)
@limiter.limit("20/minute")
async def posts(request: Request, db: DbSession, page: int = 0):
    posts = db.query(Posts).order_by(desc(Posts.created_at)).limit(12).offset((page-1)*12).all()
    if posts is None:
        raise post_exception()
    for post in posts:
        clean_post_content = remove_html_tags(post.content)[:200]
        post.title = escape(post.title[:100])
        post.content = clean_post_content
    pages = ceil(db.query(Posts).count() / 12)
    if pages is None:
        raise post_exception()
    return templates.TemplateResponse("subpages/news.html", {"request": request, "posts": posts, "pages": pages, "actual_page": page})


@router.get("/news/{id}", response_class=HTMLResponse)
@limiter.limit("20/minute")
async def posts(request: Request, db: DbSession, id: int):
    post = db.query(Posts).filter(Posts.id == id).one_or_none()
    if posts is None:
        raise post_exception()
    author = db.query(Users).filter(Users.id == post.user_id).execution_options(include_deleted=True).one_or_none()
    post.title = escape(post.title)
    post.content = post.content
    return templates.TemplateResponse("subpages/actual_news.html", {"request": request, "post": post, "author": author})


@router.get("/analysis", response_class=HTMLResponse)
@limiter.limit("20/minute")
async def analysis_page(request: Request):

    return templates.TemplateResponse("subpages/analysis.html", {"request": request})


@router.get("/map", response_class=HTMLResponse)
@limiter.limit("20/minute")
async def mapa(request: Request):
    return templates.TemplateResponse("subpages/map.html", {"request": request})


@router.get("/map-actor-country", response_class=HTMLResponse)
@limiter.limit("20/minute")
async def map_actor_country(request: Request):
    content = '''<iframe id="map" src="/static/map2/map-actor-country.html" width="80%" height="500px"></iframe>'''
    return HTMLResponse(content=content)


@router.get("/map-motive", response_class=HTMLResponse)
@limiter.limit("20/minute")
async def map_actor_country(request: Request):
    content = '''<iframe id="map" src="/static/map2/map-motive.html" width="80%" height="500px"></iframe>'''
    return HTMLResponse(content=content)


@router.get("/map-type", response_class=HTMLResponse)
@limiter.limit("20/minute")
async def map_actor_country(request: Request):
    content = '''<iframe id="map" src="/static/map2/map-type.html" width="80%" height="500px"></iframe>'''
    return HTMLResponse(content=content)


@router.get("/links", response_class=HTMLResponse)
@limiter.limit("20/minute")
async def links(request: Request):
    return templates.TemplateResponse("subpages/links.html", {"request": request})


@router.get("/open-navbar")
@limiter.limit("20/minute")
async def open_navbar(request: Request):
    return FileResponse("templates/htmx/open-navbar.html")


@router.get("/close-navbar")
@limiter.limit("20/minute")
async def close_navbar(request: Request):
    return FileResponse("templates/htmx/close-navbar.html")


@router.get('/phishing')
@limiter.limit("20/minute")
async def phishing(request: Request):
    return FileResponse("templates/htmx/phishing.html")


@router.get('/malware')
@limiter.limit("20/minute")
async def malware(request: Request):   
    return FileResponse("templates/htmx/malware.html")


@router.get('/ddos')
@limiter.limit("20/minute")
async def ddos(request: Request):
    return FileResponse("templates/htmx/ddos.html")


@router.get('/mitm')
@limiter.limit("20/minute")
async def mitm(request: Request):
    return FileResponse("templates/htmx/mitm.html")


@router.get('/sql')
@limiter.limit("20/minute")
async def sql(request: Request):
    return FileResponse("templates/htmx/sql.html")


@router.get('/zero-day')
@limiter.limit("20/minute")
async def zero_day(request: Request):
    return FileResponse("templates/htmx/zero-day.html")


@router.get('/most-actor-country')
@limiter.limit("20/minute")
async def most_actor_country(request: Request):
    return FileResponse("templates/htmx/most_actor_country.html")


@router.get('/most-attacked-country')
@limiter.limit("20/minute")
async def most_attacked_country(request: Request):
    return FileResponse("templates/htmx/most_attacked_country.html")


@router.get('/most-actor-country-poland')
@limiter.limit("20/minute")
async def most_actor_country_poland(request: Request):
    return FileResponse("templates/htmx/most_actor_country_poland.html")


@router.get('/cyber-attack-actor-types')
@limiter.limit("20/minute")
async def cyber_attack_actor_types(request: Request):
    return FileResponse("templates/htmx/cyber_attack_actor_types.html")


@router.get('/cyber-attack-motives')
@limiter.limit("20/minute")
async def cyber_attack_motives(request: Request):
    return FileResponse("templates/htmx/cyber_attack_motives.html")


@router.get('/cyber-attack-event-types')
@limiter.limit("20/minute")
async def cyber_attack_event_types(request: Request):
    return FileResponse("templates/htmx/cyber_attack_event_types.html")


@router.get('/cyber-attack-motives-poland')
@limiter.limit("20/minute")
async def cyber_attack_motives_poland(request: Request):
    return FileResponse("templates/htmx/cyber_attack_motives_poland.html")


@router.get('/number-of-events')
@limiter.limit("20/minute")
async def number_of_events(request: Request):
    return FileResponse("templates/htmx/number_of_events_by_year.html")


@router.get('/summary')
@limiter.limit("20/minute")
async def summary(request: Request):
    return FileResponse("templates/htmx/summary.html")