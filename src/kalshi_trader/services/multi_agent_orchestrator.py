"""Multi-agent orchestrator for coordinated trading analysis."""

from typing import Dict, List, Any
from dataclasses import dataclass, field
from datetime import datetime
import uuid

from ..models.market import Market


@dataclass
class AgentAnalysis:
    """Analysis from a single agent."""

    agent_id: str
    agent_type: str  # analyst, risk_manager, sentiment_analyst, executioner
    market_ticker: str
    recommendation: str  # buy, sell, hold
    confidence: float
    reasoning: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConsensusDecision:
    """Consensus decision from multi-agent analysis."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    market_ticker: str = ""
    decision: str = "hold"
    confidence: float = 0.0
    participating_agents: List[str] = field(default_factory=list)
    reasoning: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)


class MultiAgentOrchestrator:
    """Orchestrates multiple AI agents for trading decisions."""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.analyses: List[AgentAnalysis] = []
        self.decisions: List[ConsensusDecision] = []

        # Register default agents
        self._register_default_agents()

    def _register_default_agents(self):
        """Register default trading agents."""
        self.agents = {
            "market_analyst": {
                "type": "analyst",
                "role": "Analyze market trends and price action",
                "llm_model": "nemotron-3-super",  # Reasoning model
            },
            "risk_manager": {
                "type": "risk_manager",
                "role": "Assess risk and position sizing",
                "llm_model": "qwen3.5-35b-a3b",  # Fast analysis
            },
            "sentiment_analyst": {
                "type": "sentiment_analyst",
                "role": "Analyze news and social sentiment",
                "llm_model": "qwen3.5-35b-a3b",
            },
            "executioner": {
                "type": "executioner",
                "role": "Determine optimal execution strategy",
                "llm_model": "nemotron-3-nano",  # Lightweight
            },
        }

    def register_agent(
        self,
        agent_id: str,
        agent_type: str,
        role: str,
        llm_model: str,
    ):
        """Register a new agent."""
        self.agents[agent_id] = {
            "type": agent_type,
            "role": role,
            "llm_model": llm_model,
        }

    async def analyze_market(
        self, market: Market, context: Dict[str, Any] = None
    ) -> List[AgentAnalysis]:
        """
        Run multi-agent analysis on a market.

        Args:
            market: Market to analyze
            context: Additional context (news, history, etc.)

        Returns:
            List of agent analyses
        """
        context = context or {}
        analyses = []

        for agent_id, agent_config in self.agents.items():
            analysis = await self._run_agent_analysis(
                agent_id, agent_config, market, context
            )
            analyses.append(analysis)

        self.analyses.extend(analyses)
        return analyses

    async def _run_agent_analysis(
        self,
        agent_id: str,
        agent_config: Dict[str, Any],
        market: Market,
        context: Dict[str, Any],
    ) -> AgentAnalysis:
        """Run analysis for a single agent."""
        # Placeholder for actual LLM integration
        # In real implementation, this would call the LLM with appropriate prompts
        
        # Default analysis based on agent type
        if agent_config["type"] == "analyst":
            recommendation = "hold"
            confidence = 0.5
            reasoning = f"Market {market.ticker} at {market.last_price:.2f}"
        elif agent_config["type"] == "risk_manager":
            recommendation = "hold"
            confidence = 0.7
            reasoning = "Position within risk limits"
        elif agent_config["type"] == "sentiment_analyst":
            recommendation = "hold"
            confidence = 0.4
            reasoning = "Neutral sentiment detected"
        else:
            recommendation = "hold"
            confidence = 0.5
            reasoning = "Awaiting signal"

        return AgentAnalysis(
            agent_id=agent_id,
            agent_type=agent_config["type"],
            market_ticker=market.ticker,
            recommendation=recommendation,
            confidence=confidence,
            reasoning=reasoning,
        )

    async def build_consensus(
        self, analyses: List[AgentAnalysis]
    ) -> ConsensusDecision:
        """
        Build consensus from agent analyses.

        Args:
            analyses: List of agent analyses

        Returns:
            Consensus decision
        """
        if not analyses:
            return ConsensusDecision(decision="hold", confidence=0.0)

        # Weight by agent type
        weights = {
            "analyst": 0.3,
            "risk_manager": 0.3,
            "sentiment_analyst": 0.2,
            "executioner": 0.2,
        }

        # Calculate weighted decision
        buy_score = 0.0
        sell_score = 0.0
        total_weight = 0.0

        for analysis in analyses:
            weight = weights.get(analysis.agent_type, 0.1)
            if analysis.recommendation == "buy":
                buy_score += weight * analysis.confidence
            elif analysis.recommendation == "sell":
                sell_score += weight * analysis.confidence
            total_weight += weight

        # Normalize
        if total_weight > 0:
            buy_score /= total_weight
            sell_score /= total_weight

        # Determine decision
        if buy_score > sell_score and buy_score > 0.5:
            decision = "buy"
            confidence = buy_score
        elif sell_score > buy_score and sell_score > 0.5:
            decision = "sell"
            confidence = sell_score
        else:
            decision = "hold"
            confidence = 1.0 - max(buy_score, sell_score)

        consensus = ConsensusDecision(
            market_ticker=analyses[0].market_ticker,
            decision=decision,
            confidence=confidence,
            participating_agents=[a.agent_id for a in analyses],
            reasoning=f"Consensus from {len(analyses)} agents",
        )

        self.decisions.append(consensus)
        return consensus

    def get_recent_decisions(self, limit: int = 50) -> List[ConsensusDecision]:
        """Get recent consensus decisions."""
        return self.decisions[-limit:]
