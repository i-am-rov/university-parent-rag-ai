from app.services.rag_service import RetrievedDocument, build_answer
from app.database import Student


class LocalLLMProvider:
    """Deterministic local answer builder for development and tests."""

    def answer(self, question: str, sources: list[RetrievedDocument], student: Student | None = None) -> str:
        return build_answer(question=question, sources=sources, student=student)


llm_provider = LocalLLMProvider()
