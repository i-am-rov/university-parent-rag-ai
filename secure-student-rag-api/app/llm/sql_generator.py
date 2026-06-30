import requests
from fastapi import HTTPException, status

from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT_SECONDS
from app.llm.local_llm import remove_thinking_text
from app.security.sql_validator import validate_sql


import re


SQL_FENCE_RE = re.compile(r"```(?:sql)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


DATABASE_SCHEMA = """
Allowed tables and columns:

students:
- id
- student_id
- full_name
- department
- semester
- cgpa
- guardian_id

student_fees:
- id
- student_pk
- semester
- total_amount
- paid_amount
- due_amount
- status
- due_date

student_courses:
- id
- student_pk
- code
- title
- credit
- teacher
- semester

student_exams:
- id
- student_pk
- course_code
- course_title
- exam_type
- exam_date
- start_time
- room
"""


def build_sql_prompt(question: str) -> str:
    return f"""
You generate safe SQLite SELECT SQL for a parent/student portal.

Rules:
- Return only one SQL SELECT statement.
- Do not explain.
- Do not use markdown.
- Never generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, PRAGMA, ATTACH, or DETACH.
- Never hard-code a student ID value.
- Always scope the query with the parameter :student_id.
- For the students table, use WHERE student_id = :student_id.
- For child tables, join through students or use a subquery linked to students.id.
- Use LIMIT only when a list may be returned, and keep LIMIT between 1 and 100.

{DATABASE_SCHEMA}

Question: {question}

SQL:
""".strip()


def extract_sql(raw_text: str) -> str:
    text = remove_thinking_text(raw_text).strip()
    fenced = SQL_FENCE_RE.search(text)
    if fenced:
        text = fenced.group(1).strip()

    select_index = text.lower().find("select")
    if select_index >= 0:
        text = text[select_index:]

    first_statement = text.split(";", 1)[0].strip()
    if not first_statement:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="LLM did not return SQL.")
    return f"{first_statement};"


def generate_sql(question: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": build_sql_prompt(question),
        "stream": False,
    }

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=OLLAMA_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Could not connect to Ollama model {OLLAMA_MODEL}.",
        ) from exc

    sql = validate_sql(extract_sql(response.json().get("response", "")))
    print(f"[SQL_GENERATOR] question={question!r}")
    print(f"[SQL_GENERATOR] sql={sql}")
    return sql
