"""Performance analytics engine for trading metrics."""
import logging
import math
from datetime import datetime
from typing import Dict, List, Optional
from statistics import stdev, mean

logger = logging.getLogger(__name__)

class PerformanceAnalytics:
    """Calculate trading performance metrics."""
    
    def __init__(self):
        self.equity_history: List[dict] = []
        self.trade_history: List[dict] = []
        
    def add_equity_point(self, equity: float, timestamp: Optional[int] = None):
        """Add an equity data point."""
        self.equity_history.append({
            'equity': equity,
            'timestamp': timestamp or int(datetime.now().timestamp())
        })
    
    def add_trade(self, trade: dict):
        """Add a completed trade."""
        self.trade_history.append(trade)
    
    def calculate_sharpe_ratio(self, risk_free_rate: float = 0.02, 
                                periods_per_year: int = 365) -> float:
        """Calculate annualized Sharpe ratio."""
        if len(self.equity_history) < 2:
            return 0.0
        
        # Calculate returns
        returns = []
        for i in range(1, len(self.equity_history)):
            if self.equity_history[i-1]['equity'] > 0:
                r = (self.equity_history[i]['equity'] - self.equity_history[i-1]['equity']) / \
                    self.equity_history[i-1]['equity']
                returns.append(r)
        
        if len(returns) < 2:
            return 0.0
        
        avg_return = mean(returns)
        return_std = stdev(returns)
        
        if return_std == 0:
            return 0.0
        
        # Annualize
        sharpe = (avg_return - risk_free_rate / periods_per_year) / return_std * math.sqrt(periods_per_year)
        
        return round(sharpe, 2)
    
    def calculate_sortino_ratio(self, risk_free_rate: float = 0.02,
                                 periods_per_year: int = 365) -> float:
        """Calculate Sortino ratio (downside deviation only)."""
        if len(self.equity_history) < 2:
            return 0.0
        
        returns = []
        for i in range(1, len(self.equity_history)):
            if self.equity_history[i-1]['equity'] > 0:
                r = (self.equity_history[i]['equity'] - self.equity_history[i-1]['equity']) / \
                    self.equity_history[i-1]['equity']
                returns.append(r)
        
        if len(returns) < 2:
            return 0.0
        
        avg_return = mean(returns)
        
        # Downside deviation (only negative returns)
        downside_returns = [r for r in returns if r < 0]
        if not downside_returns:
            return float('inf')
        
        downside_std = stdev(downside_returns) if len(downside_returns) > 1 else 0
        
        if downside_std == 0:
            return float('inf')
        
        sortino = (avg_return - risk_free_rate / periods_per_year) / downside_std * math.sqrt(periods_per_year)
        
        return round(sortino, 2)
    
    def calculate_max_drawdown(self) -> dict:
        """Calculate maximum drawdown from equity history."""
        if not self.equity_history:
            return {'max_drawdown_pct': 0, 'peak': 0, 'trough': 0}
        
        peak = self.equity_history[0]['equity']
        max_dd = 0.0
        peak_value = peak
        trough_value = peak
        
        for point in self.equity_history:
            equity = point['equity']
            
            if equity > peak:
                peak = equity
            
            dd = (peak - equity) / peak if peak > 0 else 0
            
            if dd > max_dd:
                max_dd = dd
                peak_value = peak
                trough_value = equity
        
        return {
            'max_drawdown_pct': round(max_dd * 100, 2),
            'peak': round(peak_value, 2),
            'trough': round(trough_value, 2),
            'recovery_needed_pct': round((peak_value / trough_value - 1) * 100, 2) if trough_value > 0 else 0
        }
    
    def calculate_win_rate(self, trades: Optional[List[dict]] = None) -> dict:
        """Calculate win rate statistics."""
        trades = trades or self.trade_history
        
        if not trades:
            return {'win_rate': 0, 'winning_trades': 0, 'losing_trades': 0, 'total': 0}
        
        wins = sum(1 for t in trades if t.get('pnl', 0) > 0)
        losses = sum(1 for t in trades if t.get('pnl', 0) < 0)
        breakeven = sum(1 for t in trades if t.get('pnl', 0) == 0)
        total = len(trades)
        
        return {
            'win_rate': round(wins / total * 100, 2) if total > 0 else 0,
            'winning_trades': wins,
            'losing_trades': losses,
            'breakeven_trades': breakeven,
            'total': total,
            'profit_factor': self._calculate_profit_factor(trades)
        }
    
    def _calculate_profit_factor(self, trades: List[dict]) -> float:
        """Calculate profit factor (gross profit / gross loss)."""
        gross_profit = sum(t.get('pnl', 0) for t in trades if t.get('pnl', 0) > 0)
        gross_loss = abs(sum(t.get('pnl', 0) for t in trades if t.get('pnl', 0) < 0))
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
        
        return round(gross_profit / gross_loss, 2)
    
    def calculate_expectancy(self, trades: Optional[List[dict]] = None) -> float:
        """Calculate expected return per trade."""
        trades = trades or self.trade_history
        
        if not trades:
            return 0.0
        
        total_pnl = sum(t.get('pnl', 0) for t in trades)
        return round(total_pnl / len(trades), 2)
    
    def calculate_r_multiples(self, trades: Optional[List[dict]] = None) -> dict:
        """Calculate R-multiples (return relative to risk)."""
        trades = trades or self.trade_history
        
        r_multiples = []
        for trade in trades:
            pnl = trade.get('pnl', 0)
            risk = trade.get('risk_amount', trade.get('entry_price', 1) * 0.02)  # Default 2% risk
            if risk > 0:
                r_multiples.append(pnl / risk)
        
        if not r_multiples:
            return {'avg_r': 0, 'r_squared': 0, 'best_r': 0, 'worst_r': 0}
        
        return {
            'avg_r': round(mean(r_multiples), 2),
            'r_squared': round(sum(r * r for r in r_multiples), 2),
            'best_r': round(max(r_multiples), 2),
            'worst_r': round(min(r_multiples), 2),
            'total_r': round(sum(r_multiples), 2)
        }
    
    def calculate_consecutive_stats(self, trades: Optional[List[dict]] = None) -> dict:
        """Calculate consecutive wins/losses."""
        trades = trades or self.trade_history
        
        if not trades:
            return {'max_consecutive_wins': 0, 'max_consecutive_losses': 0}
        
        max_wins = 0
        max_losses = 0
        current_wins = 0
        current_losses = 0
        
        for trade in trades:
            pnl = trade.get('pnl', 0)
            
            if pnl > 0:
                current_wins += 1
                current_losses = 0
                max_wins = max(max_wins, current_wins)
            elif pnl < 0:
                current_losses += 1
                current_wins = 0
                max_losses = max(max_losses, current_losses)
            else:
                current_wins = 0
                current_losses = 0
        
        return {
            'max_consecutive_wins': max_wins,
            'max_consecutive_losses': max_losses,
            'current_streak': current_wins if current_wins > 0 else -current_losses
        }
    
    def get_monthly_returns(self) -> List[dict]:
        """Get monthly return breakdown."""
        if not self.equity_history:
            return []
        
        monthly_data = {}
        
        for point in self.equity_history:
            dt = datetime.fromtimestamp(point['timestamp'])
            month_key = dt.strftime('%Y-%m')
            
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    'start_equity': point['equity'],
                    'end_equity': point['equity'],
                    'high': point['equity'],
                    'low': point['equity']
                }
            else:
                monthly_data[month_key]['end_equity'] = point['equity']
                monthly_data[month_key]['high'] = max(monthly_data[month_key]['high'], point['equity'])
                monthly_data[month_key]['low'] = min(monthly_data[month_key]['low'], point['equity'])
        
        result = []
        for month, data in sorted(monthly_data.items()):
            pnl = data['end_equity'] - data['start_equity']
            return_pct = (pnl / data['start_equity'] * 100) if data['start_equity'] > 0 else 0
            
            result.append({
                'month': month,
                'pnl': round(pnl, 2),
                'return_pct': round(return_pct, 2),
                'start_equity': round(data['start_equity'], 2),
                'end_equity': round(data['end_equity'], 2)
            })
        
        return result
    
    def get_full_report(self) -> dict:
        """Generate complete performance report."""
        win_stats = self.calculate_win_rate()
        dd_stats = self.calculate_max_drawdown()
        sharpe = self.calculate_sharpe_ratio()
        sortino = self.calculate_sortino_ratio()
        expectancy = self.calculate_expectancy()
        r_multiples = self.calculate_r_multiples()
        consecutive = self.calculate_consecutive_stats()
        monthly = self.get_monthly_returns()
        
        return {
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'max_drawdown': dd_stats,
            'win_rate': win_stats,
            'expectancy': expectancy,
            'r_multiples': r_multiples,
            'consecutive_stats': consecutive,
            'monthly_returns': monthly,
            'total_return_pct': round(
                ((self.equity_history[-1]['equity'] / self.equity_history[0]['equity']) - 1) * 100, 2
            ) if len(self.equity_history) >= 2 else 0,
            'equity_points': len(self.equity_history),
            'total_trades': len(self.trade_history)
        }
