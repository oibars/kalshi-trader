"""Strategy routes for trader skill."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..models.strategy import Strategy, StrategyType
from ..services.strategy_engine import StrategyEngine
from ..services.trading import TradingService

router = APIRouter(prefix="/trader", tags=["trader"])


class StrategyCreate(BaseModel):
    name: str
    strategy_type: StrategyType
    market_filter: Optional[str] = None
    parameters: dict = {}
    enabled: bool = True


def get_strategy_engine() -> StrategyEngine:
    trading_service = TradingService()
    return StrategyEngine(trading_service)


@router.get("/strategies", response_model=List[Strategy])
async def list_strategies(
    service: StrategyEngine = Depends(get_strategy_engine),
):
    """List all trading strategies."""
    return service.list_strategies()


@router.post("/strategies", response_model=Strategy)
async def create_strategy(
    strategy: StrategyCreate,
    service: StrategyEngine = Depends(get_strategy_engine),
):
    """Create a new trading strategy."""
    return service.create_strategy(
        name=strategy.name,
        strategy_type=strategy.strategy_type,
        parameters=strategy.parameters,
    )


@router.get("/strategies/{strategy_id}", response_model=Strategy)
async def get_strategy(
    strategy_id: str,
    service: StrategyEngine = Depends(get_strategy_engine),
):
    """Get strategy details."""
    strategy = service.get_strategy(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy


@router.post("/strategies/{strategy_id}/toggle")
async def toggle_strategy(
    strategy_id: str,
    enabled: bool,
    service: StrategyEngine = Depends(get_strategy_engine),
):
    """Enable or disable a strategy."""
    strategy = service.get_strategy(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    strategy.enabled = enabled
    return {"status": "updated", "strategy_id": strategy_id, "enabled": enabled}


@router.delete("/strategies/{strategy_id}")
async def delete_strategy(
    strategy_id: str,
    service: StrategyEngine = Depends(get_strategy_engine),
):
    """Delete a strategy."""
    if strategy_id not in service.strategies:
        raise HTTPException(status_code=404, detail="Strategy not found")
    del service.strategies[strategy_id]
    return {"status": "deleted", "strategy_id": strategy_id}
