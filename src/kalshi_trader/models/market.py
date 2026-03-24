"""Market model for prediction markets."""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
import uuid


class MarketStatus(str, Enum):
    """Status of a market."""

    OPEN = "open"
    CLOSED = "closed"
    SETTLED = "settled"


class MarketBase(BaseModel):
    """Base model for markets."""

    ticker: str = Field(..., description="Market ticker symbol")
    title: str = Field(..., description="Market title/question")
    category: str = Field(default="general", description="Market category")
    status: MarketStatus = Field(default=MarketStatus.OPEN)
    expiration_date: Optional[datetime] = Field(None, description="Market expiration")
    last_price: float = Field(default=0.5, ge=0.0, le=1.0, description="Last trade price")
    volume_24h: float = Field(default=0.0, description="24h volume")
    open_interest: float = Field(default=0.0, description="Open interest")


class Market(MarketBase):
    """Full market model with ID."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
