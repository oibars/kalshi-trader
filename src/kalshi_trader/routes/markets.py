"""Market routes for trader skill."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException

from ..models.market import Market, MarketStatus
from ..services.market_data import MarketDataService

router = APIRouter(prefix="/trader", tags=["trader"])


def get_market_service() -> MarketDataService:
    return MarketDataService()


@router.get("/markets", response_model=List[Market])
async def list_markets(
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[MarketStatus] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=200, description="Max results"),
    service: MarketDataService = Depends(get_market_service),
):
    """
    List available prediction markets.

    - **category**: Filter by market category (politics, finance, sports, etc.)
    - **status**: Filter by market status (open, closed, settled)
    - **limit**: Maximum number of results
    """
    return await service.get_markets(category=category, status=status, limit=limit)


@router.get("/markets/{ticker}", response_model=Market)
async def get_market(
    ticker: str,
    service: MarketDataService = Depends(get_market_service),
):
    """Get details for a specific market by ticker."""
    market = await service.get_market(ticker)
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")
    return market


@router.get("/markets/{ticker}/price")
async def get_market_price(
    ticker: str,
    service: MarketDataService = Depends(get_market_service),
):
    """Get current price for a market."""
    price = await service.get_market_price(ticker)
    return {"ticker": ticker, "price": price}


@router.get("/markets/{ticker}/orderbook")
async def get_orderbook(
    ticker: str,
    service: MarketDataService = Depends(get_market_service),
):
    """Get order book for a market."""
    return await service.get_orderbook(ticker)
