"""Authentication, authorization, and student data access guards."""

from app.security.student_scope_guard import (
    ensure_parent_can_access_student,
    filter_query_to_student_scope,
    get_linked_student_for_parent,
    get_scoped_student_for_user,
)

__all__ = [
    "ensure_parent_can_access_student",
    "filter_query_to_student_scope",
    "get_linked_student_for_parent",
    "get_scoped_student_for_user",
]
