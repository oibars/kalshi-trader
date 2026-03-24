"""Trader routes."""
from .markets import router as markets_router
from .positions import router as positions_router
from .orders import router as orders_router
from .strategies import router as strategies_router
from .backtest import router as backtest_router

routers = [
    markets_router,
    positions_router,
    orders_router,
    strategies_router,
    backtest_router,
]

__all__ = ["routers"]
