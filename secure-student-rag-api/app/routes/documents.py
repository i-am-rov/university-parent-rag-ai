from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import KnowledgeDocument, User, get_db
from app.schemas import DocumentCreate, DocumentRead, SearchResult
from app.security.auth import require_roles
from app.services.rag_service import search_documents


router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentRead)
def create_document(
    payload: DocumentCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles("admin"))],
) -> KnowledgeDocument:
    document = KnowledgeDocument(**payload.model_dump())
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.get("", response_model=list[DocumentRead])
def list_documents(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles("admin"))],
) -> list[KnowledgeDocument]:
    return db.query(KnowledgeDocument).order_by(KnowledgeDocument.created_at.desc()).all()


@router.get("/search", response_model=list[SearchResult])
def search(
    q: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles("admin", "parent", "student"))],
    category: str | None = None,
) -> list[SearchResult]:
    return [SearchResult(**result.__dict__) for result in search_documents(db, q, category=category)]
