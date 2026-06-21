import re

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.database import Student, User


SENSITIVE_PATTERNS = [
    re.compile(r"\b(password|secret|token|api[_ -]?key)\b", re.IGNORECASE),
    re.compile(r"\b(all students|everyone|full database|dump)\b", re.IGNORECASE),
]


def reject_sensitive_question(question: str) -> None:
    if any(pattern.search(question) for pattern in SENSITIVE_PATTERNS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question asks for sensitive or broad private data.",
        )


def get_accessible_student(db: Session, student_pk: int, user: User) -> Student:
    student = db.get(Student, student_pk)
    if student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    if user.role == "admin":
        return student
    if student.guardian_id == user.id:
        return student
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Student is outside your access scope")
