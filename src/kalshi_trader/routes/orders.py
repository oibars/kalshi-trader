"""Order routes for trader skill."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..models.order import Order, OrderType, OrderBase
from ..services.trading import TradingService

router = APIRouter(prefix="/trader", tags=["trader"])


class OrderCreate(BaseModel):
    market_ticker: str
    side: str  # "yes" or "no"
    quantity: int
    price: Optional[float] = None  # Required for limit orders
    order_type: OrderType = OrderType.MARKET
    dry_run: bool = False


def get_trading_service() -> TradingService:
    return TradingService()


@router.post("/orders", response_model=Order)
async def create_order(
    order: OrderCreate,
    service: TradingService = Depends(get_trading_service),
):
    """
    Create a new order.

    - **market_ticker**: Market to trade on
    - **side**: Buy YES or NO
    - **quantity**: Number of contracts
    - **price**: Limit price (0-1)
    - **order_type**: Market or Limit
    - **dry_run**: Simulate without executing
    """
    if order.order_type == OrderType.LIMIT and order.price is None:
        raise HTTPException(status_code=400, detail="Limit orders require a price")

    order_data = OrderBase(
        market_id=order.market_ticker,
        side=order.side,
        quantity=order.quantity,
        order_type=order.order_type,
        price=order.price,
    )
    result = await service.place_order(order_data)
    return result


@router.get("/orders", response_model=List[Order])
async def list_orders(
    market_ticker: Optional[str] = None,
    service: TradingService = Depends(get_trading_service),
):
    """List orders, optionally filtered by market."""
    return await service.list_orders(market_id=market_ticker)


@router.delete("/orders/{order_id}")
async def cancel_order(
    order_id: str,
    service: TradingService = Depends(get_trading_service),
):
    """Cancel an open order."""
    result = await service.cancel_order(order_id)
    if not result:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"status": "cancelled", "order_id": order_id}
