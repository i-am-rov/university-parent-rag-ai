from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import Student, User, get_db
from app.schemas import StudentCreate, StudentRead
from app.security.auth import get_current_user, require_roles
from app.security.guards import get_accessible_student
from app.services.student_service import create_student


router = APIRouter(prefix="/students", tags=["students"])


@router.post("", response_model=StudentRead)
def add_student(
    payload: StudentCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles("admin", "parent"))],
) -> Student:
    return create_student(db, payload, current_user)


@router.get("", response_model=list[StudentRead])
def list_students(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[Student]:
    if current_user.role == "admin":
        return db.query(Student).order_by(Student.full_name).all()
    return db.query(Student).filter(Student.guardian_id == current_user.id).order_by(Student.full_name).all()


@router.get("/{student_pk}", response_model=StudentRead)
def get_student(
    student_pk: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Student:
    return get_accessible_student(db, student_pk, current_user)
