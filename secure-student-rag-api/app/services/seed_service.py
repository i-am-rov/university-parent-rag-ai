from datetime import date

from sqlalchemy.orm import Session

from app.database import KnowledgeDocument, Student, StudentCourse, StudentExam, StudentFee, User
from app.security.password_utils import hash_password


def seed_demo_data(db: Session) -> None:
    parent = db.query(User).filter(User.email == "parent@example.com").first()
    if parent is None:
        admin = User(
            email="admin@example.com",
            full_name="Demo Admin",
            role="admin",
            hashed_password=hash_password("AdminPass123"),
        )
        parent = User(
            email="parent@example.com",
            full_name="Demo Parent",
            role="parent",
            hashed_password=hash_password("ParentPass123"),
        )
        db.add_all([admin, parent])
        db.flush()

    student = db.query(Student).filter(Student.student_id == "STU-1001").first()
    if student is None:
        student = Student(
            student_id="STU-1001",
            full_name="Ayesha Rahman",
            department="Computer Science",
            semester="Spring 2026",
            guardian_id=parent.id,
        )
        db.add(student)
        db.flush()

    if not db.query(KnowledgeDocument).first():
        docs = [
            KnowledgeDocument(
                title="Tuition Payment Policy",
                category="fees",
                content=(
                    "Tuition invoices are published before each semester. Parents can pay through the "
                    "student portal, bank transfer, or campus accounts office. Late fees may apply after "
                    "the published deadline."
                ),
            ),
            KnowledgeDocument(
                title="Exam Attendance Rules",
                category="exams",
                content=(
                    "Students must carry a valid ID card and arrive at least 20 minutes before an exam. "
                    "Make-up exams require department approval and documented justification."
                ),
            ),
            KnowledgeDocument(
                title="Academic Advising",
                category="advising",
                content=(
                    "Students should meet their assigned academic advisor before registration. Advisors "
                    "help review course load, prerequisite completion, and academic progress."
                ),
            ),
        ]
        db.add_all(docs)

    if not db.query(StudentFee).filter(StudentFee.student_pk == student.id).first():
        db.add_all(
            [
                StudentFee(
                    student_pk=student.id,
                    semester="Spring 2026",
                    total_amount=52000,
                    paid_amount=35000,
                    due_amount=17000,
                    status="partial",
                    due_date=date(2026, 7, 15),
                ),
                StudentFee(
                    student_pk=student.id,
                    semester="Fall 2025",
                    total_amount=50000,
                    paid_amount=50000,
                    due_amount=0,
                    status="paid",
                    due_date=date(2025, 12, 10),
                ),
            ]
        )

    if not db.query(StudentCourse).filter(StudentCourse.student_pk == student.id).first():
        db.add_all(
            [
                StudentCourse(
                    student_pk=student.id,
                    code="CSE-201",
                    title="Data Structures",
                    credit=3,
                    teacher="Dr. Nadia Islam",
                    semester="Spring 2026",
                ),
                StudentCourse(
                    student_pk=student.id,
                    code="CSE-205",
                    title="Database Systems",
                    credit=3,
                    teacher="Prof. Hasan Karim",
                    semester="Spring 2026",
                ),
                StudentCourse(
                    student_pk=student.id,
                    code="MAT-210",
                    title="Discrete Mathematics",
                    credit=3,
                    teacher="Dr. Farhana Ahmed",
                    semester="Spring 2026",
                ),
            ]
        )

    if not db.query(StudentExam).filter(StudentExam.student_pk == student.id).first():
        db.add_all(
            [
                StudentExam(
                    student_pk=student.id,
                    course_code="CSE-201",
                    course_title="Data Structures",
                    exam_type="Midterm",
                    exam_date=date(2026, 8, 5),
                    start_time="10:00 AM",
                    room="B-204",
                ),
                StudentExam(
                    student_pk=student.id,
                    course_code="CSE-205",
                    course_title="Database Systems",
                    exam_type="Midterm",
                    exam_date=date(2026, 8, 8),
                    start_time="02:00 PM",
                    room="Lab-3",
                ),
            ]
        )

    db.commit()
