#!/bin/bash
set -e
echo "=== Futures Brokiepedia VPS Setup ==="

# System dependencies
sudo apt update && sudo apt install -y \
  python3-pip python3-venv \
  docker.io docker-compose \
  curl git

# Python virtual environment
python3 -m venv /home/ubuntu/brokiepedia/venv
source /home/ubuntu/brokiepedia/venv/bin/activate

# Python packages
pip install --upgrade pip
pip install \
  langgraph langchain-openai langchain-community \
  ccxt chromadb fastapi uvicorn \
  aiohttp python-dotenv \
  pandas numpy scipy questdb websockets \
  pytest libsql-client

# Start Docker services
docker-compose -f /home/ubuntu/brokiepedia/vps/setup/docker-compose.yml up -d

# Install systemd service
sudo cp /home/ubuntu/brokiepedia/vps/setup/brokiepedia.service \
  /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable brokiepedia

echo ""
echo "=== Setup complete ==="
echo "Next steps:"
echo "1. Copy .env.example to .env and fill in all values"
echo "2. Create strategy_research.md (see docs)"
echo "3. Run: sudo systemctl start brokiepedia"
echo "4. Check: sudo systemctl status brokiepedia"
