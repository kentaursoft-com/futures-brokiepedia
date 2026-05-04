// Phase 5 API client extensions for analytics and trading.
import { api } from "./api";

export interface PerformanceReport {
  sharpe_ratio: number;
  sortino_ratio: number;
  max_drawdown: {
    max_drawdown_pct: number;
    peak: number;
    trough: number;
    recovery_needed_pct: number;
  };
  win_rate: {
    win_rate: number;
    winning_trades: number;
    losing_trades: number;
    breakeven_trades: number;
    total: number;
    profit_factor: number;
  };
  expectancy: number;
  r_multiples: {
    avg_r: number;
    r_squared: number;
    best_r: number;
    worst_r: number;
    total_r: number;
  };
  consecutive_stats: {
    max_consecutive_wins: number;
    max_consecutive_losses: number;
    current_streak: number;
  };
  monthly_returns: Array<{
    month: string;
    pnl: number;
    return_pct: number;
    start_equity: number;
    end_equity: number;
  }>;
  total_return_pct: number;
  equity_points: number;
  total_trades: number;
}

export interface RiskStatus {
  current_drawdown_pct: number;
  max_drawdown_pct: number;
  daily_pnl: number;
  equity: number;
  open_positions: number;
  execution_enabled: boolean;
  risk_limits: {
    max_positions: number;
    max_risk_per_trade_pct: number;
    soft_drawdown_pct: number;
    hard_drawdown_pct: number;
  };
}

export interface Trade {
  id: string;
  symbol: string;
  side: string;
  size: number;
  entry_price: number;
  exit_price?: number;
  pnl?: number;
  exchange: string;
  strategy: string;
  duration_seconds?: number;
}

export interface EquityPoint {
  timestamp: number;
  equity: number;
  daily_pnl: number;
}

class Phase5ApiClient {
  async getPerformance(): Promise<PerformanceReport> {
    return api.fetch("/api/v1/performance") as Promise<PerformanceReport>;
  }

  async getEquityCurve(days: number = 30): Promise<EquityPoint[]> {
    const res = await api.fetch(`/api/v1/performance/equity-curve?days=${days}`);
    return (res as any).equity_history || [];
  }

  async getTrades(limit: number = 100): Promise<Trade[]> {
    const res = await api.fetch(`/api/v1/trades?limit=${limit}`);
    return (res as any).trades || [];
  }

  async getTradeStats(days: number = 30): Promise<any> {
    return api.fetch(`/api/v1/trades/stats?days=${days}`);
  }

  async getRiskStatus(): Promise<RiskStatus> {
    return api.fetch("/api/v1/risk/status") as Promise<RiskStatus>;
  }

  async closePosition(positionId: string, reason: string = "manual"): Promise<any> {
    return api.fetch(`/api/v1/positions/${positionId}/close`, {
      method: "POST",
      body: JSON.stringify({ reason }),
    });
  }
}

export const phase5Api = new Phase5ApiClient();
