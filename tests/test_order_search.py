"""Order search filtering and date-boundary tests."""

from datetime import datetime

import pytest


def test_search_without_filters_returns_all_orders(client):
    body = client.get("/orders/search").json()
    assert body["total"] == 1000


@pytest.mark.parametrize("filter_name", ["status", "customer_id", "date_from", "date_to"])
def test_search_individual_filters_match_seed(client, seed, filter_name):
    example = seed["orders"][0]
    value = {
        "status": example["status"],
        "customer_id": example["customer_id"],
        "date_from": "2026-03-01",
        "date_to": "2026-03-31",
    }[filter_name]
    params = {filter_name: value, "page_size": 100}
    response = client.get("/orders/search", params=params)
    assert response.status_code == 200

    def matches(order):
        created = datetime.fromisoformat(order["created_at"])
        if filter_name == "status":
            return order["status"] == value
        if filter_name == "customer_id":
            return order["customer_id"] == value
        if filter_name == "date_from":
            return created.date().isoformat() >= value
        return created.date().isoformat() <= value

    assert response.json()["total"] == sum(matches(order) for order in seed["orders"])


def test_search_combines_all_filters(client, seed):
    target = seed["orders"][0]
    day = datetime.fromisoformat(target["created_at"]).date().isoformat()
    params = {
        "status": target["status"],
        "customer_id": target["customer_id"],
        "date_from": day,
        "date_to": day,
        "page_size": 100,
    }
    expected = [
        order
        for order in seed["orders"]
        if order["status"] == target["status"]
        and order["customer_id"] == target["customer_id"]
        and datetime.fromisoformat(order["created_at"]).date().isoformat() == day
    ]
    response = client.get("/orders/search", params=params)
    assert response.status_code == 200
    assert response.json()["total"] == len(expected)


def test_search_date_to_includes_full_day(client, seed):
    latest = max(datetime.fromisoformat(row["created_at"]) for row in seed["orders"])
    day = latest.date().isoformat()
    expected = sum(
        datetime.fromisoformat(row["created_at"]).date().isoformat() <= day
        for row in seed["orders"]
    )
    response = client.get("/orders/search", params={"date_to": day, "page_size": 100})
    assert response.status_code == 200
    assert response.json()["total"] == expected


def test_search_rejects_reversed_date_range(client):
    response = client.get(
        "/orders/search",
        params={"date_from": "2026-03-02", "date_to": "2026-03-01"},
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "date_from must be on or before date_to"


def test_search_rejects_invalid_status_and_date(client):
    assert client.get("/orders/search", params={"status": "cancelled"}).status_code == 422
    assert client.get("/orders/search", params={"date_from": "not-a-date"}).status_code == 422


def test_search_results_are_newest_first(client):
    response = client.get("/orders/search", params={"page_size": 100})
    rows = response.json()["items"]
    expected = sorted(rows, key=lambda row: row["id"])
    expected.sort(key=lambda row: row["created_at"], reverse=True)
    assert rows == expected


def test_search_page_past_end_has_no_items_and_preserves_total(client):
    body = client.get("/orders/search", params={"page": 1000, "page_size": 20}).json()
    assert body["items"] == []
    assert body["total"] == 1000
    assert body["page"] == 1000


def test_order_route_still_matches_a1001(client):
    assert client.get("/orders/A-1001").status_code == 200
