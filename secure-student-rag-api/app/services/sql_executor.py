from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.security.sql_validator import MAX_LIMIT, validate_sql


def execute_student_sql(db: Session, sql: str, student_id: str) -> list[dict[str, Any]]:
    safe_sql = validate_sql(sql)
    result = db.execute(text(safe_sql), {"student_id": student_id})
    rows = result.mappings().fetchmany(MAX_LIMIT)
    return [dict(row) for row in rows]
