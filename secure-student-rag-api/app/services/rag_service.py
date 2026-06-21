import re
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.database import KnowledgeDocument, Student


TOKEN_RE = re.compile(r"[a-zA-Z0-9]+")


@dataclass
class RetrievedDocument:
    id: int
    title: str
    category: str
    snippet: str
    score: float
    content: str


def tokenize(text: str) -> set[str]:
    return {token.lower() for token in TOKEN_RE.findall(text) if len(token) > 2}


def snippet_for(content: str, limit: int = 220) -> str:
    compact = " ".join(content.split())
    if len(compact) <= limit:
        return compact
    return f"{compact[:limit].rstrip()}..."


def search_documents(db: Session, query: str, category: str | None = None, limit: int = 5) -> list[RetrievedDocument]:
    query_tokens = tokenize(query)
    docs_query = db.query(KnowledgeDocument).filter(KnowledgeDocument.is_public.is_(True))
    if category:
        docs_query = docs_query.filter(KnowledgeDocument.category == category)

    scored: list[RetrievedDocument] = []
    for doc in docs_query.all():
        doc_tokens = tokenize(f"{doc.title} {doc.category} {doc.content}")
        overlap = len(query_tokens & doc_tokens)
        if not query_tokens:
            score = 0.0
        else:
            score = overlap / len(query_tokens)
        if score > 0:
            scored.append(
                RetrievedDocument(
                    id=doc.id,
                    title=doc.title,
                    category=doc.category,
                    snippet=snippet_for(doc.content),
                    score=round(score, 3),
                    content=doc.content,
                )
            )

    return sorted(scored, key=lambda result: result.score, reverse=True)[:limit]


def build_answer(question: str, sources: list[RetrievedDocument], student: Student | None = None) -> str:
    if not sources:
        return (
            "I could not find a matching policy document for that question. Please contact the university "
            "office or add the relevant document to the knowledge base."
        )

    student_context = ""
    if student is not None:
        student_context = (
            f"For {student.full_name} ({student.student_id}), {student.department}, "
            f"{student.semester}: "
        )

    evidence = " ".join(source.content for source in sources[:2])
    return (
        f"{student_context}Based on the available university information, {evidence} "
        "For personal academic or financial decisions, verify the final details with the authorized office."
    )
