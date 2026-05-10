// Shared types for Futures Brokiepedia

export interface AgentVerdict {
  department: string;
  name?: string;
  direction: "long" | "short" | "flat";
  confidence: number;
  timeframe: string;
  regime_tag: string;
  reasoning: string;
  lastRun?: string;
}

export interface Position {
  id: string;
  symbol: string;
  side: "long" | "short";
  size: number;
  entry_price: number;
  mark_price: number;
  unrealized_pnl: number;
  exchange: string;
  strategy: string;
}

export interface Strategy {
  id: string;
  name: string;
  status: "draft" | "backtesting" | "paper" | "live" | "rejected" | "demoted";
  win_rate: number;
  sharpe: number;
  expectancy: number;
  regime: string;
  days_live: number;
}

export interface DashboardState {
  systemStatus: "live" | "paper" | "halted";
  activeAsset: string;
  regime: string;
  lastSync: number;
  todayPnl: number;
  unrealizedPnl: number;
  equity: number;
  dailyDrawdown: number;
  executionEnabled: boolean;
  killSwitchTriggered: boolean;
  departments: AgentVerdict[];
  positions: Position[];
  activeStrategy: Strategy | null;
  health: SystemHealth;
  binance_ws_connected?: boolean;
  langgraph_running?: boolean;
  agents_initialized?: boolean;
  evolution_loop_running?: boolean;
}

export interface SystemHealth {
  vps: boolean;
  binance: boolean;
  deepseek: boolean;
  turso: boolean;
  exchanges: number;
}

export interface Trade {
  id: string;
  strategy_id: string;
  exchange: string;
  symbol: string;
  side: "long" | "short";
  entry_price: number;
  exit_price?: number;
  size: number;
  pnl?: number;
  fee: number;
  regime: string;
  paper: boolean;
  created_at: number;
}

export interface BacktestResult {
  id: string;
  strategy_id: string;
  win_rate: number;
  sharpe: number;
  max_drawdown: number;
  expectancy: number;
  total_trades: number;
  fee_adjusted: boolean;
  regime: string;
  passed_gate: boolean;
  created_at: number;
}

export interface RiskGate {
  max_risk_per_trade_pct: number;
  max_concurrent_positions: number;
  soft_drawdown_pct: number;
  hard_drawdown_pct: number;
  max_leverage: number;
  min_reward_risk_ratio: number;
  correlation_block_threshold: number;
}

export const RISK_PARAMETERS: RiskGate = {
  max_risk_per_trade_pct: 2.0,
  max_concurrent_positions: 4,
  soft_drawdown_pct: 3.0,
  hard_drawdown_pct: 6.0,
  max_leverage: 5,
  min_reward_risk_ratio: 1.5,
  correlation_block_threshold: 0.7,
};

export interface DepartmentWeight {
  department: string;
  weight: number;
  can_veto: boolean;
}

export const DEPARTMENT_WEIGHTS: DepartmentWeight[] = [
  { department: "Quantitative", weight: 0.3, can_veto: false },
  { department: "Technical", weight: 0.25, can_veto: false },
  { department: "Sentiment", weight: 0.2, can_veto: false },
  { department: "Fundamental", weight: 0.15, can_veto: false },
  { department: "Statistical", weight: 0.1, can_veto: false },
  { department: "Qualitative", weight: 0.0, can_veto: true },
];
