"""Order browsing and status transition tests."""

import pytest

from app.models import ORDER_STATUSES


def find_order(seed, status):
    return next(row for row in seed["orders"] if row["status"] == status)


def test_order_list_is_paginated_and_newest_first(client, seed):
    response = client.get("/orders", params={"page_size": 10})
    assert response.status_code == 200
    body = response.json()
    expected = sorted(seed["orders"], key=lambda row: row["id"])
    expected.sort(key=lambda row: row["created_at"], reverse=True)
    assert body["total"] == 1000
    assert [row["id"] for row in body["items"]] == [row["id"] for row in expected[:10]]


def test_order_list_rejects_bad_pagination(client):
    assert client.get("/orders", params={"page": 0}).status_code == 422
    assert client.get("/orders", params={"page_size": 101}).status_code == 422


def test_get_order_a1001(client):
    response = client.get("/orders/A-1001")
    assert response.status_code == 200
    assert response.json()["id"] == "A-1001"


def test_unknown_order_returns_404(client):
    response = client.get("/orders/not-an-order")
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


@pytest.mark.parametrize(
    ("current", "next_status"),
    [
        ("placed", "shipped"),
        ("shipped", "delivered"),
        ("delivered", "returned"),
        ("returned", "refunded"),
    ],
)
def test_valid_order_transition_is_persisted(client, seed, current, next_status):
    order_id = find_order(seed, current)["id"]
    response = client.patch(f"/orders/{order_id}/status", json={"status": next_status})
    assert response.status_code == 200
    assert response.json()["status"] == next_status
    assert client.get(f"/orders/{order_id}").json()["status"] == next_status


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("placed", "delivered"),
        ("shipped", "placed"),
        ("placed", "placed"),
        ("refunded", "shipped"),
    ],
)
def test_invalid_order_transition_returns_conflict(client, seed, current, target):
    order_id = find_order(seed, current)["id"]
    response = client.patch(f"/orders/{order_id}/status", json={"status": target})
    assert response.status_code == 409
    assert response.json()["detail"] == (f"Cannot change status from '{current}' to '{target}'")


def test_unknown_order_status_returns_422(client, seed):
    order_id = find_order(seed, ORDER_STATUSES[0])["id"]
    assert (
        client.patch(f"/orders/{order_id}/status", json={"status": "cancelled"}).status_code == 422
    )


def test_changing_unknown_order_returns_404(client):
    response = client.patch("/orders/missing/status", json={"status": "shipped"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"
