# Futures Brokiepedia

AI-powered crypto futures trading platform with autonomous strategy evolution.

## Architecture

- **Frontend:** SvelteKit + Tailwind CSS + shadcn-svelte → Cloudflare Pages
- **Edge API:** Cloudflare Workers (TypeScript)
- **Edge State:** Cloudflare KV (5s polling from frontend)
- **Edge Queue:** Cloudflare Queues (agent task routing)
- **Edge Audit:** Cloudflare D1 (audit log, sessions)
- **Primary DB:** Turso (libSQL) — strategies, trades, ledger, prompts
- **Time-series DB:** QuestDB (OHLCV, indicators, funding rates)
- **Vector Memory:** ChromaDB (agent reasoning history)
- **AI Agents:** LangGraph + DeepSeek V4 Pro/Flash
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
├── src/
│   ├── lib/
│   │   ├── utils.ts          # Tailwind cn() helper
│   │   ├── types.ts          # Shared TypeScript types
│   │   ├── stores.ts         # Svelte stores
│   │   ├── api.ts            # API client
│   │   └── auth.ts           # WebAuthn passkey utils
│   ├── routes/
│   │   ├── +layout.svelte    # Root layout
│   │   └── +page.svelte      # Dashboard
│   ├── app.css               # Global styles + CSS variables
│   └── app.d.ts              # App types
├── workers/
│   └── api/                  # Cloudflare Worker
│       ├── src/index.ts      # Worker entry
│       └── wrangler.toml     # Worker config
├── schema/
│   ├── turso.sql             # Turso table definitions
│   └── questdb.sql           # QuestDB table definitions
├── .github/workflows/
│   └── deploy.yml            # CI/CD to Cloudflare Pages
└── package.json
```

## Environment Variables

All secrets stored in Cloudflare Secrets Store (never in code):

```
DEEPSEEK_API_KEY=
TELEGRAM_BOT_TOKEN=
BINANCE_API_KEY=
BINANCE_SECRET_KEY=
TURSO_DB_TOKEN=
CLOUDFLARE_API_TOKEN=
```

## Security

- WebAuthn/FIDO2 passkey authentication
- Kill-switch with passkey confirmation
- Risk gate: max 2% per trade, 6% hard drawdown halt
- All API keys in Cloudflare Secrets Store
- No secrets in repository

## License

Private — Futures Brokiepedia
# Deployment triggered Sun May  3 10:42:27 CEST 2026
