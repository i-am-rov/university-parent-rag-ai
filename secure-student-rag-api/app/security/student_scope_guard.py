from fastapi import HTTPException, status
from sqlalchemy.orm import Query, Session

from app.database import Student, User


def get_linked_student_for_parent(db: Session, parent_id: int) -> Student:
    student = db.query(Student).filter(Student.guardian_id == parent_id).order_by(Student.id).first()
    if student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No student is linked to this parent")
    return student


def get_scoped_student_for_user(db: Session, user: User) -> Student:
    if user.role == "parent":
        return get_linked_student_for_parent(db, user.id)

    student = db.query(Student).order_by(Student.id).first()
    if student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return student


def ensure_parent_can_access_student(db: Session, parent_id: int, student_pk: int) -> Student:
    student = get_linked_student_for_parent(db, parent_id)
    if student.id != student_pk:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Student is outside parent scope")
    return student


def filter_query_to_student_scope(query: Query, model, student: Student) -> Query:
    if not hasattr(model, "student_pk"):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Model has no student scope column")
    return query.filter(model.student_pk == student.id)
