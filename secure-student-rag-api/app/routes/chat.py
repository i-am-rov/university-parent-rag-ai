from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import ChatMessage, User, get_db
from app.schemas import ChatRequest, ChatResponse
from app.security.auth import get_current_user


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def ask(payload: ChatRequest) -> ChatResponse:
    return ChatResponse(answer="This is a test answer from backend.")


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
