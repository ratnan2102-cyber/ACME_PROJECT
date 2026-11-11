"""Pydantic request and response models."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

OrderStatus = Literal["placed", "shipped", "delivered", "returned", "refunded"]
TicketStatus = Literal["open", "in_progress", "resolved", "closed"]
Priority = Literal["low", "medium", "high"]
Channel = Literal["email", "chat", "whatsapp", "phone"]
HealthStatus = Literal["ok"]


class HealthOut(BaseModel):
    """Health check response."""

    status: HealthStatus


class CustomerOut(BaseModel):
    """Public customer representation."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    phone: str
    city: str
    state: str
    created_at: datetime


class OrderOut(BaseModel):
    """Public order representation."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    customer_id: int
    product: str
    category: str
    quantity: int
    amount_inr: float
    payment_method: str
    status: OrderStatus
    created_at: datetime


class OrderStatusUpdate(BaseModel):
    """Requested order status."""

    status: OrderStatus


class TicketCreate(BaseModel):
    """Fields required to create a support ticket."""

    customer_id: int
    order_id: str | None = None
    subject: str = Field(min_length=3, max_length=200)
    message: str = Field(min_length=5, max_length=5000)
    channel: Channel = "email"
    priority: Priority = "medium"


class TicketOut(BaseModel):
    """Public ticket representation."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    order_id: str | None
    subject: str
    message: str
    channel: Channel
    priority: Priority
    status: TicketStatus
    created_at: datetime


class TicketStatusUpdate(BaseModel):
    """Requested ticket status."""

    status: TicketStatus


class Page[T](BaseModel):
    """A page of filtered results."""

    items: list[T]
    total: int
    page: int
    page_size: int
