from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.database import SessionLocal, get_settings, init_db
from app.routes import auth, chat, documents, health, pages, students
from app.services.seed_service import seed_demo_data


settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    db: Session = SessionLocal()
    try:
        seed_demo_data(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Secure student-scoped retrieval augmented generation API.",
    lifespan=lifespan,
)

allowed_origins = [origin.strip() for origin in settings.allowed_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(pages.router)
app.include_router(health.router)
app.include_router(auth.router, prefix="/api")
app.include_router(students.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
