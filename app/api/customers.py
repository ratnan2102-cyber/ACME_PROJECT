"""Customer lookup and order-history endpoints."""

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.pagination import PageParam, PageSizeParam, paginate
from app.db import DbSession
from app.models import Customer, Order
from app.schemas import CustomerOut, OrderOut, Page

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=Page[CustomerOut])
def list_customers(
    db: DbSession,
    city: str | None = None,
    page: PageParam = 1,
    page_size: PageSizeParam = 20,
) -> dict:
    """List customers, optionally filtering by city."""
    stmt = select(Customer)
    if city is not None:
        stmt = stmt.where(Customer.city == city)
    return paginate(db, stmt.order_by(Customer.id), page, page_size)


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: int, db: DbSession) -> Customer:
    """Return one customer."""
    customer = db.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.get("/{customer_id}/orders", response_model=list[OrderOut])
def list_customer_orders(customer_id: int, db: DbSession) -> list[Order]:
    """Return a customer's orders, newest first."""
    if db.get(Customer, customer_id) is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    stmt = (
        select(Order)
        .where(Order.customer_id == customer_id)
        .order_by(Order.created_at.desc(), Order.id)
    )
    return list(db.scalars(stmt).all())
