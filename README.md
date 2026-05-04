# Futures Brokiepedia

AI-powered crypto futures trading platform with autonomous strategy evolution.

**Status: Phase 5 Complete ✅** — Live Trading Integration & Advanced Analytics

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Cloudflare    │────▶│   Cloudflare     │────▶│   VPS Daemon    │
│   Pages (UI)    │     │   Worker (API)   │     │   (Python)      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │                           │
                               ▼                           ▼
                        ┌─────────────┐            ┌─────────────┐
                        │   KV / D1   │            │  QuestDB    │
                        │             │            │  ChromaDB   │
                        └─────────────┘            └─────────────┘
```

### Components

- **Frontend:** SvelteKit + Tailwind CSS + shadcn-svelte → Cloudflare Pages
- **Edge API:** Cloudflare Workers (TypeScript) — CORS, rate limiting, auth
- **Edge State:** Cloudflare KV (5s polling from frontend)
- **Edge Queue:** Cloudflare Queues (agent task routing)
- **Edge Audit:** Cloudflare D1 (audit log, sessions)
- **Primary DB:** Turso (libSQL) — strategies, trades, ledger, prompts
- **Time-series DB:** QuestDB (OHLCV, indicators, funding rates)
- **Vector Memory:** ChromaDB (agent reasoning history)
- **AI Agents:** LangGraph + DeepSeek V4 Pro/Flash (6 departments)
- **Exchange Layer:** ccxt (8 exchanges normalized)
- **Notifications:** Telegram Bot API

## Quick Start

```bash
# Install dependencies
npm install

# Run dev server
npm run dev

# Type check
npm run check

# Build for production
npm run build
```

## Project Structure

```
├── src/                          # Frontend (SvelteKit)
│   ├── lib/
│   │   ├── utils.ts              # Tailwind cn() helper
│   │   ├── types.ts              # Shared TypeScript types
│   │   ├── stores.ts             # Svelte stores
│   │   ├── api.ts                # API client
│   │   ├── auth.ts               # WebAuthn passkey utils
│   │   └── websocket.ts          # Binance WebSocket
│   ├── routes/
│   │   ├── +layout.svelte        # Root layout
│   │   ├── +page.svelte          # Dashboard
│   │   └── auth/+page.svelte     # Auth page
│   └── app.css                   # Global styles
├── workers/
│   └── api/                      # Cloudflare Worker
│       ├── src/index.ts          # Worker entry
│       └── wrangler.toml         # Worker config
├── vps/                          # VPS Backend (Docker)
│   ├── daemon/                   # Python trading daemon
│   │   ├── src/
│   │   │   ├── main.py           # Daemon entry
│   │   │   ├── api/server.py     # FastAPI server
│   │   │   ├── agents/           # AI agents
│   │   │   ├── exchanges/        # Exchange layer
│   │   │   ├── ingestion/        # Data ingestion
│   │   │   └── notifications/    # Telegram alerts
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── docker-compose.yml        # Development
│   ├── docker-compose.prod.yml   # Production
│   └── config/                   # Config files
├── schema/
│   ├── turso.sql                 # Turso table definitions
│   └── questdb.sql               # QuestDB table definitions
├── scripts/                      # Deployment scripts
│   ├── deploy-worker.sh
│   ├── deploy-frontend.sh
│   ├── setup-vps.sh
│   ├── health-check.sh
│   └── test-integration.sh
├── .env.example                  # Environment template
└── package.json
```

## Phase 4: What's New

### Production Features

- ✅ **Rate Limiting** — 120 req/min per IP on daemon API
- ✅ **CORS Security** — Restricted to production domains
- ✅ **Health Checks** — Docker health checks for all services
- ✅ **Monitoring** — Prometheus configuration (optional)
- ✅ **Deployment Scripts** — Automated deployment for all components
- ✅ **Integration Tests** — End-to-end test suite
- ✅ **VPS Setup** — Systemd service configuration

### Security Enhancements

- ✅ Request logging middleware
- ✅ Rate limiting middleware
- ✅ CORS restricted to known origins
- ✅ Passkey authentication for kill-switch
- ✅ All secrets externalized

## Phase 5: Live Trading Integration & Advanced Analytics

### Trading Features

- ✅ **Turso Integration** — Persistent storage for all trades and strategies
- ✅ **Live Execution** — Real order execution (paper/live modes)
- ✅ **Position Tracking** — Real-time P&L and mark price updates
- ✅ **Performance Analytics** — Sharpe, Sortino, max drawdown, win rate
- ✅ **Risk Management v2** — Kelly sizing, drawdown protection, daily limits
- ✅ **Trade Journal** — Complete audit trail with agent reasoning
- ✅ **Daily Reports** — Automated Telegram summary at midnight
- ✅ **Equity Curve** — Historical equity tracking and visualization

### Analytics Available

| Metric | Description |
|--------|-------------|
| Sharpe Ratio | Risk-adjusted returns |
| Sortino Ratio | Downside risk only |
| Max Drawdown | Peak-to-trough decline |
| Win Rate | Winning trades % |
| Profit Factor | Gross profit / gross loss |
| Expectancy | Average return per trade |
| R-Multiples | Return relative to risk |
| Consecutive Stats | Win/loss streaks |
| Monthly Returns | Month-by-month breakdown |

## Deployment

### Prerequisites

- Cloudflare account (Pages + Workers + KV + D1 + Queues)
- VPS with Docker & Docker Compose
- Telegram bot token
- Exchange API keys (Binance)
- DeepSeek API key

### 1. VPS Backend

```bash
# Copy environment file
cp .env.example /opt/futures-brokiepedia/.env
# Edit with your values
nano /opt/futures-brokiepedia/.env

# Run setup script
sudo ./scripts/setup-vps.sh

# Start services
sudo systemctl start futures-brokiepedia

# View logs
docker compose -f vps/docker-compose.prod.yml logs -f
```

### 2. Cloudflare Worker

```bash
cd workers/api

# Login (if not already)
wrangler login

# Deploy
wrangler deploy

# Set secrets
wrangler secret put DEEPSEEK_API_KEY
wrangler secret put TELEGRAM_BOT_TOKEN
wrangler secret put BINANCE_API_KEY
wrangler secret put BINANCE_SECRET_KEY
wrangler secret put TURSO_DB_TOKEN

# Update DAEMON_URL in wrangler.toml with your VPS IP
```

### 3. Frontend

```bash
# Deploy to Cloudflare Pages
npm run build
npx wrangler pages deploy .svelte-kit/cloudflare
```

## Environment Variables

All secrets stored in Cloudflare Secrets Store (never in code):

```
DEEPSEEK_API_KEY=         # DeepSeek API key
TELEGRAM_BOT_TOKEN=       # Telegram bot token
TELEGRAM_CHAT_ID=         # Telegram chat ID for alerts
BINANCE_API_KEY=          # Binance API key
BINANCE_SECRET_KEY=       # Binance secret key
TURSO_DB_TOKEN=           # Turso database token
LANGCHAIN_API_KEY=        # LangSmith API key (optional)
```

## Security

- WebAuthn/FIDO2 passkey authentication
- Kill-switch with passkey confirmation
- Risk gate: max 2% per trade, 6% hard drawdown halt
- All API keys in Cloudflare Secrets Store
- No secrets in repository
- Rate limiting on all endpoints
- CORS restricted to production domains

## Health Checks

```bash
# Quick health check
./scripts/health-check.sh

# Integration tests
API_URL=http://your-vps:8080 ./scripts/test-integration.sh

# With Worker
API_URL=http://your-vps:8080 WORKER_URL=https://your-worker.workers.dev ./scripts/test-integration.sh
```

## Monitoring

Optional Prometheus monitoring:

```bash
cd vps
docker compose -f docker-compose.prod.yml --profile monitoring up -d
```

Access Prometheus at `http://your-vps:9090`

## License

Private — Futures Brokiepedia
