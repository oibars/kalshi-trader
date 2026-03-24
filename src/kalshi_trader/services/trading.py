"""Trading service for executing orders."""

import os
from typing import Dict, List, Optional
from datetime import datetime

from ..models.order import Order, OrderStatus, OrderBase
from ..models.position import Position, PositionSide


class TradingService:
    """Service for executing trades and managing positions."""

    def __init__(self):
        self.kalshi_api_key = os.getenv("KALSHI_API_KEY")
        self.kalshi_base_url = "https://trading-api.kalshi.com/v1"
        self.orders: Dict[str, Order] = {}
        self.positions: Dict[str, Position] = {}
        self.paper_trading = os.getenv("PAPER_TRADING", "true").lower() == "true"

    async def place_order(self, order_data: OrderBase) -> Order:
        """
        Place a new order.

        Args:
            order_data: Order parameters

        Returns:
            Created Order object
        """
        order = Order(**order_data.model_dump())

        if self.paper_trading:
            # Simulate immediate fill for paper trading
            order.status = OrderStatus.FILLED
            order.filled_quantity = order.quantity
            order.avg_fill_price = order.price or 0.5
        else:
            # Real trading via Kalshi API
            order = await self._place_kalshi_order(order)

        self.orders[order.id] = order

        # Update position
        if order.status == OrderStatus.FILLED:
            await self._update_position(order)

        return order

    async def cancel_order(self, order_id: str) -> Optional[Order]:
        """Cancel an order."""
        order = self.orders.get(order_id)
        if not order:
            return None

        if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED]:
            return order

        if not self.paper_trading:
            await self._cancel_kalshi_order(order)

        order.status = OrderStatus.CANCELLED
        return order

    async def get_order(self, order_id: str) -> Optional[Order]:
        """Get an order by ID."""
        return self.orders.get(order_id)

    async def list_orders(
        self, market_id: Optional[str] = None, status: Optional[OrderStatus] = None
    ) -> List[Order]:
        """List orders, optionally filtered."""
        orders = list(self.orders.values())
        if market_id:
            orders = [o for o in orders if o.market_id == market_id]
        if status:
            orders = [o for o in orders if o.status == status]
        return sorted(orders, key=lambda o: o.created_at, reverse=True)

    async def get_positions(self) -> List[Position]:
        """Get all positions."""
        return list(self.positions.values())

    async def get_position(self, market_id: str) -> Optional[Position]:
        """Get position for a market."""
        return self.positions.get(market_id)

    async def _update_position(self, order: Order):
        """Update position after order fill."""
        pos_key = f"{order.market_id}_{order.side}"
        
        if pos_key in self.positions:
            pos = self.positions[pos_key]
            total_cost = (pos.quantity * pos.avg_price) + (
                order.filled_quantity * (order.avg_fill_price or 0)
            )
            pos.quantity += order.filled_quantity
            pos.avg_price = total_cost / pos.quantity if pos.quantity > 0 else 0
            pos.updated_at = datetime.utcnow()
        else:
            self.positions[pos_key] = Position(
                market_id=order.market_id,
                side=PositionSide.YES if order.side == "yes" else PositionSide.NO,
                quantity=order.filled_quantity,
                avg_price=order.avg_fill_price or 0,
            )

    async def _place_kalshi_order(self, order: Order) -> Order:
        """Place order via Kalshi API."""
        import httpx

        headers = {"Authorization": f"Bearer {self.kalshi_api_key}"}
        payload = {
            "ticker": order.market_id,
            "side": order.side,
            "quantity": order.quantity,
            "type": order.order_type.value,
        }
        if order.price:
            payload["price"] = order.price

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.post(
                    f"{self.kalshi_base_url}/orders",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                order.status = OrderStatus(data.get("status", "pending"))
                order.filled_quantity = data.get("filled_quantity", 0)
                order.avg_fill_price = data.get("avg_fill_price")
            except Exception:
                order.status = OrderStatus.REJECTED

        return order

    async def _cancel_kalshi_order(self, order: Order):
        """Cancel order via Kalshi API."""
        import httpx

        headers = {"Authorization": f"Bearer {self.kalshi_api_key}"}

        async with httpx.AsyncClient(timeout=30) as client:
            await client.delete(
                f"{self.kalshi_base_url}/orders/{order.id}",
                headers=headers,
            )
