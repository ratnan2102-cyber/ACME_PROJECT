"""Shared test fixtures backed by a fresh in-memory SQLite database."""

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app
from app.seed import SEED_FILE, load_seed


@pytest.fixture(scope="session")
def seed() -> dict[str, list[dict[str, Any]]]:
    """Return canonical fixture values for expectations."""
    with SEED_FILE.open(encoding="utf-8") as file:
        return json.load(file)


@pytest.fixture
def client() -> Iterator[TestClient]:
    """Create a test client wired to a fresh in-memory database."""
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=test_engine)
    test_session = sessionmaker(bind=test_engine, autoflush=False, expire_on_commit=False)

    def override_get_db() -> Iterator[Session]:
        with test_session() as db:
            yield db

    with test_session() as db:
        load_seed(db, Path(SEED_FILE))

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        test_engine.dispose()
