from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import ChatMessage, Student, User, get_db
from app.llm.provider import llm_provider
from app.schemas import ChatRequest, ChatResponse, SearchResult
from app.security.auth import get_current_user
from app.security.guards import get_accessible_student, reject_sensitive_question
from app.services.rag_service import search_documents


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def ask(
    payload: ChatRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ChatResponse:
    reject_sensitive_question(payload.question)

    student: Student | None = None
    if payload.student_id is not None:
        student = get_accessible_student(db, payload.student_id, current_user)

    sources = search_documents(db, payload.question, category=payload.category)
    answer = llm_provider.answer(payload.question, sources=sources, student=student)

    db.add(
        ChatMessage(
            user_id=current_user.id,
            student_id=student.id if student else None,
            question=payload.question,
            answer=answer,
        )
    )
    db.commit()

    return ChatResponse(
        answer=answer,
        sources=[SearchResult(**source.__dict__) for source in sources],
    )


@router.get("/history")
def history(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[dict[str, str | int | None]]:
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == current_user.id)
        .order_by(ChatMessage.created_at.desc())
        .limit(25)
        .all()
    )
    return [
        {
            "id": message.id,
            "student_id": message.student_id,
            "question": message.question,
            "answer": message.answer,
            "created_at": message.created_at.isoformat(),
        }
        for message in messages
    ]
