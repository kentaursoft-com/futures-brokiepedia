#!/bin/bash
set -e
echo "=== Futures Brokiepedia VPS Setup ==="

# Detect user
USER=$(whoami)
HOME_DIR=$(eval echo ~$USER)
PROJECT_DIR="$HOME_DIR/futures-brokiepedia"

echo "Installing as user: $USER"
echo "Project dir: $PROJECT_DIR"

# System dependencies
sudo apt update

# Install packages individually to handle conflicts
sudo apt install -y python3-pip python3-venv curl git || true

# Docker - install if not present
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    sudo apt install -y docker.io || true
    sudo systemctl enable docker
    sudo systemctl start docker
fi

# Docker Compose (v2 plugin or standalone)
if ! command -v docker-compose &> /dev/null; then
    echo "Installing docker-compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Python virtual environment
VENV_DIR="$PROJECT_DIR/venv"
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

# Upgrade pip
pip install --upgrade pip

# Install Python packages (with fallbacks)
pip install fastapi uvicorn aiohttp python-dotenv pandas numpy scipy pytest websockets || true
pip install libsql-client || true

# Try langgraph/langchain (may fail on some systems)
pip install langgraph langchain-openai langchain-community || echo "Warning: langgraph install failed, continuing..."

# Try ccxt and chromadb
pip install ccxt || echo "Warning: ccxt install failed"
pip install chromadb || echo "Warning: chromadb install failed"

# Start Docker services
echo "Starting QuestDB and ChromaDB..."
if [ -f "$PROJECT_DIR/vps/setup/docker-compose.yml" ]; then
    sudo docker-compose -f "$PROJECT_DIR/vps/setup/docker-compose.yml" up -d || \
    sudo docker compose -f "$PROJECT_DIR/vps/setup/docker-compose.yml" up -d || \
    echo "Warning: Docker compose failed - start manually later"
fi

# Install systemd service
echo "Installing systemd service..."
if [ -f "$PROJECT_DIR/vps/setup/brokiepedia.service" ]; then
    # Replace placeholder paths in service file
    sed "s|/home/ubuntu|$HOME_DIR|g" "$PROJECT_DIR/vps/setup/brokiepedia.service" | sudo tee /etc/systemd/system/brokiepedia.service > /dev/null
    sudo systemctl daemon-reload
    sudo systemctl enable brokiepedia || true
fi

echo ""
echo "=== Setup complete ==="
echo "Next steps:"
echo "1. Ensure .env file is filled in: $PROJECT_DIR/.env"
echo "2. Create strategy_research.md if not present"
echo "3. Start daemon: sudo systemctl start brokiepedia"
echo "   OR manually: cd $PROJECT_DIR/vps && source ../venv/bin/activate && python main.py"
echo "4. Check status: sudo systemctl status brokiepedia"
echo ""
echo "Docker status:"
sudo docker ps 2>/dev/null || echo "Docker not running - start with: sudo systemctl start docker"
