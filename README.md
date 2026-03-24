# Kalshi Trader

Kalshi prediction market trading system with multi-agent strategy orchestration.

## Features
- Order management (place, cancel, track)
- Position tracking
- Market data ingestion
- Multi-agent strategy engine (LangChain)
- Backtesting routes
- Paper trading mode

## Install
```bash
pip install -e .
```

## Environment
```bash
KALSHI_API_KEY=your_key
PAPER_TRADING=true  # set to false for live trading
```

## Usage
```python
from kalshi_trader.services.trading import TradingService
from kalshi_trader.models.order import OrderBase

service = TradingService()
order = await service.place_order(OrderBase(
    market_id="some-market",
    side="yes",
    quantity=10,
    price=0.55
))
```

## API Routes
```python
from kalshi_trader.routes import orders, positions, markets, strategies, backtest
app.include_router(orders.router, prefix="/trader/orders")
```
