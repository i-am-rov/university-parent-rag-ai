from sqlalchemy.orm import Session

from app.database import Student, StudentCourse, StudentExam, StudentFee, User
from app.security.student_scope_guard import filter_query_to_student_scope, get_scoped_student_for_user


def get_profile(db: Session, current_user: User) -> Student:
    return get_scoped_student_for_user(db, current_user)


def get_fees(db: Session, current_user: User) -> list[StudentFee]:
    student = get_scoped_student_for_user(db, current_user)
    query = filter_query_to_student_scope(db.query(StudentFee), StudentFee, student)
    return query.order_by(StudentFee.due_date.desc()).all()


def get_courses(db: Session, current_user: User) -> list[StudentCourse]:
    student = get_scoped_student_for_user(db, current_user)
    query = filter_query_to_student_scope(db.query(StudentCourse), StudentCourse, student)
    return query.order_by(StudentCourse.code).all()


def get_exams(db: Session, current_user: User) -> list[StudentExam]:
    student = get_scoped_student_for_user(db, current_user)
    query = filter_query_to_student_scope(db.query(StudentExam), StudentExam, student)
    return query.order_by(StudentExam.exam_date).all()
