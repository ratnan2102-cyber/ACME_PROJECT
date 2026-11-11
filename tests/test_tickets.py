"""Support ticket creation, filtering, and status tests."""

import pytest


def test_create_ticket_without_order_uses_defaults(client, seed):
    response = client.post(
        "/tickets",
        json={
            "customer_id": seed["customers"][0]["id"],
            "subject": "Need help",
            "message": "Please assist me.",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "open"
    assert body["channel"] == "email"
    assert body["priority"] == "medium"
    assert body["order_id"] is None


def test_create_ticket_with_customer_order(client, seed):
    order = seed["orders"][0]
    response = client.post(
        "/tickets",
        json={
            "customer_id": order["customer_id"],
            "order_id": order["id"],
            "subject": "Order question",
            "message": "I have a question about this order.",
        },
    )
    assert response.status_code == 201
    assert response.json()["order_id"] == order["id"]


def test_create_ticket_unknown_customer_returns_404(client):
    response = client.post(
        "/tickets",
        json={"customer_id": 9999, "subject": "Need help", "message": "Please assist me."},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"


def test_create_ticket_missing_or_foreign_order_returns_404(client, seed):
    customer_id = seed["customers"][0]["id"]
    payload = {
        "customer_id": customer_id,
        "order_id": "missing",
        "subject": "Order question",
        "message": "I have a question about this order.",
    }
    response = client.post("/tickets", json=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found for this customer"

    foreign_order = next(row for row in seed["orders"] if row["customer_id"] != customer_id)
    payload["order_id"] = foreign_order["id"]
    response = client.post("/tickets", json=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found for this customer"


@pytest.mark.parametrize(
    "updates",
    [
        {"subject": "No"},
        {"message": "Tiny"},
        {"channel": "sms"},
        {"priority": "urgent"},
    ],
)
def test_create_ticket_validates_fields(client, seed, updates):
    payload = {
        "customer_id": seed["customers"][0]["id"],
        "subject": "Need help",
        "message": "Please assist me.",
        **updates,
    }
    assert client.post("/tickets", json=payload).status_code == 422


def test_new_ticket_appears_first_in_customer_queue(client, seed):
    customer_id = seed["customers"][0]["id"]
    created = client.post(
        "/tickets",
        json={"customer_id": customer_id, "subject": "New request", "message": "Please assist me."},
    )
    assert created.status_code == 201
    response = client.get("/tickets", params={"customer_id": customer_id})
    assert response.status_code == 200
    assert response.json()["items"][0]["id"] == created.json()["id"]


@pytest.mark.parametrize("filter_name", ["status", "priority", "customer_id"])
def test_ticket_filters_match_seed(client, seed, filter_name):
    value = seed["tickets"][0][filter_name]
    expected = sum(row[filter_name] == value for row in seed["tickets"])
    response = client.get("/tickets", params={filter_name: value, "page_size": 100})
    assert response.status_code == 200
    assert response.json()["total"] == expected


def test_ticket_filters_can_be_combined(client, seed):
    ticket = seed["tickets"][0]
    expected = sum(
        row["status"] == ticket["status"]
        and row["priority"] == ticket["priority"]
        and row["customer_id"] == ticket["customer_id"]
        for row in seed["tickets"]
    )
    response = client.get(
        "/tickets",
        params={
            "status": ticket["status"],
            "priority": ticket["priority"],
            "customer_id": ticket["customer_id"],
        },
    )
    assert response.status_code == 200
    assert response.json()["total"] == expected


def test_ticket_list_rejects_invalid_filters_and_paging(client):
    assert client.get("/tickets", params={"status": "waiting"}).status_code == 422
    assert client.get("/tickets", params={"priority": "urgent"}).status_code == 422
    assert client.get("/tickets", params={"page_size": 101}).status_code == 422


def test_get_ticket_and_unknown_ticket(client, seed):
    ticket_id = seed["tickets"][0]["id"]
    assert client.get(f"/tickets/{ticket_id}").status_code == 200
    response = client.get("/tickets/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


def test_ticket_status_can_be_changed_through_lifecycle(client, seed):
    customer_id = seed["customers"][0]["id"]
    created = client.post(
        "/tickets",
        json={"customer_id": customer_id, "subject": "New request", "message": "Please assist me."},
    ).json()
    for status in ("in_progress", "resolved", "closed"):
        response = client.patch(f"/tickets/{created['id']}/status", json={"status": status})
        assert response.status_code == 200
        assert response.json()["status"] == status


@pytest.mark.parametrize("status", ["open", "closed"])
def test_closed_ticket_rejects_all_status_changes(client, seed, status):
    ticket_id = next(row["id"] for row in seed["tickets"] if row["status"] == "closed")
    response = client.patch(f"/tickets/{ticket_id}/status", json={"status": status})
    assert response.status_code == 409
    assert response.json()["detail"] == "Closed tickets cannot be reopened"


def test_ticket_status_update_validation_and_missing_ticket(client, seed):
    ticket_id = seed["tickets"][0]["id"]
    assert (
        client.patch(f"/tickets/{ticket_id}/status", json={"status": "waiting"}).status_code == 422
    )
    response = client.patch("/tickets/9999/status", json={"status": "open"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"
