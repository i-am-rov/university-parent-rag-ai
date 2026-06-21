from sqlalchemy.orm import Session

from app.database import KnowledgeDocument, Student, User
from app.security.auth import hash_password


def seed_demo_data(db: Session) -> None:
    if db.query(User).first():
        return

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

    student = Student(
        student_id="STU-1001",
        full_name="Ayesha Rahman",
        department="Computer Science",
        semester="Spring 2026",
        guardian_id=parent.id,
    )
    db.add(student)

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
    db.commit()
