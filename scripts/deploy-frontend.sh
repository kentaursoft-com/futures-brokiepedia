#!/bin/bash
# Deploy Frontend to Cloudflare Pages

set -e

echo "🚀 Deploying Futures Brokiepedia Frontend..."

# Build the project
echo "📦 Building..."
npm run build

# Deploy to Cloudflare Pages
echo "☁️ Deploying to Cloudflare Pages..."
npx wrangler pages deploy .svelte-kit/cloudflare

echo "✅ Frontend deployed!"
