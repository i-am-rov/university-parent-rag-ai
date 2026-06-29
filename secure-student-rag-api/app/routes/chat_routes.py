from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import ChatMessage, User, get_db
from app.llm.sql_generator import generate_sql
from app.schemas import ChatRequest, ChatResponse
from app.security.jwt_handler import get_current_user
from app.security.student_scope_guard import get_scoped_student_for_user


router = APIRouter(tags=["chat"])


@router.post("/api/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ChatResponse:
    student = get_scoped_student_for_user(db, current_user)
    generated_sql = generate_sql(request.question)
    answer = f"Generated SQL for {student.student_id}:\n{generated_sql}\n\nSQL was not executed."
    db.add(
        ChatMessage(
            user_id=current_user.id,
            student_id=student.id,
            question=request.question,
            answer=answer,
        )
    )
    db.commit()
    return ChatResponse(answer=answer)
