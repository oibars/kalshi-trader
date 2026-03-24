"""Strategy model for trading strategies."""

from datetime import datetime
from enum import Enum
from typing import Dict, Any
from pydantic import BaseModel, Field
import uuid


class StrategyType(str, Enum):
    """Type of trading strategy."""

    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    SENTIMENT = "sentiment"
    ARBITRAGE = "arbitrage"


class StrategyBase(BaseModel):
    """Base model for strategies."""

    name: str = Field(..., description="Strategy name")
    type: StrategyType = Field(..., description="Strategy type")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Strategy parameters")
    enabled: bool = Field(default=True, description="Whether strategy is active")


class Strategy(StrategyBase):
    """Full strategy model with performance metrics."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    performance_metrics: Dict[str, Any] = Field(
        default_factory=lambda: {
            "total_trades": 0,
            "win_rate": 0.0,
            "avg_return": 0.0,
            "max_drawdown": 0.0,
            "sharpe_ratio": 0.0,
        }
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
