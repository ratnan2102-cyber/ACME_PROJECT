"""Health check and seed loading tests."""

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db import Base
from app.models import Customer, Order, Ticket
from app.seed import load_seed


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_seed_loads_all_rows_once():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    with Session(engine) as db:
        assert load_seed(db) is True
        assert db.scalar(select(func.count()).select_from(Customer)) == 200
        assert db.scalar(select(func.count()).select_from(Order)) == 1000
        assert db.scalar(select(func.count()).select_from(Ticket)) == 300
        assert load_seed(db) is False
    engine.dispose()
