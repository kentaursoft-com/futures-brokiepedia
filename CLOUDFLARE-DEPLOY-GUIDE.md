# Cloudflare Worker Deployment Guide

## ⚠️ IMPORTANT: Security Notice

**NEVER commit API tokens to Git or store them in code files!**

The tokens you provided will be used temporarily and are NOT saved anywhere.

## Quick Deploy Steps

### Step 1: Set Environment Variables

```bash
# Set your Cloudflare API token (the Edit one for deployment)
export CF_API_TOKEN="zHzZCn-NtLajQFUcKwuEV1GNyahK4_Z5zheK416a"

# Optional: Set your secrets now so they're auto-configured
export DEEPSEEK_API_KEY="your_deepseek_key"
export TELEGRAM_BOT_TOKEN="your_telegram_token"
export BINANCE_API_KEY="your_binance_key"
export BINANCE_SECRET_KEY="your_binance_secret"
export TURSO_DB_TOKEN="your_turso_token"
```

### Step 2: Authenticate Wrangler

```bash
cd /root/.openclaw/workspace/futures-brokiepedia

# Login with your API token
echo "$CF_API_TOKEN" | npx wrangler login
```

### Step 3: Deploy Worker

```bash
# Deploy the worker
cd workers/api
npx wrangler deploy
```

### Step 4: Update DAEMON_URL

```bash
# Run from project root
cd /root/.openclaw/workspace/futures-brokiepedia

# Replace YOUR_VPS_IP with your actual server IP
./scripts/update-worker-config.sh YOUR_VPS_IP

# Example:
# ./scripts/update-worker-config.sh 192.168.1.100
```

### Step 5: Set Secrets

If you didn't export them in Step 1, set them manually:

```bash
cd workers/api

# Each will prompt you for the value
echo "your_deepseek_key" | npx wrangler secret put DEEPSEEK_API_KEY
echo "your_telegram_token" | npx wrangler secret put TELEGRAM_BOT_TOKEN
echo "your_binance_key" | npx wrangler secret put BINANCE_API_KEY
echo "your_binance_secret" | npx wrangler secret put BINANCE_SECRET_KEY
echo "your_turso_token" | npx wrangler secret put TURSO_DB_TOKEN
```

### Step 6: Deploy Frontend

```bash
cd /root/.openclaw/workspace/futures-brokiepedia

# Build and deploy to Cloudflare Pages
npm run build
npx wrangler pages deploy .svelte-kit/cloudflare
```

## Verification

Test the worker is working:

```bash
# Test health endpoint
curl https://futures-brokiepedia-api.kentaursoft-com.workers.dev/health

# Test state endpoint
curl https://futures-brokiepedia-api.kentaursoft-com.workers.dev/api/v1/state
```

## Troubleshooting

### "Authentication error"
- Make sure CF_API_TOKEN is set correctly
- The token needs "Cloudflare Workers:Edit" permission

### "Daemon offline" on dashboard
- Check DAEMON_URL in wrangler.toml matches your VPS IP
- Ensure VPS daemon is running: `sudo systemctl status futures-brokiepedia`
- Check VPS firewall allows port 8080

### "404 Not Found"
- Worker might not be deployed yet
- Check wrangler deploy output for errors

## One-Command Deploy (After Setup)

Once configured, you can deploy everything with:

```bash
cd /root/.openclaw/workspace/futures-brokiepedia

# Deploy worker
cd workers/api && npx wrangler deploy && cd ../..

# Deploy frontend
npm run build && npx wrangler pages deploy .svelte-kit/cloudflare
```

## Resources

- Wrangler docs: https://developers.cloudflare.com/workers/wrangler/
- Workers docs: https://developers.cloudflare.com/workers/
- Pages docs: https://developers.cloudflare.com/pages/
