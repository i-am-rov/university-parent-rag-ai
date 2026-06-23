# Secure Student RAG API

A ready-to-run FastAPI starter for a secure student-scoped RAG API.

## What Is Included

- JWT authentication with hashed passwords.
- Role support for `admin`, `parent`, and `student`.
- SQLite database models for users, students, knowledge documents, and chat history.
- Student access guard so parents can only query assigned students.
- Local document retrieval and deterministic answer generation for development.
- Demo seed data on first startup.

## Project Structure

```text
secure-student-rag-api/
|-- app/
|   |-- main.py
|   |-- database.py
|   |-- schemas.py
|   |-- routes/
|   |-- templates/
|   |-- static/
|   |-- services/
|   |-- llm/
|   `-- security/
|-- requirements.txt
|-- .env
`-- README.md
```

## Run Locally

```powershell
cd secure-student-rag-api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:

- Home page: http://127.0.0.1:8000/
- Login page: http://127.0.0.1:8000/login
- Dashboard page: http://127.0.0.1:8000/dashboard
- Chat page: http://127.0.0.1:8000/chat
- API docs: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

## Demo Accounts

The app seeds these users the first time the database is created:

```text
admin@example.com  / AdminPass123
parent@example.com / ParentPass123
```

## Common API Flow

1. Login with `POST /api/auth/login`.
2. Use the returned bearer token in the `Authorization` header.
3. Ask a RAG question with `POST /api/chat`.

Example chat body:

```json
{
  "question": "What are the exam attendance rules?",
  "student_id": 1,
  "category": "exams"
}
```

## Production Notes

- Change `SECRET_KEY` in `.env`.
- Use a production database instead of the default SQLite file.
- Replace `app/llm/provider.py` with your approved LLM provider.
- Review and extend `app/security/guards.py` for your university privacy rules.
