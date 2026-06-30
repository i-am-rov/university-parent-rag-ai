import re

from fastapi import HTTPException, status


MAX_LIMIT = 100

ALLOWED_TABLES: dict[str, set[str]] = {
    "students": {
        "id",
        "student_id",
        "full_name",
        "department",
        "semester",
        "cgpa",
        "guardian_id",
    },
    "student_fees": {
        "id",
        "student_pk",
        "semester",
        "total_amount",
        "paid_amount",
        "due_amount",
        "status",
        "due_date",
    },
    "student_courses": {
        "id",
        "student_pk",
        "code",
        "title",
        "credit",
        "teacher",
        "semester",
    },
    "student_exams": {
        "id",
        "student_pk",
        "course_code",
        "course_title",
        "exam_type",
        "exam_date",
        "start_time",
        "room",
    },
}

FORBIDDEN_SQL = re.compile(
    r"\b(delete|update|insert|drop|alter|truncate|create|replace|pragma|attach|detach)\b",
    re.IGNORECASE,
)
TABLE_RE = re.compile(
    r"\b(?:from|join)\s+([a-zA-Z_][a-zA-Z0-9_]*)"
    r"(?:\s+(?:as\s+)?"
    r"(?!(?:where|join|inner|left|right|outer|on|and|or|group|order|having|limit|offset)\b)"
    r"([a-zA-Z_][a-zA-Z0-9_]*))?",
    re.IGNORECASE,
)
QUALIFIED_COLUMN_RE = re.compile(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\.\s*([a-zA-Z_][a-zA-Z0-9_]*)\b")
LIMIT_RE = re.compile(r"\blimit\s+([0-9]+)\b", re.IGNORECASE)
STUDENT_SCOPE_RE = re.compile(
    r"(?:\b[a-zA-Z_][a-zA-Z0-9_]*\s*\.\s*)?student_id\s*=\s*:student_id|"
    r":student_id\s*=\s*(?:\b[a-zA-Z_][a-zA-Z0-9_]*\s*\.\s*)?student_id",
    re.IGNORECASE,
)
IDENTIFIER_RE = re.compile(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b")
STRING_RE = re.compile(r"'(?:''|[^'])*'|\"(?:\"\"|[^\"])*\"")
WILDCARD_RE = re.compile(r"(^|[\s,])(?:[a-zA-Z_][a-zA-Z0-9_]*\s*\.)?\*($|[\s,)])")

SQL_KEYWORDS = {
    "select",
    "from",
    "where",
    "join",
    "inner",
    "left",
    "right",
    "outer",
    "on",
    "and",
    "or",
    "as",
    "in",
    "is",
    "not",
    "null",
    "like",
    "between",
    "order",
    "by",
    "asc",
    "desc",
    "group",
    "having",
    "limit",
    "offset",
    "distinct",
}
ALLOWED_FUNCTIONS = {"count", "sum", "avg", "min", "max", "round", "date"}


def normalize_sql(sql: str) -> str:
    return " ".join(sql.strip().split())


def reject_comments(sql: str) -> None:
    if "--" in sql or "/*" in sql or "*/" in sql:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SQL comments are not allowed.")


def reject_multiple_statements(sql: str) -> None:
    stripped = sql.strip()
    without_final_semicolon = stripped[:-1] if stripped.endswith(";") else stripped
    if ";" in without_final_semicolon:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only one SQL statement is allowed.")


def validate_select_only(sql: str) -> None:
    normalized = normalize_sql(sql).lower()
    if not normalized.startswith("select "):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only SELECT SQL is allowed.")
    if FORBIDDEN_SQL.search(sql):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dangerous SQL command is blocked.")


def validate_no_wildcards(sql: str) -> None:
    if WILDCARD_RE.search(sql):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wildcard column selection is not allowed.")


def table_aliases(sql: str) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for table, alias in TABLE_RE.findall(sql):
        table_name = table.lower()
        alias_name = alias.lower() if alias else ""

        if table_name not in ALLOWED_TABLES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Table is not allowed: {table}")

        aliases[table_name] = table_name
        if alias_name and alias_name not in SQL_KEYWORDS:
            aliases[alias_name] = table_name

    if not aliases:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SQL must reference an allowed table.")
    return aliases


def validate_qualified_columns(sql: str, aliases: dict[str, str]) -> None:
    for qualifier, column in QUALIFIED_COLUMN_RE.findall(sql):
        qualifier_name = qualifier.lower()
        column_name = column.lower()
        table_name = aliases.get(qualifier_name)

        if table_name is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown table or alias: {qualifier}",
            )
        if column_name not in ALLOWED_TABLES[table_name]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Column is not allowed: {qualifier}.{column}",
            )


def validate_identifiers(sql: str, aliases: dict[str, str]) -> None:
    sql_without_strings = STRING_RE.sub(" ", sql)
    sql_without_params = re.sub(r":[a-zA-Z_][a-zA-Z0-9_]*", " ", sql_without_strings)
    sql_without_qualified = QUALIFIED_COLUMN_RE.sub(" ", sql_without_params)

    allowed_columns = set().union(*ALLOWED_TABLES.values())
    allowed_identifiers = (
        SQL_KEYWORDS
        | ALLOWED_FUNCTIONS
        | set(ALLOWED_TABLES)
        | set(aliases)
        | allowed_columns
    )
    alias_names = {
        match.group(1).lower()
        for match in re.finditer(r"\bas\s+([a-zA-Z_][a-zA-Z0-9_]*)\b", sql_without_qualified, re.IGNORECASE)
    }
    allowed_identifiers |= alias_names

    for identifier in IDENTIFIER_RE.findall(sql_without_qualified):
        if identifier.lower() not in allowed_identifiers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Identifier is not allowed: {identifier}",
            )


def validate_limit(sql: str) -> None:
    limits = LIMIT_RE.findall(sql)
    if len(limits) > 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only one LIMIT clause is allowed.")

    if re.search(r"\blimit\b", sql, re.IGNORECASE) and not limits:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="LIMIT must be a positive integer.")

    if not limits:
        return

    limit = int(limits[0])
    if limit < 1 or limit > MAX_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"LIMIT must be between 1 and {MAX_LIMIT}.",
        )


def validate_student_scope(sql: str) -> None:
    if ":student_id" not in sql:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SQL must use :student_id parameter.")
    if not STUDENT_SCOPE_RE.search(sql):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SQL must scope data with student_id = :student_id.",
        )


def validate_sql(sql: str) -> str:
    cleaned = normalize_sql(sql)
    reject_comments(cleaned)
    reject_multiple_statements(cleaned)
    validate_select_only(cleaned)
    validate_no_wildcards(cleaned)
    aliases = table_aliases(cleaned)
    validate_qualified_columns(cleaned, aliases)
    validate_identifiers(cleaned, aliases)
    validate_limit(cleaned)
    validate_student_scope(cleaned)
    return cleaned
