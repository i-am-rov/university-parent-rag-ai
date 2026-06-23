from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse


router = APIRouter(tags=["pages"])

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def html_page(filename: str) -> FileResponse:
    return FileResponse(TEMPLATES_DIR / filename, media_type="text/html")


@router.get("/")
def index() -> FileResponse:
    return html_page("index.html")


@router.get("/login")
def login() -> FileResponse:
    return html_page("login.html")


@router.get("/dashboard")
def dashboard() -> FileResponse:
    return html_page("dashboard.html")


@router.get("/chat")
def chat() -> FileResponse:
    return html_page("chat.html")
