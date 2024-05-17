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


@router.get("/open-navbar")
async def open_navbar():
    content = '''<header>
      <h1 class="mainPage"><a href="/">Bezpieczni</a></h1>
      <div class="menu">
        <a href="/cyberattacks">Cyber Ataki</a>
        <a href="/news/page-1" id="activeLink">Aktualności</a>
        <a href="/analysis">Analiza</a>
        <a href="/map">Mapa</a>
        <a href="/links">Linki</a>
      </div>
      <div
        class="menu2"
        hx-get="/close-navbar"
        hx-swap="outerHTML"
        hx-target="header"
        hx-on:click="document.getElementById('navbar').remove()"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="30"
          height="30"
          fill="currentColor"
          class="bi bi-list"
          viewBox="0 0 16 16"
        >
          <path
            fill-rule="evenodd"
            d="M2.5 12a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5m0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5m0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5"
          />
        </svg>
      </div>
    </header>
    <div id="navbar"><a href="/cyberattacks">Cyber Ataki</a>
        <a href="/news/page-1">Aktualności</a>
        <a href="/analysis">Analiza</a>
        <a href="/map">Mapa</a>
        <a href="/links">Linki</a></div>'''
    return (HTMLResponse(content=content))


@router.get("/close-navbar")
async def close_navbar():
    content = '''<header>
      <h1 class="mainPage"><a href="/">Bezpieczni</a></h1>
      <div class="menu">
        <a href="/cyberattacks">Cyber Ataki</a>
        <a href="/news/page-1" id="activeLink">Aktualności</a>
        <a href="/analysis">Analiza</a>
        <a href="/map">Mapa</a>
        <a href="/links">Linki</a>
      </div>
      <div
        class="menu2"
        hx-get="/open-navbar"
        hx-swap="outerHTML"
        hx-target="header"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="30"
          height="30"
          fill="currentColor"
          class="bi bi-list"
          viewBox="0 0 16 16"
        >
          <path
            fill-rule="evenodd"
            d="M2.5 12a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5m0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5m0-4a.5.5 0 0 1 .5-.5h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5"
          />
        </svg>
      </div>
    </header>'''
    return (HTMLResponse(content=content))


@router.get('/phishing')
async def phishing():
    content = '''<div id="attack-type"><div><h3>Phishing</h3>
    <img
          src="https://cyberbucket-s3.s3.eu-north-1.amazonaws.com/cyberattacks-types.jpeg"
          alt="Phishing"
          /></div>
    <p>Phishing to jedna z najczęstszych i najbardziej podstępnych form cyberataków. Jego celem jest oszukanie użytkowników i skłonienie ich do ujawnienia wrażliwych informacji, takich jak hasła, numery kart kredytowych czy inne dane osobowe. Ataki phishingowe są zwykle przeprowadzane za pomocą fałszywych e-maili, wiadomości SMS, czy stron internetowych, które na pierwszy rzut oka wyglądają na wiarygodne i pochodzące od zaufanych źródeł.</p>
       </div> '''
    return HTMLResponse(content=content)

@router.get('/malware')
async def malware():
    content = '''<div id="attack-type"><div><h3>Malware</h3>
    <img
          src="https://cyberbucket-s3.s3.eu-north-1.amazonaws.com/malware.jpeg"
          alt="Malware"
        /> </div>
    <p>Malware to skrót od "malicious software" (złośliwe oprogramowanie), które jest zaprojektowane w celu uszkodzenia, zakłócenia, kradzieży lub ogólnego przejęcia kontroli nad systemami komputerowymi, sieciami, tabletami i telefonami komórkowymi. Malware może przybierać wiele form, w tym wirusy, robaki, konie trojańskie, ransomware, spyware i adware. Malware jest nieustannym zagrożeniem w cyfrowym świecie, ale poprzez stosowanie odpowiednich środków ostrożności i utrzymanie systemów zabezpieczeń, można znacznie zmniejszyć ryzyko infekcji.</p>
       </div> 
       <div id="about-type">
       <div>
       <h4>Wirusy</h4>
          <p>Programy, które przyczepiają się do zdrowych plików i programów oraz rozprzestrzeniają się na inne pliki. Wymagają one działania użytkownika, aby mogły się aktywować, takie jak otwarcie zainfekowanego pliku.</p>
        </div>
        <div>
       <h4>Robaki</h4>
          <p>Samoreplikujące się programy, które rozprzestrzeniają się bez interwencji użytkownika, często przez sieci.Mogą powodować przeciążenie sieci i systemów, co prowadzi do spowolnienia ich działania lub całkowitego wyłączenia.</p>
        </div>
        <div>
       <h4>Konie trojańskie</h4>
          <p>Programy, które podszywają się pod legalne oprogramowanie, ale wykonują złośliwe działania po ich zainstalowaniu. Mogą otwierać tylnie drzwi (backdoors) dla innych malware, kraść dane lub przejmować kontrolę nad systemem.</p>
        </div>
        <div>
       <h4>Ransomware</h4>
          <p>Oprogramowanie, które szyfruje dane na komputerze ofiary i żąda okupu za ich odszyfrowanie. Blokuje dostęp do ważnych plików i danych, żądając zapłaty, zwykle w kryptowalutach, w zamian za klucz deszyfrujący.</p>
        </div>
        <div>
       <h4>Spyware</h4>
          <p>Oprogramowanie, które potajemnie śledzi aktywność użytkownika i zbiera informacje bez jego wiedzy. Może rejestrować naciśnięcia klawiszy (keylogging), przechwytywać dane logowania i monitorować przeglądane strony internetowe.</p>
        </div>
        <div>
       <h4>Adware</h4>
          <p>Oprogramowanie, które wyświetla niechciane reklamy na urządzeniu użytkownika. Może śledzić nawyki przeglądania w celu wyświetlania ukierunkowanych reklam, a czasem prowadzić do innych form malware.</p>
        </div>
       </div>
       '''
    return HTMLResponse(content=content)