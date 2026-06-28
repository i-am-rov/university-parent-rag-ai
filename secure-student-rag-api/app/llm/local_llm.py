import re

import requests
from fastapi import HTTPException, status

from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT_SECONDS
from app.database import Student


THINK_BLOCK_RE = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)


def remove_thinking_text(answer: str) -> str:
    return THINK_BLOCK_RE.sub("", answer).strip()


def build_prompt(question: str, student: Student) -> str:
    return (
        "You are a helpful university parent assistant. "
        "Answer only for the logged-in parent's linked student. "
        "Do not mention or invent data about other students.\n\n"
        f"Linked student: {student.full_name} ({student.student_id}), "
        f"Department: {student.department}, Semester: {student.semester}\n\n"
        f"Parent question: {question}\n\n"
        "Answer:"
    )


def ask_ollama(question: str, student: Student) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": build_prompt(question, student),
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

    answer = remove_thinking_text(response.json().get("response", ""))
    if not answer:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Ollama returned an empty answer.",
        )
    return answer
