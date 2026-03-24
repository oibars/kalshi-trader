"""Position routes for trader skill."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException

from ..models.position import Position
from ..services.trading import TradingService

router = APIRouter(prefix="/trader", tags=["trader"])


def get_trading_service() -> TradingService:
    return TradingService()


@router.get("/positions", response_model=List[Position])
async def list_positions(
    service: TradingService = Depends(get_trading_service),
):
    """List all current positions."""
    return await service.get_positions()


@router.get("/positions/{market_id}", response_model=Position)
async def get_position(
    market_id: str,
    service: TradingService = Depends(get_trading_service),
):
    """Get details for a specific position by market ID."""
    position = await service.get_position(market_id)
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    return position
