from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.database import Student, User
from app.schemas import UserCreate
from app.security.password_utils import hash_password, verify_password


def create_user(db: Session, payload: UserCreate) -> User:
    email = payload.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        email=email,
        full_name=payload.full_name,
        role=payload.role,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_parent(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email.lower()).first()
    if user is None or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
    if user.role != "parent":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only parent login is allowed here")
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email.lower()).first()
    if user is None or not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


def get_linked_student_for_parent(db: Session, parent: User) -> Student:
    if parent.role != "parent":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Logged-in user is not a parent")

    student = db.query(Student).filter(Student.guardian_id == parent.id).order_by(Student.id).first()
    if student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No student is linked to this parent")
    return student


def get_student_for_user(db: Session, user: User) -> Student:
    if user.role == "parent":
        return get_linked_student_for_parent(db, user)

    student = db.query(Student).order_by(Student.id).first()
    if student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return student
