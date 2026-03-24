"""Position model for trading positions."""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class PositionSide(str, Enum):
    """Side of a position."""

    YES = "yes"
    NO = "no"


class PositionBase(BaseModel):
    """Base model for positions."""

    market_id: str = Field(..., description="Market ID")
    side: PositionSide = Field(..., description="Position side (yes/no)")
    quantity: int = Field(..., ge=0, description="Number of contracts")
    avg_price: float = Field(..., ge=0.0, le=1.0, description="Average entry price")


class Position(PositionBase):
    """Full position model with calculated values."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    current_value: float = Field(default=0.0, description="Current position value")
    pnl: float = Field(default=0.0, description="Profit/Loss")
    opened_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def calculate_pnl(self, current_price: float) -> float:
        """Calculate PnL based on current price."""
        if self.side == PositionSide.YES:
            self.current_value = self.quantity * current_price
            self.pnl = self.current_value - (self.quantity * self.avg_price)
        else:
            self.current_value = self.quantity * (1 - current_price)
            self.pnl = self.current_value - (self.quantity * (1 - self.avg_price))
        return self.pnl

    class Config:
        from_attributes = True
