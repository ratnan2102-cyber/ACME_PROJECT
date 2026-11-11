"""Customer endpoints and customer order history tests."""

from datetime import datetime

import pytest


def test_customer_list_default_pagination(client):
    response = client.get("/customers")
    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 20
    assert body["total"] == 200
    assert (body["page"], body["page_size"]) == (1, 20)
    assert [row["id"] for row in body["items"]] == list(range(1, 21))


@pytest.mark.parametrize("params", [{"page": 0}, {"page_size": 0}, {"page_size": 101}])
def test_customer_list_rejects_bad_pagination(client, params):
    assert client.get("/customers", params=params).status_code == 422


def test_customer_city_filter_count(client, seed):
    city = seed["customers"][0]["city"]
    expected = sum(customer["city"] == city for customer in seed["customers"])
    response = client.get("/customers", params={"city": city, "page_size": 100})
    assert response.status_code == 200
    assert response.json()["total"] == expected
    assert all(row["city"] == city for row in response.json()["items"])


def test_get_customer(client, seed):
    expected = seed["customers"][0]
    response = client.get(f"/customers/{expected['id']}")
    assert response.status_code == 200
    assert response.json()["email"] == expected["email"]


def test_get_unknown_customer_returns_404(client):
    response = client.get("/customers/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"


def test_customer_orders_are_complete_and_newest_first(client, seed):
    customer_id = seed["orders"][0]["customer_id"]
    expected = [row for row in seed["orders"] if row["customer_id"] == customer_id]
    expected.sort(key=lambda row: row["id"])
    expected.sort(key=lambda row: datetime.fromisoformat(row["created_at"]), reverse=True)
    response = client.get(f"/customers/{customer_id}/orders")
    assert response.status_code == 200
    rows = response.json()
    assert len(rows) == len(expected)
    assert all(row["customer_id"] == customer_id for row in rows)
    assert [row["id"] for row in rows] == [row["id"] for row in expected]


def test_orders_of_unknown_customer_return_404(client):
    response = client.get("/customers/9999/orders")
    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"
