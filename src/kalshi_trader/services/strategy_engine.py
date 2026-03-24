"""Strategy engine for trading strategies."""

from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
import uuid

from ..models.strategy import Strategy, StrategyType
from ..models.market import Market


@dataclass
class Signal:
    """Trading signal from a strategy."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    strategy_id: str = ""
    market_ticker: str = ""
    signal_type: str = "buy"  # buy, sell, hold
    side: str = "yes"  # yes, no
    confidence: float = 0.5
    price_target: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class StrategyEngine:
    """Engine for running trading strategies."""

    def __init__(self, trading_service):
        self.trading_service = trading_service
        self.strategies: Dict[str, Strategy] = {}
        self.signals: List[Signal] = []

    def create_strategy(
        self,
        name: str,
        strategy_type: StrategyType,
        parameters: Dict[str, Any],
    ) -> Strategy:
        """Create a new strategy."""
        strategy = Strategy(
            name=name,
            type=strategy_type,
            parameters=parameters,
        )
        self.strategies[strategy.id] = strategy
        return strategy

    def get_strategy(self, strategy_id: str) -> Optional[Strategy]:
        """Get a strategy by ID."""
        return self.strategies.get(strategy_id)

    def list_strategies(self, enabled_only: bool = False) -> List[Strategy]:
        """List all strategies."""
        strategies = list(self.strategies.values())
        if enabled_only:
            strategies = [s for s in strategies if s.enabled]
        return strategies

    async def run_strategy(
        self, strategy_id: str, markets: List[Market]
    ) -> List[Signal]:
        """
        Run a strategy on a list of markets.

        Args:
            strategy_id: Strategy to run
            markets: Markets to analyze

        Returns:
            List of generated signals
        """
        strategy = self.strategies.get(strategy_id)
        if not strategy or not strategy.enabled:
            return []

        signals = []
        
        if strategy.type == StrategyType.MOMENTUM:
            signals = await self._run_momentum(strategy, markets)
        elif strategy.type == StrategyType.MEAN_REVERSION:
            signals = await self._run_mean_reversion(strategy, markets)
        elif strategy.type == StrategyType.SENTIMENT:
            signals = await self._run_sentiment(strategy, markets)

        self.signals.extend(signals)
        return signals

    async def _run_momentum(
        self, strategy: Strategy, markets: List[Market]
    ) -> List[Signal]:
        """Run momentum strategy."""
        signals = []
        threshold = strategy.parameters.get("momentum_threshold", 0.05)
        
        for market in markets:
            # Simple momentum: price moving up = buy yes
            if market.volume_24h > 0:
                # Calculate momentum (simplified)
                momentum = (market.last_price - 0.5) / 0.5
                
                if abs(momentum) > threshold:
                    signals.append(
                        Signal(
                            strategy_id=strategy.id,
                            market_ticker=market.ticker,
                            signal_type="buy",
                            side="yes" if momentum > 0 else "no",
                            confidence=min(abs(momentum), 1.0),
                        )
                    )

        return signals

    async def _run_mean_reversion(
        self, strategy: Strategy, markets: List[Market]
    ) -> List[Signal]:
        """Run mean reversion strategy."""
        signals = []
        threshold = strategy.parameters.get("reversion_threshold", 0.3)
        
        for market in markets:
            # Mean reversion: price far from 0.5 = bet on reversion
            deviation = abs(market.last_price - 0.5)
            
            if deviation > threshold:
                signals.append(
                    Signal(
                        strategy_id=strategy.id,
                        market_ticker=market.ticker,
                        signal_type="buy",
                        side="no" if market.last_price > 0.5 else "yes",
                        confidence=deviation,
                        price_target=0.5,
                    )
                )

        return signals

    async def _run_sentiment(
        self, strategy: Strategy, markets: List[Market]
    ) -> List[Signal]:
        """Run sentiment-based strategy (placeholder for LLM integration)."""
        # This would integrate with LLM for sentiment analysis
        return []

    def update_performance(
        self, strategy_id: str, pnl: float, win: bool
    ):
        """Update strategy performance metrics."""
        strategy = self.strategies.get(strategy_id)
        if not strategy:
            return

        metrics = strategy.performance_metrics
        metrics["total_trades"] += 1
        if win:
            wins = metrics.get("wins", 0) + 1
            metrics["wins"] = wins
            metrics["win_rate"] = wins / metrics["total_trades"]
        
        # Update average return
        current_avg = metrics["avg_return"]
        metrics["avg_return"] = (
            current_avg * (metrics["total_trades"] - 1) + pnl
        ) / metrics["total_trades"]

    def get_signals(
        self, strategy_id: Optional[str] = None, limit: int = 100
    ) -> List[Signal]:
        """Get recent signals."""
        signals = self.signals
        if strategy_id:
            signals = [s for s in signals if s.strategy_id == strategy_id]
        return signals[-limit:]
