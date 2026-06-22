from __future__ import annotations

import csv
import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "sample_database.sqlite3"
RANDOM_SEED = 20260616
STUDENT_COUNT = 1000


DEPARTMENTS = [
    ("CSE", "Computer Science and Engineering"),
    ("EEE", "Electrical and Electronic Engineering"),
    ("BBA", "Business Administration"),
    ("ENG", "English"),
    ("LAW", "Law"),
    ("PHR", "Pharmacy"),
    ("CE", "Civil Engineering"),
    ("ECO", "Economics"),
]

COURSE_BANK = {
    "CSE": [
        ("CSE101", "Structured Programming", 3.0),
        ("CSE203", "Data Structures", 3.0),
        ("CSE211", "Database Systems", 3.0),
        ("CSE305", "Operating Systems", 3.0),
        ("CSE321", "Artificial Intelligence", 3.0),
    ],
    "EEE": [
        ("EEE101", "Electrical Circuits", 3.0),
        ("EEE203", "Digital Electronics", 3.0),
        ("EEE221", "Signals and Systems", 3.0),
        ("EEE303", "Power Systems", 3.0),
        ("EEE315", "Control Systems", 3.0),
    ],
    "BBA": [
        ("BUS101", "Principles of Management", 3.0),
        ("BUS203", "Business Communication", 3.0),
        ("FIN221", "Corporate Finance", 3.0),
        ("MKT301", "Marketing Management", 3.0),
        ("ACC211", "Financial Accounting", 3.0),
    ],
    "ENG": [
        ("ENG101", "Composition and Rhetoric", 3.0),
        ("ENG205", "Bangladeshi Literature", 3.0),
        ("ENG221", "Phonetics", 3.0),
        ("ENG303", "Postcolonial Studies", 3.0),
        ("ENG315", "ELT Methods", 3.0),
    ],
    "LAW": [
        ("LAW101", "Legal System of Bangladesh", 3.0),
        ("LAW203", "Constitutional Law", 3.0),
        ("LAW221", "Criminal Law", 3.0),
        ("LAW303", "Contract Law", 3.0),
        ("LAW315", "Land Laws", 3.0),
    ],
    "PHR": [
        ("PHR101", "Pharmaceutical Chemistry", 3.0),
        ("PHR203", "Pharmacognosy", 3.0),
        ("PHR221", "Human Physiology", 3.0),
        ("PHR303", "Clinical Pharmacy", 3.0),
        ("PHR315", "Dosage Form Design", 3.0),
    ],
    "CE": [
        ("CE101", "Engineering Drawing", 3.0),
        ("CE203", "Structural Mechanics", 3.0),
        ("CE221", "Surveying", 3.0),
        ("CE303", "Transportation Engineering", 3.0),
        ("CE315", "Environmental Engineering", 3.0),
    ],
    "ECO": [
        ("ECO101", "Microeconomics", 3.0),
        ("ECO203", "Macroeconomics", 3.0),
        ("ECO221", "Bangladesh Economy", 3.0),
        ("ECO303", "Development Economics", 3.0),
        ("ECO315", "Econometrics", 3.0),
    ],
}

FIRST_NAMES_MALE = [
    "Arafat",
    "Sajid",
    "Rafi",
    "Tanvir",
    "Mahfuz",
    "Nayeem",
    "Shakib",
    "Fahim",
    "Imran",
    "Hasan",
    "Rakib",
    "Sabbir",
    "Nabil",
    "Arif",
    "Jubair",
]

FIRST_NAMES_FEMALE = [
    "Nusrat",
    "Maliha",
    "Tanjina",
    "Sadia",
    "Farhana",
    "Jannatul",
    "Mou",
    "Sumaiya",
    "Tasnim",
    "Ishrat",
    "Samia",
    "Afsana",
    "Nabila",
    "Sharmin",
    "Raisa",
]

LAST_NAMES = [
    "Ahmed",
    "Islam",
    "Rahman",
    "Hossain",
    "Akter",
    "Khan",
    "Chowdhury",
    "Miah",
    "Sultana",
    "Hasan",
    "Karim",
    "Begum",
]

DISTRICTS = [
    "Dhaka",
    "Chattogram",
    "Sylhet",
    "Rajshahi",
    "Khulna",
    "Barishal",
    "Rangpur",
    "Mymensingh",
    "Cumilla",
    "Gazipur",
    "Narayanganj",
    "Bogura",
    "Noakhali",
    "Kushtia",
    "Jessore",
    "Dinajpur",
]

SECTIONS = ["A", "B", "C", "D"]
FACULTIES = ["Dr. Rahman", "Prof. Sultana", "Dr. Karim", "Ms. Akter", "Mr. Chowdhury"]


STUDENT_FIELDS = [
    "student_id",
    "name",
    "gender",
    "date_of_birth",
    "department",
    "program",
    "batch",
    "semester",
    "section",
    "cgpa",
    "email",
    "phone",
    "present_address",
    "permanent_district",
    "guardian_name",
    "guardian_phone",
    "status",
    "admission_date",
]

COURSE_FIELDS = [
    "course_id",
    "student_id",
    "course_code",
    "course_title",
    "credit",
    "semester",
    "faculty",
    "section",
    "enrolled_status",
]

FEE_FIELDS = [
    "fee_id",
    "student_id",
    "semester",
    "tuition_fee",
    "lab_fee",
    "library_fee",
    "transport_fee",
    "waiver_percent",
    "total_payable",
    "paid_amount",
    "due_amount",
    "due_date",
    "payment_status",
]

EXAM_FIELDS = [
    "exam_id",
    "student_id",
    "semester",
    "course_code",
    "exam_type",
    "exam_date",
    "marks",
    "grade",
    "gpa",
]


def digits16(dept_index: int, batch: int, serial: int) -> str:
    return f"2026{dept_index + 1:02d}{batch:02d}{serial:08d}"


def phone(rng: random.Random) -> str:
    prefix = rng.choice(["013", "014", "015", "016", "017", "018", "019"])
    return f"+880{prefix[1:]}{rng.randint(10000000, 99999999)}"


def grade_for_marks(marks: int) -> tuple[str, float]:
    if marks >= 80:
        return "A+", 4.00
    if marks >= 75:
        return "A", 3.75
    if marks >= 70:
        return "A-", 3.50
    if marks >= 65:
        return "B+", 3.25
    if marks >= 60:
        return "B", 3.00
    if marks >= 55:
        return "B-", 2.75
    if marks >= 50:
        return "C+", 2.50
    if marks >= 45:
        return "C", 2.25
    if marks >= 40:
        return "D", 2.00
    return "F", 0.00


def sql_value(value: object) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, (int, float)):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_rows() -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    rng = random.Random(RANDOM_SEED)
    students: list[dict[str, object]] = []
    courses: list[dict[str, object]] = []
    fees: list[dict[str, object]] = []
    exams: list[dict[str, object]] = []

    for serial in range(1, STUDENT_COUNT + 1):
        dept_index = (serial - 1) % len(DEPARTMENTS)
        dept_code, program = DEPARTMENTS[dept_index]
        batch = 49 + ((serial - 1) % 8)
        semester = 1 + ((serial - 1) % 8)
        section = SECTIONS[(serial - 1) % len(SECTIONS)]
        gender = "Female" if serial % 3 == 0 else "Male"
        first_name = rng.choice(FIRST_NAMES_FEMALE if gender == "Female" else FIRST_NAMES_MALE)
        last_name = rng.choice(LAST_NAMES)
        name = f"{first_name} {last_name}"
        student_id = digits16(dept_index, batch, serial)
        cgpa = round(rng.uniform(2.40, 3.95), 2)
        district = rng.choice(DISTRICTS)
        admission_date = date(2020 + ((batch - 49) % 4), rng.randint(1, 12), rng.randint(1, 28))
        dob = date(admission_date.year - rng.randint(18, 22), rng.randint(1, 12), rng.randint(1, 28))
        guardian_first = rng.choice(FIRST_NAMES_MALE)
        guardian_name = f"{guardian_first} {rng.choice(LAST_NAMES)}"

        students.append(
            {
                "student_id": student_id,
                "name": name,
                "gender": gender,
                "date_of_birth": dob.isoformat(),
                "department": dept_code,
                "program": program,
                "batch": batch,
                "semester": semester,
                "section": section,
                "cgpa": cgpa,
                "email": f"{first_name.lower()}.{last_name.lower()}.{serial}@student.example.edu.bd",
                "phone": phone(rng),
                "present_address": f"House {rng.randint(1, 220)}, Road {rng.randint(1, 30)}, {district}",
                "permanent_district": district,
                "guardian_name": guardian_name,
                "guardian_phone": phone(rng),
                "status": "Active" if serial % 37 else "On Leave",
                "admission_date": admission_date.isoformat(),
            }
        )

        for course_index, (code, title, credit) in enumerate(COURSE_BANK[dept_code], start=1):
            course_id = f"CRS{serial:04d}{course_index:02d}"
            courses.append(
                {
                    "course_id": course_id,
                    "student_id": student_id,
                    "course_code": code,
                    "course_title": title,
                    "credit": credit,
                    "semester": semester,
                    "faculty": rng.choice(FACULTIES),
                    "section": section,
                    "enrolled_status": "Enrolled",
                }
            )

            marks = rng.randint(40, 97)
            grade, gpa = grade_for_marks(marks)
            exams.append(
                {
                    "exam_id": f"EXM{serial:04d}{course_index:02d}",
                    "student_id": student_id,
                    "semester": semester,
                    "course_code": code,
                    "exam_type": "Final",
                    "exam_date": (date(2026, 7, 1) + timedelta(days=course_index + (serial % 20))).isoformat(),
                    "marks": marks,
                    "grade": grade,
                    "gpa": f"{gpa:.2f}",
                }
            )

        tuition_fee = rng.choice([32000, 36000, 40000, 45000, 50000])
        lab_fee = 3500 if dept_code in {"CSE", "EEE", "PHR", "CE"} else 1500
        library_fee = 1000
        transport_fee = rng.choice([0, 2500, 3500])
        waiver_percent = rng.choice([0, 0, 0, 10, 15, 20, 25, 30])
        subtotal = tuition_fee + lab_fee + library_fee + transport_fee
        total_payable = int(subtotal * (100 - waiver_percent) / 100)
        paid_amount = rng.choice([total_payable, total_payable, total_payable - 5000, total_payable - 10000])
        due_amount = max(total_payable - paid_amount, 0)
        fees.append(
            {
                "fee_id": f"FEE{serial:04d}",
                "student_id": student_id,
                "semester": semester,
                "tuition_fee": tuition_fee,
                "lab_fee": lab_fee,
                "library_fee": library_fee,
                "transport_fee": transport_fee,
                "waiver_percent": waiver_percent,
                "total_payable": total_payable,
                "paid_amount": paid_amount,
                "due_amount": due_amount,
                "due_date": date(2026, 8, 15).isoformat(),
                "payment_status": "Paid" if due_amount == 0 else "Due",
            }
        )

    return students, courses, fees, exams


def create_sql(students: list[dict[str, object]], courses: list[dict[str, object]], fees: list[dict[str, object]], exams: list[dict[str, object]]) -> str:
    sections = [
        "-- Bangladesh-style university sample data",
        "-- Generated by scripts/generate_sample_data.py",
        "PRAGMA foreign_keys = ON;",
        "DROP TABLE IF EXISTS exams;",
        "DROP TABLE IF EXISTS fees;",
        "DROP TABLE IF EXISTS courses;",
        "DROP TABLE IF EXISTS students;",
        """
CREATE TABLE students (
    student_id TEXT PRIMARY KEY CHECK(length(student_id) = 16),
    name TEXT NOT NULL,
    gender TEXT NOT NULL,
    date_of_birth TEXT NOT NULL,
    department TEXT NOT NULL,
    program TEXT NOT NULL,
    batch INTEGER NOT NULL,
    semester INTEGER NOT NULL,
    section TEXT NOT NULL,
    cgpa REAL NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT NOT NULL,
    present_address TEXT NOT NULL,
    permanent_district TEXT NOT NULL,
    guardian_name TEXT NOT NULL,
    guardian_phone TEXT NOT NULL,
    status TEXT NOT NULL,
    admission_date TEXT NOT NULL
);""",
        """
CREATE TABLE courses (
    course_id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    course_code TEXT NOT NULL,
    course_title TEXT NOT NULL,
    credit REAL NOT NULL,
    semester INTEGER NOT NULL,
    faculty TEXT NOT NULL,
    section TEXT NOT NULL,
    enrolled_status TEXT NOT NULL
);""",
        """
CREATE TABLE fees (
    fee_id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    semester INTEGER NOT NULL,
    tuition_fee INTEGER NOT NULL,
    lab_fee INTEGER NOT NULL,
    library_fee INTEGER NOT NULL,
    transport_fee INTEGER NOT NULL,
    waiver_percent INTEGER NOT NULL,
    total_payable INTEGER NOT NULL,
    paid_amount INTEGER NOT NULL,
    due_amount INTEGER NOT NULL,
    due_date TEXT NOT NULL,
    payment_status TEXT NOT NULL
);""",
        """
CREATE TABLE exams (
    exam_id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    semester INTEGER NOT NULL,
    course_code TEXT NOT NULL,
    exam_type TEXT NOT NULL,
    exam_date TEXT NOT NULL,
    marks INTEGER NOT NULL,
    grade TEXT NOT NULL,
    gpa REAL NOT NULL
);""",
        "CREATE INDEX idx_courses_student_id ON courses(student_id);",
        "CREATE INDEX idx_fees_student_id ON fees(student_id);",
        "CREATE INDEX idx_exams_student_id ON exams(student_id);",
    ]

    table_rows = [
        ("students", STUDENT_FIELDS, students),
        ("courses", COURSE_FIELDS, courses),
        ("fees", FEE_FIELDS, fees),
        ("exams", EXAM_FIELDS, exams),
    ]

    for table, fields, rows in table_rows:
        columns = ", ".join(fields)
        sections.append(f"\n-- {len(rows)} {table} rows")
        for row in rows:
            values = ", ".join(sql_value(row[field]) for field in fields)
            sections.append(f"INSERT INTO {table} ({columns}) VALUES ({values});")

    return "\n".join(sections) + "\n"


def write_sqlite_database(sql_text: str) -> None:
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("PRAGMA journal_mode = OFF;")
        connection.executescript(sql_text)


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    students, courses, fees, exams = build_rows()

    write_csv(DATA_DIR / "sample_students.csv", STUDENT_FIELDS, students)
    write_csv(DATA_DIR / "sample_courses.csv", COURSE_FIELDS, courses)
    write_csv(DATA_DIR / "sample_fees.csv", FEE_FIELDS, fees)
    write_csv(DATA_DIR / "sample_exams.csv", EXAM_FIELDS, exams)

    sql_text = create_sql(students, courses, fees, exams)
    (DATA_DIR / "sample_database.sql").write_text(sql_text, encoding="utf-8")
    write_sqlite_database(sql_text)

    print(f"students={len(students)}")
    print(f"courses={len(courses)}")
    print(f"fees={len(fees)}")
    print(f"exams={len(exams)}")
    print(f"database={DB_PATH}")


if __name__ == "__main__":
    main()
