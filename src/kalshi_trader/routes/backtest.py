"""Backtest routes for trader skill."""

from typing import List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import datetime

from ..services.strategy_engine import StrategyEngine
from ..services.trading import TradingService

router = APIRouter(prefix="/trader", tags=["trader"])


class BacktestRequest(BaseModel):
    strategy_id: str
    start_date: datetime
    end_date: datetime
    initial_capital: float = 1000.0
    market_filter: Optional[str] = None


class BacktestResult(BaseModel):
    strategy_id: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_capital: float
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    trades: List[dict]


def get_strategy_engine() -> StrategyEngine:
    trading_service = TradingService()
    return StrategyEngine(trading_service)


@router.post("/backtest", response_model=BacktestResult)
async def run_backtest(
    request: BacktestRequest,
    service: StrategyEngine = Depends(get_strategy_engine),
):
    """
    Run a backtest for a strategy.

    - **strategy_id**: Strategy to backtest
    - **start_date**: Backtest start date
    - **end_date**: Backtest end date
    - **initial_capital**: Starting capital
    - **market_filter**: Optional market filter
    """
    # Placeholder implementation
    return BacktestResult(
        strategy_id=request.strategy_id,
        start_date=request.start_date,
        end_date=request.end_date,
        initial_capital=request.initial_capital,
        final_capital=request.initial_capital,
        total_return=0.0,
        sharpe_ratio=0.0,
        max_drawdown=0.0,
        win_rate=0.0,
        total_trades=0,
        trades=[],
    )


@router.get("/backtest/results")
async def list_backtest_results(
    strategy_id: Optional[str] = None,
    service: StrategyEngine = Depends(get_strategy_engine),
):
    """List historical backtest results."""
    return {"results": [], "strategy_id": strategy_id}
