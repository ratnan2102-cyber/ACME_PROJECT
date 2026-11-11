"""FastAPI application entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import customers, orders, tickets
from app.db import Base, SessionLocal, engine
from app.schemas import HealthOut
from app.seed import load_seed


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Create database tables and seed an empty database on startup."""
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        load_seed(db)
    yield


app = FastAPI(title="Acme Support Copilot", version="0.1.0", lifespan=lifespan)


@app.get("/health", response_model=HealthOut, tags=["health"])
def health() -> dict[str, str]:
    """Report that the API process is running."""
    return {"status": "ok"}


app.include_router(customers.router)
app.include_router(orders.router)
app.include_router(tickets.router)
