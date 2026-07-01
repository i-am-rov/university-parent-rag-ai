from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import ChatMessage, User, get_db
from app.llm.answer_generator import answer_from_rows
from app.llm.sql_generator import generate_sql
from app.schemas import ChatRequest, ChatResponse
from app.security.jwt_handler import get_current_user
from app.security.student_scope_guard import get_scoped_student_for_user
from app.services.sql_executor import execute_student_sql


router = APIRouter(tags=["chat"])


@router.post("/api/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ChatResponse:
    student = get_scoped_student_for_user(db, current_user)
    generated_sql = generate_sql(request.question)
    rows = execute_student_sql(db, generated_sql, student.student_id)
    answer = answer_from_rows(request.question, generated_sql, rows, student)
    db.add(
        ChatMessage(
            user_id=current_user.id,
            student_id=student.id,
            question=request.question,
            answer=answer,
        )
    )
    db.commit()
    return ChatResponse(answer=answer, generated_sql=generated_sql, rows=rows)
