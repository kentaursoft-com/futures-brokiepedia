# Futures Brokiepedia - VPS Backend

## Architecture

```
┌─────────────────────────────────────────┐
│           Docker Network                │
│  ┌──────────┐  ┌──────────┐           │
│  │ QuestDB  │  │ ChromaDB │           │
│  │  :8812   │  │  :8000   │           │
│  └────┬─────┘  └────┬─────┘           │
│       │             │                  │
│  ┌────┴─────────────┴─────┐           │
│  │    Trading Daemon       │           │
│  │  ┌───────────────────┐  │           │
│  │  │ Binance WS Feed   │  │           │
│  │  │ LangGraph Agents  │  │           │
│  │  │ ccxt Exchanges    │  │           │
│  │  │ Risk Manager      │  │           │
│  │  └───────────────────┘  │           │
│  └─────────────────────────┘           │
└─────────────────────────────────────────┘
```

## Quick Start

```bash
# 1. Set environment variables
export DEEPSEEK_API_KEY=your_key
export BINANCE_API_KEY=your_key
export BINANCE_SECRET_KEY=your_secret
export TELEGRAM_BOT_TOKEN=your_token

# 2. Start services
docker-compose up -d

# 3. Check logs
docker-compose logs -f daemon
```

## Components

| Service  | Port | Purpose                   |
| -------- | ---- | ------------------------- |
| QuestDB  | 8812 | Time-series OHLCV data    |
| ChromaDB | 8000 | Vector memory for agents  |
| Daemon   | -    | Main trading orchestrator |

## Trading Mode

**Default: PAPER TRADING**

- No real money at risk
- Simulated fills at mid-price
- Full system testing

To switch to live:

```bash
export TRADING_MODE=live
```

## Data Flow

1. Binance WS → Real-time 1m candles
2. QuestDB → Historical data + indicators
3. Regime Classifier → ADX + ATR analysis
4. 6 Department Agents → DeepSeek reasoning
5. Signal Aggregator → Weighted consensus
6. Risk Gate → Position sizing validation
7. Execution Agent → ccxt order submission
8. Telegram → Notification alerts

## Monitoring

```bash
# Daemon logs
docker-compose logs -f daemon

# QuestDB console
open http://localhost:9000

# Health check
curl http://localhost:8000/health
```
