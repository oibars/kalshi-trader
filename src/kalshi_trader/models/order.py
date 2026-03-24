"""Order model for trading orders."""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
import uuid


class OrderType(str, Enum):
    """Type of order."""

    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"


class OrderStatus(str, Enum):
    """Status of an order."""

    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class OrderBase(BaseModel):
    """Base model for orders."""

    market_id: str = Field(..., description="Market ID")
    side: str = Field(..., description="Order side (yes/no)")
    quantity: int = Field(..., ge=1, description="Number of contracts")
    order_type: OrderType = Field(default=OrderType.MARKET)
    price: Optional[float] = Field(None, ge=0.0, le=1.0, description="Limit price")


class Order(OrderBase):
    """Full order model with status."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    filled_quantity: int = Field(default=0, description="Filled quantity")
    avg_fill_price: Optional[float] = Field(None, description="Average fill price")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
