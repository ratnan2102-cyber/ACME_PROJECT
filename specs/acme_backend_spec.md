# Acme Support Copilot — backend spec

## Purpose

Acme is a fictional Indian online store. Support agents use this API to look up customers and
orders, move orders through their lifecycle, and work the support-ticket queue. Prices are in
rupees. Customers pay by UPI, Card, Cash on Delivery, Net Banking, or Wallet; support channels are
email, chat, WhatsApp, and phone. The API contract must be predictable for later AI clients.

## Data model

Use SQLAlchemy 2 typed ORM models and a SQLite `acme.db` in the project root.

- `customers`: integer primary key; name (100), unique email (200), phone (20), indexed city (60),
  state (60), and required `created_at`.
- `orders`: string primary key `A-<number>` (20); indexed customer FK; product (100), category (40),
  quantity, amount in rupees, payment method (30), indexed status (20), indexed `created_at`.
- `tickets`: integer autoincrement primary key; indexed customer FK; nullable order FK; subject
  (200), message text, channel (20), indexed priority (10) and status (20), required `created_at`.
- Allowed order statuses: placed, shipped, delivered, returned, refunded. Allowed ticket statuses:
  open, in_progress, resolved, closed. Priorities: low, medium, high.

The canonical `data/seed.json` and `scripts/generate_seed.py` are provided and must never be edited.
On startup create tables and, only if customers are empty, load customers then orders then tickets,
flushing between groups and converting ISO timestamps to `datetime`. `load_seed` returns whether it
loaded data.

## API contract

Every paginated list accepts `page` (integer >= 1, default 1) and `page_size` (integer 1–100,
default 20), returning `{"items": [], "total": 0, "page": 1, "page_size": 20}`. Every list counts
all rows matching its filters, before slicing.

| Method | Path | Contract |
|---|---|---|
| GET | `/health` | `{"status":"ok"}` |
| GET | `/customers` | Paginated, optional city filter, ascending id |
| GET | `/customers/{customer_id}` | Customer or 404 `Customer not found` |
| GET | `/customers/{customer_id}/orders` | Customer's orders, newest first; missing customer 404 |
| GET | `/orders` | Paginated, newest first, then id |
| GET | `/orders/search` | Optional status/customer/date filters, newest first |
| GET | `/orders/{order_id}` | Order or 404 `Order not found` |
| PATCH | `/orders/{order_id}/status` | Advance one lifecycle step only |
| POST | `/tickets` | Create open ticket; 201 |
| GET | `/tickets` | Paginated status/priority/customer filters, newest first |
| GET | `/tickets/{ticket_id}` | Ticket or 404 `Ticket not found` |
| PATCH | `/tickets/{ticket_id}/status` | Change status unless ticket is already closed |

Order search dates are ISO `YYYY-MM-DD`, inclusive through the full `date_to` day. If
`date_from > date_to`, return 422 with `date_from must be on or before date_to`. Declare search
before the dynamic order-id route.

Order status transitions are strictly one step: placed → shipped → delivered → returned → refunded.
No same-status, backward, or skipped transitions are allowed; return 409 with
`Cannot change status from '<old>' to '<new>'`.

Tickets may optionally reference only an order belonging to their customer. Missing customers return
404 `Customer not found`; a missing or foreign order returns 404 `Order not found for this customer`.
Closed tickets cannot change status, including closed → closed; return 409
`Closed tickets cannot be reopened`.

Define allowed values as tuples in `app/models.py` and `Literal` types in `app/schemas.py`, ensuring
invalid enum values return 422. `TicketCreate` has required customer, subject (3–200 chars), and
message (5–5000 chars); optional order id; channel defaults to email and priority to medium.
All output schemas use `ConfigDict(from_attributes=True)`.

## Project and tests

Keep the modules described in the README's project layout. Tests use an independent in-memory SQLite
database per test, `StaticPool`, and `app.dependency_overrides`; instantiate `TestClient` without a
context manager so the real database startup does not run. A session-scoped seed fixture provides
expected values to tests. Tests must not touch `acme.db` or depend on test order.

Run `pytest -q` and `ruff check .`. The docs should expose all 12 endpoints grouped under health,
customers, orders, and tickets.
