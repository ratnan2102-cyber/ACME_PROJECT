# Acme Support Copilot

A FastAPI backend for Acme's customer-support team. It provides customer and order lookups, order
lifecycle updates, and support-ticket creation and queue management using SQLite and a fixed,
canonical dataset.

## Run

Use Python 3.12 and install the project dependencies:

```powershell
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

The first application startup creates `acme.db` and loads the seed data if the customer table is
empty. Visit <http://127.0.0.1:8000/docs> to explore the API.

## Run in Docker

Build the image and start the API with a named volume for persistent SQLite data:

```powershell
docker build -t acme-support-copilot .
docker run --name acme-support-copilot -p 8000:8000 -v acme-data:/data acme-support-copilot
```

Open <http://localhost:8000/docs>. The container seeds `/data/acme.db` on first startup; the
`acme-data` volume preserves the database when the container is replaced. Docker reports the
container as healthy after `/health` responds.

## Test and lint

```powershell
pytest -q
ruff check .
ruff format .
```

Tests use a separate in-memory database per test and do not read or modify `acme.db`.

## Data

`data/seed.json` contains 200 customers, 1,000 orders, and 300 tickets. It is the canonical,
fixed course dataset and must not be edited. `scripts/generate_seed.py` is the provided deterministic
generator and must not be edited.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/customers` | List customers; optional `city` filter |
| GET | `/customers/{customer_id}` | Get a customer |
| GET | `/customers/{customer_id}/orders` | List a customer's orders, newest first |
| GET | `/orders` | List orders, newest first |
| GET | `/orders/search` | Search by status, customer, and inclusive date range |
| GET | `/orders/{order_id}` | Get an order |
| PATCH | `/orders/{order_id}/status` | Advance an order exactly one lifecycle step |
| POST | `/tickets` | Create a support ticket |
| GET | `/tickets` | List tickets; optional status, priority, and customer filters |
| GET | `/tickets/{ticket_id}` | Get a ticket |
| PATCH | `/tickets/{ticket_id}/status` | Change a ticket's status unless closed |

All list endpoints accept `page` (default 1) and `page_size` (default 20, maximum 100). Responses
have the form:

```json
{"items": [], "total": 0, "page": 1, "page_size": 20}
```

## Project layout

```text
Dockerfile
.dockerignore
app/
  api/
    customers.py
    orders.py
    pagination.py
    tickets.py
  db.py
  main.py
  models.py
  schemas.py
  seed.py
data/seed.json
scripts/generate_seed.py
specs/acme_backend_spec.md
tests/
  conftest.py
  test_customers.py
  test_health.py
  test_order_search.py
  test_orders.py
  test_tickets.py
```
