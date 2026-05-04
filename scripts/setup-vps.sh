#!/bin/bash
# Setup VPS for Futures Brokiepedia Daemon

set -e

echo "🔧 Setting up VPS for Futures Brokiepedia..."

# Create directories
echo "📁 Creating directories..."
mkdir -p /opt/futures-brokiepedia/{logs,data,config}
mkdir -p /opt/futures-brokiepedia/daemon/src

# Copy docker-compose
echo "🐳 Setting up Docker Compose..."
cp vps/docker-compose.yml /opt/futures-brokiepedia/
cp -r vps/daemon /opt/futures-brokiepedia/

# Create systemd service
echo "⚙️ Creating systemd service..."
cat > /etc/systemd/system/futures-brokiepedia.service << 'EOF'
[Unit]
Description=Futures Brokiepedia Trading Daemon
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/futures-brokiepedia
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

# Enable service
systemctl daemon-reload
systemctl enable futures-brokiepedia.service

echo "✅ VPS setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy .env file to /opt/futures-brokiepedia/"
echo "2. Run: systemctl start futures-brokiepedia"
echo "3. Check logs: docker compose logs -f"
