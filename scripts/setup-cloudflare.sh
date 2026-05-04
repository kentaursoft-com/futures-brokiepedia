#!/bin/bash
# Setup Cloudflare Worker with API tokens
# Usage: export CF_API_TOKEN=your_token && ./scripts/setup-cloudflare.sh

set -e

echo "🔧 Cloudflare Worker Setup"
echo "=========================="

# Check for API token
if [ -z "$CF_API_TOKEN" ]; then
    echo "❌ Error: CF_API_TOKEN environment variable not set"
    echo ""
    echo "Set it with:"
    echo "  export CF_API_TOKEN='your_api_token_here'"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo "✅ API token found"

# Login to wrangler with API token
echo ""
echo "🔐 Authenticating with Cloudflare..."
echo "$CF_API_TOKEN" | wrangler login

# Navigate to worker directory
cd workers/api

echo ""
echo "📦 Deploying Worker..."
wrangler deploy

echo ""
echo "🔐 Setting secrets..."
echo ""
echo "IMPORTANT: You need to set these secrets manually:"
echo ""
echo "  wrangler secret put DEEPSEEK_API_KEY"
echo "  wrangler secret put TELEGRAM_BOT_TOKEN"
echo "  wrangler secret put BINANCE_API_KEY"
echo "  wrangler secret put BINANCE_SECRET_KEY"
echo "  wrangler secret put TURSO_DB_TOKEN"
echo ""
echo "You'll be prompted for each value."
echo ""

# Optional: Auto-set if env vars are available
if [ ! -z "$DEEPSEEK_API_KEY" ]; then
    echo "Setting DEEPSEEK_API_KEY..."
    echo "$DEEPSEEK_API_KEY" | wrangler secret put DEEPSEEK_API_KEY
fi

if [ ! -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "Setting TELEGRAM_BOT_TOKEN..."
    echo "$TELEGRAM_BOT_TOKEN" | wrangler secret put TELEGRAM_BOT_TOKEN
fi

if [ ! -z "$BINANCE_API_KEY" ]; then
    echo "Setting BINANCE_API_KEY..."
    echo "$BINANCE_API_KEY" | wrangler secret put BINANCE_API_KEY
fi

if [ ! -z "$BINANCE_SECRET_KEY" ]; then
    echo "Setting BINANCE_SECRET_KEY..."
    echo "$BINANCE_SECRET_KEY" | wrangler secret put BINANCE_SECRET_KEY
fi

if [ ! -z "$TURSO_DB_TOKEN" ]; then
    echo "Setting TURSO_DB_TOKEN..."
    echo "$TURSO_DB_TOKEN" | wrangler secret put TURSO_DB_TOKEN
fi

echo ""
echo "✅ Worker setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Update DAEMON_URL in wrangler.toml with your VPS IP"
echo "2. Deploy again: wrangler deploy"
echo "3. Test: curl https://futures-brokiepedia-api.kentaursoft-com.workers.dev/health"
