"""Market data service for fetching market information."""

import os
from typing import List, Optional, Dict, Any
from datetime import datetime
import httpx

from ..models.market import Market, MarketStatus


class MarketDataService:
    """Service for fetching market data from Kalshi and other exchanges."""

    def __init__(self):
        self.kalshi_api_key = os.getenv("KALSHI_API_KEY")
        self.kalshi_base_url = "https://trading-api.kalshi.com/v1"
        self.timeout = 30
        self._markets: Dict[str, Market] = {}

    async def get_markets(
        self,
        category: Optional[str] = None,
        status: Optional[MarketStatus] = None,
        limit: int = 50,
    ) -> List[Market]:
        """
        Get available markets.

        Args:
            category: Filter by category
            status: Filter by status
            limit: Maximum number of results

        Returns:
            List of Market objects
        """
        # Try Kalshi API
        markets = await self._fetch_kalshi_markets(category, limit)
        
        # Filter by status if provided
        if status:
            markets = [m for m in markets if m.status == status]
        
        # Cache markets
        for m in markets:
            self._markets[m.ticker] = m
        
        return markets

    async def get_market(self, ticker: str) -> Optional[Market]:
        """Get a specific market by ticker."""
        if ticker in self._markets:
            return self._markets[ticker]

        # Fetch from API and cache
        _ = await self.get_markets()
        return self._markets.get(ticker)

    async def get_market_price(self, ticker: str) -> Optional[float]:
        """Get current price for a market."""
        market = await self.get_market(ticker)
        return market.last_price if market else None

    async def _fetch_kalshi_markets(
        self, category: Optional[str], limit: int
    ) -> List[Market]:
        """Fetch markets from Kalshi API."""
        headers = {}
        if self.kalshi_api_key:
            headers["Authorization"] = f"Bearer {self.kalshi_api_key}"

        params = {"limit": limit}
        if category:
            params["category"] = category

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.kalshi_base_url}/markets",
                    headers=headers,
                    params=params,
                )
                response.raise_for_status()
                data = response.json()
            except Exception:
                return []

        markets = []
        for item in data.get("markets", []):
            status = MarketStatus.OPEN
            if item.get("closed", False):
                status = MarketStatus.CLOSED
            elif item.get("settled", False):
                status = MarketStatus.SETTLED

            markets.append(
                Market(
                    ticker=item.get("ticker", ""),
                    title=item.get("title", ""),
                    category=item.get("category", "general"),
                    status=status,
                    expiration_date=datetime.fromisoformat(item["expiration_date"])
                    if item.get("expiration_date")
                    else None,
                    last_price=item.get("last_price", 0.5),
                    volume_24h=item.get("volume_24h", 0.0),
                    open_interest=item.get("open_interest", 0.0),
                )
            )

        return markets

    async def get_orderbook(self, ticker: str) -> Dict[str, Any]:
        """Get orderbook for a market."""
        headers = {}
        if self.kalshi_api_key:
            headers["Authorization"] = f"Bearer {self.kalshi_api_key}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.kalshi_base_url}/markets/{ticker}/orderbook",
                    headers=headers,
                )
                response.raise_for_status()
                return response.json()
            except Exception:
                return {"bids": [], "asks": []}

    async def check_api(self) -> bool:
        """Check if Kalshi API is available."""
        return bool(self.kalshi_api_key)
