"""LangGraph department agents for Futures Brokiepedia — with external signal support.

Each department can receive signals from external Discord agents via unique API keys.
External signals take priority over internal LLM analysis for that department.
"""

import json
import logging
from typing import Dict, List, Optional, TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from .external_signals import ExternalSignalStore

logger = logging.getLogger(__name__)


class AgentVerdict(TypedDict):
    department: str
    direction: str  # "long" | "short" | "flat"
    confidence: float
    timeframe: str
    regime_tag: str
    reasoning: str
    source: str  # "internal" (DeepSeek) | "external" (Discord agent)


class AnalysisState(TypedDict):
    symbol: str
    market_data: dict
    regime: str
    verdicts: List[AgentVerdict]
    aggregated_signal: dict
    should_trade: bool
    risk_check_passed: bool


class DepartmentAgents:
    """6 department analysis agents using DeepSeek + external signal fallback."""

    DEPARTMENT_WEIGHTS = {
        'Quantitative': 0.30,
        'Technical': 0.25,
        'Sentiment': 0.20,
        'Fundamental': 0.15,
        'Statistical': 0.10,
        'Qualitative': 0.00,  # Veto only
    }

    DEPARTMENT_SLUGS = {
        'Quantitative': 'quantitative',
        'Technical': 'technical',
        'Sentiment': 'sentiment',
        'Fundamental': 'fundamental',
        'Statistical': 'statistical',
        'Qualitative': 'qualitative',
    }

    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com",
                 signal_store: Optional[ExternalSignalStore] = None):
        self.llm = ChatOpenAI(
            model="deepseek-reasoner",  # V4 Pro
            api_key=api_key,
            base_url=base_url,
            temperature=0.1
        )

        self.fast_llm = ChatOpenAI(
            model="deepseek-chat",  # V4 Flash
            api_key=api_key,
            base_url=base_url,
            temperature=0.2
        )

        self.signal_store = signal_store or ExternalSignalStore()
        self.graph = self._build_graph()

    def _get_external_verdict(self, department: str) -> Optional[AgentVerdict]:
        """Check for an external signal from Discord agents."""
        signal = self.signal_store.get_latest_signal(department)
        if signal:
            verdict = AgentVerdict(
                department=department,
                direction=signal.get('direction', 'flat'),
                confidence=float(signal.get('confidence', 0.5)),
                timeframe=signal.get('timeframe', '1h'),
                regime_tag="external",
                reasoning=f"[External - {signal.get('source', 'discord')}]: {signal.get('reasoning', 'No reasoning provided')}",
                source="external"
            )
            # Mark consumed
            self.signal_store.mark_consumed(department, signal['id'])
            logger.info(f"Using EXTERNAL signal for {department}: {verdict['direction']} (conf: {verdict['confidence']})")
            return verdict
        return None

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph StateGraph with 6 departments."""
        workflow = StateGraph(AnalysisState)

        # Add department nodes (run in parallel)
        workflow.add_node("fundamental", self._fundamental_analysis)
        workflow.add_node("technical", self._technical_analysis)
        workflow.add_node("sentiment", self._sentiment_analysis)
        workflow.add_node("quantitative", self._quantitative_analysis)
        workflow.add_node("statistical", self._statistical_analysis)
        workflow.add_node("qualitative", self._qualitative_analysis)
        workflow.add_node("aggregator", self._aggregate_signals)
        workflow.add_node("risk_gate", self._risk_gate)

        # Set entry point
        workflow.set_entry_point("fundamental")

        # Parallel execution for all departments
        for dept in ["fundamental", "technical", "sentiment",
                     "quantitative", "statistical", "qualitative"]:
            workflow.add_edge(dept, "aggregator")

        workflow.add_edge("aggregator", "risk_gate")
        workflow.add_edge("risk_gate", END)

        return workflow.compile()

    async def _fundamental_analysis(self, state: AnalysisState) -> AnalysisState:
        """Fundamental analysis: macro context, on-chain metrics."""
        # Check for external signal first
        external = self._get_external_verdict("Fundamental")
        if external:
            state['verdicts'].append(external)
            return state

        prompt = f"""
        You are the Fundamental Analysis Department for a crypto futures trading system.

        Asset: {state['symbol']}
        Current Regime: {state['regime']}

        Analyze the fundamental outlook considering:
        1. Macro environment (Fed policy, dollar strength)
        2. On-chain metrics (if applicable)
        3. Adoption trends and network growth
        4. Regulatory landscape

        Output a JSON verdict:
        {{
            "department": "Fundamental",
            "direction": "long|short|flat",
            "confidence": 0.0-1.0,
            "timeframe": "short|medium|long",
            "regime_tag": "trending_up|trending_down|ranging|volatile",
            "reasoning": "Brief explanation"
        }}
        """

        try:
            response = await self.llm.ainvoke([SystemMessage(content=prompt)])
            verdict = json.loads(response.content)
            verdict['source'] = 'internal'
            state['verdicts'].append(verdict)
        except Exception as e:
            logger.error(f"Fundamental analysis error: {e}")
            state['verdicts'].append(self._neutral_verdict("Fundamental"))

        return state

    async def _technical_analysis(self, state: AnalysisState) -> AnalysisState:
        """Technical analysis: price action, indicators, multi-timeframe."""
        # Check for external signal first
        external = self._get_external_verdict("Technical")
        if external:
            state['verdicts'].append(external)
            return state

        data = state['market_data']

        prompt = f"""
        You are the Technical Analysis Department.

        Asset: {state['symbol']}
        Price: {data.get('close', 'N/A')}
        EMA20: {data.get('ema20', 'N/A')}
        EMA50: {data.get('ema50', 'N/A')}
        RSI: {data.get('rsi', 'N/A')}
        ATR: {data.get('atr', 'N/A')}
        Volume: {data.get('volume', 'N/A')}

        Rules:
        - 15m must agree with 1h before signaling long/short
        - Volume must be 1.2x average for confirmation
        - ADX > 25 for trend, < 20 for range

        Output JSON verdict with direction, confidence, reasoning.
        """

        try:
            response = await self.llm.ainvoke([SystemMessage(content=prompt)])
            verdict = json.loads(response.content)
            verdict['source'] = 'internal'
            state['verdicts'].append(verdict)
        except Exception as e:
            logger.error(f"Technical analysis error: {e}")
            state['verdicts'].append(self._neutral_verdict("Technical"))

        return state

    async def _sentiment_analysis(self, state: AnalysisState) -> AnalysisState:
        """Sentiment analysis: funding rates, social data, options flow."""
        # Check for external signal first
        external = self._get_external_verdict("Sentiment")
        if external:
            state['verdicts'].append(external)
            return state

        prompt = f"""
        You are the Sentiment Analysis Department.

        Asset: {state['symbol']}

        Analyze market sentiment considering:
        1. Funding rate direction and magnitude
        2. Social media sentiment (Twitter/Reddit)
        3. Options flow (if available)
        4. Fear & Greed index implications

        High funding rate on longs = bearish contrarian signal
        Negative funding = bullish contrarian signal

        Output JSON verdict.
        """

        try:
            response = await self.fast_llm.ainvoke([SystemMessage(content=prompt)])
            verdict = json.loads(response.content)
            verdict['source'] = 'internal'
            state['verdicts'].append(verdict)
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            state['verdicts'].append(self._neutral_verdict("Sentiment"))

        return state

    async def _quantitative_analysis(self, state: AnalysisState) -> AnalysisState:
        """Quantitative: probability models, Kelly criterion."""
        # Check for external signal first
        external = self._get_external_verdict("Quantitative")
        if external:
            state['verdicts'].append(external)
            return state

        prompt = f"""
        You are the Quantitative Analysis Department.

        Asset: {state['symbol']}
        Regime: {state['regime']}

        Apply quantitative methods:
        1. Historical win rate for current setup
        2. Kelly criterion position sizing
        3. Expected value calculation
        4. Monte Carlo simulation outlook

        Weight: 30% (highest influence)

        Output JSON verdict with confidence based on statistical edge.
        """

        try:
            response = await self.llm.ainvoke([SystemMessage(content=prompt)])
            verdict = json.loads(response.content)
            verdict['source'] = 'internal'
            state['verdicts'].append(verdict)
        except Exception as e:
            logger.error(f"Quantitative analysis error: {e}")
            state['verdicts'].append(self._neutral_verdict("Quantitative"))

        return state

    async def _statistical_analysis(self, state: AnalysisState) -> AnalysisState:
        """Statistical: drawdown risk, correlation, regime classification."""
        # Check for external signal first
        external = self._get_external_verdict("Statistical")
        if external:
            state['verdicts'].append(external)
            return state

        prompt = f"""
        You are the Statistical Analysis Department.

        Asset: {state['symbol']}

        Evaluate:
        1. Drawdown risk (VaR, expected shortfall)
        2. Correlation with portfolio
        3. Volatility regime classification
        4. Mean reversion probability

        Block trade if correlation > 0.7 with existing positions.

        Output JSON verdict with risk assessment.
        """

        try:
            response = await self.fast_llm.ainvoke([SystemMessage(content=prompt)])
            verdict = json.loads(response.content)
            verdict['source'] = 'internal'
            state['verdicts'].append(verdict)
        except Exception as e:
            logger.error(f"Statistical analysis error: {e}")
            state['verdicts'].append(self._neutral_verdict("Statistical"))

        return state

    async def _qualitative_analysis(self, state: AnalysisState) -> AnalysisState:
        """Qualitative: portfolio synthesis, CIO-level veto."""
        # Check for external signal first
        external = self._get_external_verdict("Qualitative")
        if external:
            state['verdicts'].append(external)
            return state

        verdicts_summary = "\n".join([
            f"{v['department']}: {v['direction']} (conf: {v['confidence']})"
            for v in state['verdicts']
        ])

        prompt = f"""
        You are the Chief Investment Officer (Qualitative Department).

        Current verdicts from other departments:
        {verdicts_summary}

        Your role:
        1. Synthesize all department views
        2. Apply qualitative judgment
        3. VETO power: can block any trade if reasoning is strong
        4. Cannot initiate trades, only approve/block

        Output JSON verdict. Set direction to "flat" to veto.
        """

        try:
            response = await self.llm.ainvoke([SystemMessage(content=prompt)])
            verdict = json.loads(response.content)
            verdict['source'] = 'internal'
            state['verdicts'].append(verdict)
        except Exception as e:
            logger.error(f"Qualitative analysis error: {e}")
            state['verdicts'].append(self._neutral_verdict("Qualitative"))

        return state

    async def _aggregate_signals(self, state: AnalysisState) -> AnalysisState:
        """Weighted signal aggregation with external signal awareness."""
        verdicts = state['verdicts']

        # Log signal sources
        internal = sum(1 for v in verdicts if v.get('source') == 'internal')
        external = sum(1 for v in verdicts if v.get('source') == 'external')
        if external > 0:
            logger.info(f"Aggregating {len(verdicts)} verdicts ({internal} internal, {external} external)")

        # Calculate weighted scores
        long_score = 0.0
        short_score = 0.0
        total_weight = 0.0

        for verdict in verdicts:
            dept = verdict['department']
            weight = self.DEPARTMENT_WEIGHTS.get(dept, 0)
            confidence = verdict.get('confidence', 0)
            direction = verdict.get('direction', 'flat')

            if direction == 'long':
                long_score += weight * confidence
            elif direction == 'short':
                short_score += weight * confidence

            total_weight += weight

        # Normalize
        if total_weight > 0:
            long_score /= total_weight
            short_score /= total_weight

        # Determine aggregated signal
        net_score = long_score - short_score
        confidence = abs(net_score)

        if confidence < 0.55:
            direction = "flat"
        elif net_score > 0:
            direction = "long"
        else:
            direction = "short"

        # Conflict rule: if top-2 departments disagree, reduce size
        top_two = sorted(verdicts,
                        key=lambda x: self.DEPARTMENT_WEIGHTS.get(x['department'], 0),
                        reverse=True)[:2]

        size_reduction = 1.0
        if len(top_two) >= 2 and top_two[0]['direction'] != top_two[1]['direction']:
            size_reduction = 0.5

        state['aggregated_signal'] = {
            'direction': direction,
            'confidence': confidence,
            'long_score': long_score,
            'short_score': short_score,
            'size_reduction': size_reduction,
            'verdicts': verdicts,
            'external_signals_used': external,
            'internal_signals_used': internal,
        }

        state['should_trade'] = direction != "flat" and confidence >= 0.55

        source_tag = f"[{external} external / {internal} internal]" if external > 0 else "[all internal]"
        logger.info(f"Aggregated signal: {direction} (conf: {confidence:.2f}) {source_tag}")

        return state

    async def _risk_gate(self, state: AnalysisState) -> AnalysisState:
        """Risk gate validation."""
        # Placeholder for risk checks
        state['risk_check_passed'] = state['should_trade']
        return state

    def _neutral_verdict(self, department: str) -> AgentVerdict:
        """Create neutral verdict for error cases."""
        return {
            "department": department,
            "direction": "flat",
            "confidence": 0.0,
            "timeframe": "none",
            "regime_tag": "unknown",
            "reasoning": "Analysis failed, defaulting to neutral",
            "source": "internal"
        }

    async def analyze(self, symbol: str, market_data: dict,
                     regime: str = "unknown") -> dict:
        """Run full analysis cycle with external signal injection."""
        initial_state = AnalysisState(
            symbol=symbol,
            market_data=market_data,
            regime=regime,
            verdicts=[],
            aggregated_signal={},
            should_trade=False,
            risk_check_passed=False
        )

        result = await self.graph.ainvoke(initial_state)
        return result
