from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import User, get_db
from app.schemas import StudentCourseRead, StudentExamRead, StudentFeeRead, StudentProfile
from app.security.jwt_handler import get_current_user
from app.services import student_data_service


router = APIRouter(prefix="/api/student", tags=["student"])


@router.get("/profile", response_model=StudentProfile)
def profile(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return student_data_service.get_profile(db, current_user)


@router.get("/fees", response_model=list[StudentFeeRead])
def fees(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return student_data_service.get_fees(db, current_user)


@router.get("/courses", response_model=list[StudentCourseRead])
def courses(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return student_data_service.get_courses(db, current_user)


@router.get("/exams", response_model=list[StudentExamRead])
def exams(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    return student_data_service.get_exams(db, current_user)
