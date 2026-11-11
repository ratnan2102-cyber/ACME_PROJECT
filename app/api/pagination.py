"""Shared pagination query parameters and database helper."""

from typing import Annotated, Any

from fastapi import Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

PageParam = Annotated[int, Query(ge=1)]
PageSizeParam = Annotated[int, Query(ge=1, le=100)]


def paginate(
    db: Session,
    stmt: Select[Any],
    page: int,
    page_size: int,
) -> dict[str, Any]:
    """Count all matching rows and return the requested result slice."""
    count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
    total = db.scalar(count_stmt) or 0
    items = db.scalars(stmt.offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": items, "total": total, "page": page, "page_size": page_size}
