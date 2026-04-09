"""Kalshi Trader - FastAPI application for Railway deployment."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import markets, positions, orders, strategies

app = FastAPI(
    title="Kalshi Trader",
    description="Prediction market trading with multi-agent strategy engine",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(markets.router)
app.include_router(positions.router)
app.include_router(orders.router)
app.include_router(strategies.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "kalshi-trader"}


@app.get("/")
async def root():
    return {"service": "kalshi-trader", "version": "1.0.0", "docs": "/docs"}
