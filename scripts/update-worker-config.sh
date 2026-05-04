#!/bin/bash
# Update Worker configuration (DAEMON_URL, etc.)
# Usage: ./scripts/update-worker-config.sh <VPS_IP>

set -e

VPS_IP=${1:-""}

if [ -z "$VPS_IP" ]; then
    echo "❌ Error: VPS IP address required"
    echo ""
    echo "Usage: ./scripts/update-worker-config.sh <YOUR_VPS_IP>"
    echo ""
    echo "Example: ./scripts/update-worker-config.sh 123.456.789.012"
    exit 1
fi

echo "📝 Updating Worker configuration..."
echo "VPS IP: $VPS_IP"

# Update wrangler.toml
cd workers/api

# Use sed to replace the DAEMON_URL
sed -i "s|DAEMON_URL = \"http://your-vps-ip:8080\"|DAEMON_URL = \"http://$VPS_IP:8080\"|" wrangler.toml

echo "✅ Updated DAEMON_URL to http://$VPS_IP:8080"

# Deploy the worker
echo ""
echo "🚀 Deploying updated Worker..."
wrangler deploy

echo ""
echo "✅ Worker updated and deployed!"
echo ""
echo "Testing connection..."
sleep 2

curl -s "https://futures-brokiepedia-api.kentaursoft-com.workers.dev/health" | echo "Health check response: $(cat -)"
