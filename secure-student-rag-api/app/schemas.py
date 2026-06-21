from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    role: str = Field(default="parent", pattern="^(admin|parent|student)$")


class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class StudentCreate(BaseModel):
    student_id: str = Field(min_length=2, max_length=80)
    full_name: str = Field(min_length=2, max_length=255)
    department: str = Field(min_length=2, max_length=120)
    semester: str = Field(min_length=1, max_length=80)
    guardian_email: EmailStr | None = None


class StudentRead(BaseModel):
    id: int
    student_id: str
    full_name: str
    department: str
    semester: str
    guardian_id: int | None = None

    model_config = ConfigDict(from_attributes=True)


class DocumentCreate(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    category: str = Field(default="general", min_length=2, max_length=120)
    content: str = Field(min_length=10)
    is_public: bool = True


class DocumentRead(BaseModel):
    id: int
    title: str
    category: str
    content: str
    is_public: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SearchResult(BaseModel):
    id: int
    title: str
    category: str
    snippet: str
    score: float


class ChatRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    student_id: int | None = None
    category: str | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[SearchResult]
