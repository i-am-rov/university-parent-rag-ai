from sqlalchemy.orm import Session

from app.database import Student, StudentCourse, StudentExam, StudentFee, User
from app.services.auth_service import get_student_for_user


def get_profile(db: Session, current_user: User) -> Student:
    return get_student_for_user(db, current_user)


def get_fees(db: Session, current_user: User) -> list[StudentFee]:
    student = get_student_for_user(db, current_user)
    return (
        db.query(StudentFee)
        .filter(StudentFee.student_pk == student.id)
        .order_by(StudentFee.due_date.desc())
        .all()
    )


def get_courses(db: Session, current_user: User) -> list[StudentCourse]:
    student = get_student_for_user(db, current_user)
    return (
        db.query(StudentCourse)
        .filter(StudentCourse.student_pk == student.id)
        .order_by(StudentCourse.code)
        .all()
    )


def get_exams(db: Session, current_user: User) -> list[StudentExam]:
    student = get_student_for_user(db, current_user)
    return (
        db.query(StudentExam)
        .filter(StudentExam.student_pk == student.id)
        .order_by(StudentExam.exam_date)
        .all()
    )
