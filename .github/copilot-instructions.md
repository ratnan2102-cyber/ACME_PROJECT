# Copilot instructions — Acme Support Copilot

- Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2 (typed `Mapped[...]` style), SQLite, pytest, ruff.
- The full spec lives in `specs/acme_backend_spec.md`; follow it exactly and ask if it is unclear.
- Every new endpoint needs a Pydantic model in `app/schemas.py` and tests in `tests/`.
- Routes take the database as `db: DbSession` from `app/db.py`; list endpoints use `paginate()`.
- Return Pydantic/ORM objects via `response_model`; use the spec's status codes.
- Add no dependencies beyond `requirements.txt`.
- Never edit `data/seed.json` or `scripts/generate_seed.py`; never read `.env` or print secrets.
- Run `ruff check .`, `ruff format .`, and `pytest -q` before finishing.
- Keep code small and readable; comment only when the reason is not obvious.
