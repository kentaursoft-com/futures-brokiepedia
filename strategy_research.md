# Strategy Research — Futures Brokiepedia

## Active strategy
None — system starting fresh.

## Account context
Exchanges: Binance, Bybit, Bitget, MEXC, KuCoin, BingX, OKX, Gate.io
Risk per trade: 2% of equity
Max concurrent positions: 4
Target timeframes: 15m signal confirmed by 1h

## Starting priorities

Priority 1: Funding rate arbitrage — market neutral, all regimes
  Entry: funding rate > 0.05% per 8h on 2+ exchanges
  Exit: rate drops below 0.01% for 2 consecutive periods

Priority 2: EMA trend following — trending regimes only (ADX > 25)
  20 EMA / 50 EMA crossover on 1h chart
  15m must confirm direction before entry
  Volume must be 1.2x 20-period average

Priority 3: RSI divergence — ranging regimes only (ADX < 20)
  1h divergence setup, 15m RSI cross for entry
  Stop below divergence low

## Rejected strategies
None yet.

## Regime rules — never violate
ADX > 25 = trending → deploy strategies 1 and 2 only
ADX < 20 = ranging → deploy strategies 1 and 3 only
ADX 20-25 = transitional → deploy strategy 1 only, reduce size 50%

## Regime notes
Begin with trending_up and trending_down strategies.
Avoid ranging-only strategies until baseline is established.

## Promotion thresholds
Gate 1 (backtest): win_rate > 55%, Sharpe > 1.2, expectancy > 0
Gate 2 (paper): win_rate > 55% over minimum 50 live trades
Demotion: win_rate drops 8% below promoted baseline (last 50 trades)

## Agent instructions
Read this file before every generation cycle.
After each cycle update: rejected strategies with failure reason,
active strategy metrics when promotion occurs,
regime notes as patterns emerge.
NEVER pause to ask if you should continue.
Fire Telegram alert on: Gate 1 pass, Gate 2 pass, promotion,
demotion, kill-switch trigger, health failure.
