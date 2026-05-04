#!/bin/bash
# Deploy Cloudflare Worker for Futures Brokiepedia API

set -e

echo "🚀 Deploying Futures Brokiepedia Worker..."

cd workers/api

# Check if wrangler is logged in
if ! wrangler whoami > /dev/null 2>&1; then
    echo "❌ Not logged into Cloudflare. Run: wrangler login"
    exit 1
fi

# Deploy worker
echo "📦 Publishing worker..."
wrangler deploy

# Set secrets (prompt for values if not set)
echo ""
echo "🔐 Setting secrets..."
echo "Note: Set secrets individually with:"
echo "  wrangler secret put DEEPSEEK_API_KEY"
echo "  wrangler secret put TELEGRAM_BOT_TOKEN"
echo "  wrangler secret put BINANCE_API_KEY"
echo "  wrangler secret put BINANCE_SECRET_KEY"
echo "  wrangler secret put TURSO_DB_TOKEN"
echo ""
echo "✅ Worker deployed!"
echo "📝 Update DAEMON_URL in wrangler.toml with your VPS IP"
