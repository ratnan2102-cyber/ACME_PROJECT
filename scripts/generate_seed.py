"""
Generate data/seed.json — the fixed dataset every student uses.

Acme is a fictional Indian online store. The data is generated with a fixed
random seed, so every run (and every student's laptop) produces exactly the
same customers, orders and tickets. Later evaluations depend on that.

Run once (the output is already committed — you rarely need to run this):
    python scripts/generate_seed.py
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

SEED = 42
N_CUSTOMERS = 200
N_ORDERS = 1000
N_TICKETS = 300
START = datetime(2026, 1, 1, 9, 0, 0)

FIRST_NAMES = [
    "Aarav",
    "Vivaan",
    "Aditya",
    "Arjun",
    "Sai",
    "Reyansh",
    "Krishna",
    "Ishaan",
    "Rohan",
    "Karthik",
    "Rahul",
    "Siddharth",
    "Nikhil",
    "Pranav",
    "Harsh",
    "Ananya",
    "Diya",
    "Aadhya",
    "Saanvi",
    "Priya",
    "Kavya",
    "Meera",
    "Sneha",
    "Pooja",
    "Divya",
    "Lakshmi",
    "Nandini",
    "Riya",
    "Shreya",
    "Fatima",
    "Imran",
    "Ayesha",
    "Gurpreet",
    "Harpreet",
    "Joseph",
    "Mary",
    "Tenzin",
]
LAST_NAMES = [
    "Sharma",
    "Verma",
    "Iyer",
    "Reddy",
    "Nair",
    "Patel",
    "Shah",
    "Gupta",
    "Mehta",
    "Rao",
    "Kulkarni",
    "Deshpande",
    "Chatterjee",
    "Banerjee",
    "Das",
    "Singh",
    "Khan",
    "Joshi",
    "Pillai",
    "Menon",
    "Agarwal",
    "Bhat",
    "Naidu",
    "Mishra",
    "Thomas",
    "Fernandes",
    "Kaur",
    "Hegde",
]
CITIES = [
    ("Bengaluru", "Karnataka"),
    ("Mumbai", "Maharashtra"),
    ("Pune", "Maharashtra"),
    ("Hyderabad", "Telangana"),
    ("Chennai", "Tamil Nadu"),
    ("Delhi", "Delhi"),
    ("Kolkata", "West Bengal"),
    ("Ahmedabad", "Gujarat"),
    ("Jaipur", "Rajasthan"),
    ("Lucknow", "Uttar Pradesh"),
    ("Kochi", "Kerala"),
    ("Indore", "Madhya Pradesh"),
    ("Bhubaneswar", "Odisha"),
    ("Chandigarh", "Chandigarh"),
    ("Guwahati", "Assam"),
    ("Coimbatore", "Tamil Nadu"),
    ("Nagpur", "Maharashtra"),
    ("Visakhapatnam", "Andhra Pradesh"),
]
# (product, category, min price, max price) — prices in rupees
PRODUCTS = [
    ("Cotton Kurta", "fashion", 499, 1499),
    ("Silk Saree", "fashion", 1999, 8999),
    ("Running Shoes", "fashion", 1299, 4999),
    ("Pressure Cooker 5L", "home_kitchen", 1199, 2999),
    ("Steel Tiffin Box", "home_kitchen", 299, 899),
    ("Mixer Grinder 750W", "home_kitchen", 2499, 5999),
    ("Bluetooth Earbuds", "electronics", 999, 3999),
    ("Smartphone 5G", "electronics", 11999, 29999),
    ("Power Bank 20000mAh", "electronics", 1099, 2499),
    ("Laptop Backpack", "accessories", 799, 2499),
    ("Cricket Bat (Kashmir Willow)", "sports", 1499, 4999),
    ("Yoga Mat", "sports", 399, 1299),
    ("NCERT Physics Set", "books", 499, 999),
    ("JEE Practice Workbook", "books", 399, 899),
    ("Ayurvedic Face Wash", "beauty", 149, 449),
]
STATUSES = ["placed", "shipped", "delivered", "returned", "refunded"]
STATUS_WEIGHTS = [15, 20, 50, 8, 7]
PAYMENT_METHODS = ["UPI", "Card", "Cash on Delivery", "Net Banking", "Wallet"]

# Ticket templates loosely follow customer-support intents used later in the course.
TICKET_TEMPLATES = [
    (
        "Where is my order?",
        "My order {order} has not reached {city} yet. It's been many days. Please share the tracking status.",
    ),
    ("Cancel my order", "I placed order {order} by mistake. Please cancel it before it ships."),
    (
        "Refund not received",
        "I returned order {order} last week but the refund has not come to my {payment} account yet.",
    ),
    (
        "Wrong item delivered",
        "I ordered a {product} (order {order}) but received something else. Need a replacement.",
    ),
    (
        "Change delivery address",
        "Can you deliver order {order} to my office address in {city} instead of home?",
    ),
    (
        "Payment deducted twice",
        "Money got deducted twice through {payment} for order {order}. Please reverse the extra amount.",
    ),
    ("Damaged product", "The {product} from order {order} arrived damaged. The box was torn."),
    (
        "Invoice needed for GST",
        "Please send a GST invoice for order {order}. I need it for office reimbursement.",
    ),
    ("COD not available", "Why is Cash on Delivery not available for my pincode in {city}?"),
    ("Account login issue", "I am not getting the OTP on my phone to log in to my Acme account."),
    (
        "Warranty claim",
        "My {product} (order {order}) stopped working within 2 months. How do I claim warranty?",
    ),
    (
        "Delivery boy asked extra money",
        "The delivery person asked for Rs 50 extra for order {order}. Is this allowed?",
    ),
]
TICKET_STATUSES = ["open", "in_progress", "resolved", "closed"]
TICKET_STATUS_WEIGHTS = [40, 25, 25, 10]
PRIORITIES = ["low", "medium", "high"]
CHANNELS = ["email", "chat", "whatsapp", "phone"]


def iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def main() -> None:
    rng = random.Random(SEED)

    customers = []
    for i in range(1, N_CUSTOMERS + 1):
        first, last = rng.choice(FIRST_NAMES), rng.choice(LAST_NAMES)
        city, state = rng.choice(CITIES)
        customers.append(
            {
                "id": i,
                "name": f"{first} {last}",
                "email": f"{first.lower()}.{last.lower()}{i}@example.in",
                "phone": f"+91 9{rng.randint(100000000, 999999999)}",
                "city": city,
                "state": state,
                "created_at": iso(START - timedelta(days=rng.randint(30, 700))),
            }
        )

    orders = []
    for i in range(N_ORDERS):
        customer = rng.choice(customers)
        product, category, lo, hi = rng.choice(PRODUCTS)
        quantity = rng.choices([1, 2, 3], weights=[80, 15, 5])[0]
        orders.append(
            {
                "id": f"A-{1001 + i}",
                "customer_id": customer["id"],
                "product": product,
                "category": category,
                "quantity": quantity,
                "amount_inr": round(rng.randint(lo, hi) * quantity, 2),
                "payment_method": rng.choice(PAYMENT_METHODS),
                "status": rng.choices(STATUSES, weights=STATUS_WEIGHTS)[0],
                "created_at": iso(START + timedelta(minutes=rng.randint(0, 270 * 24 * 60))),
            }
        )

    by_id = {c["id"]: c for c in customers}
    tickets = []
    for i in range(1, N_TICKETS + 1):
        order = rng.choice(orders)
        customer = by_id[order["customer_id"]]
        subject, body = rng.choice(TICKET_TEMPLATES)
        mentions_order = "{order}" in body
        created = datetime.fromisoformat(order["created_at"]) + timedelta(hours=rng.randint(2, 240))
        tickets.append(
            {
                "id": i,
                "customer_id": customer["id"],
                "order_id": order["id"] if mentions_order else None,
                "subject": subject,
                "message": body.format(
                    order=order["id"],
                    city=customer["city"],
                    payment=order["payment_method"],
                    product=order["product"],
                ),
                "channel": rng.choice(CHANNELS),
                "priority": rng.choices(PRIORITIES, weights=[30, 50, 20])[0],
                "status": rng.choices(TICKET_STATUSES, weights=TICKET_STATUS_WEIGHTS)[0],
                "created_at": iso(created),
            }
        )

    out = Path(__file__).resolve().parent.parent / "data" / "seed.json"
    out.write_text(
        json.dumps(
            {"customers": customers, "orders": orders, "tickets": tickets},
            indent=1,
            ensure_ascii=False,
        )
    )
    print(
        f"Wrote {len(customers)} customers, {len(orders)} orders, {len(tickets)} tickets -> {out}"
    )


if __name__ == "__main__":
    main()
