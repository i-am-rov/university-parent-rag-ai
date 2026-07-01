import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any

import requests

from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT_SECONDS
from app.database import Student
from app.llm.local_llm import remove_thinking_text


def json_default(value: Any) -> str | float:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return str(value)


def fallback_answer(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "I could not find matching data for this question."
    if len(rows) == 1 and len(rows[0]) == 1:
        key, value = next(iter(rows[0].items()))
        return f"{key}: {value}"
    return json.dumps(rows, default=json_default, indent=2)


def build_answer_prompt(question: str, sql: str, rows: list[dict[str, Any]], student: Student) -> str:
    data = json.dumps(rows, default=json_default, indent=2)
    return f"""
You answer parent questions using only the database result provided.

Rules:
- Do not invent data.
- Do not mention other students.
- If the result is empty, say the information was not found.
- Keep the answer short and clear.

Student: {student.full_name} ({student.student_id})
Question: {question}
Validated SQL: {sql}
Database result:
{data}

Answer:
""".strip()


def answer_from_rows(question: str, sql: str, rows: list[dict[str, Any]], student: Student) -> str:
    if not rows:
        return fallback_answer(rows)

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": build_answer_prompt(question, sql, rows, student),
        "stream": False,
    }

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=OLLAMA_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.RequestException:
        return fallback_answer(rows)

    answer = remove_thinking_text(response.json().get("response", ""))
    return answer or fallback_answer(rows)
