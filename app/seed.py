"""Load the canonical Acme seed data into an empty database."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Customer, Order, Ticket

SEED_FILE = Path(__file__).resolve().parents[1] / "data" / "seed.json"


def _as_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def load_seed(db: Session, seed_file: Path = SEED_FILE) -> bool:
    """Load customers, orders, and tickets if the customer table is empty."""
    if db.scalar(select(Customer.id).limit(1)) is not None:
        return False

    with seed_file.open(encoding="utf-8") as file:
        data: dict[str, list[dict[str, Any]]] = json.load(file)

    for row in data["customers"]:
        db.add(Customer(**{**row, "created_at": _as_datetime(row["created_at"])}))
    db.flush()

    for row in data["orders"]:
        db.add(Order(**{**row, "created_at": _as_datetime(row["created_at"])}))
    db.flush()

    for row in data["tickets"]:
        db.add(Ticket(**{**row, "created_at": _as_datetime(row["created_at"])}))

    db.commit()
    return True
