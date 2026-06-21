from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.database import Student, User
from app.schemas import StudentCreate


def create_student(db: Session, payload: StudentCreate, current_user: User) -> Student:
    existing = db.query(Student).filter(Student.student_id == payload.student_id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Student ID already exists")

    guardian_id: int | None = None
    if payload.guardian_email:
        guardian = db.query(User).filter(User.email == payload.guardian_email.lower()).first()
        if guardian is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guardian user not found")
        guardian_id = guardian.id
    elif current_user.role == "parent":
        guardian_id = current_user.id

    student = Student(
        student_id=payload.student_id,
        full_name=payload.full_name,
        department=payload.department,
        semester=payload.semester,
        guardian_id=guardian_id,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student
