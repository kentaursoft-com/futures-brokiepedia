FROM python:3.11-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt . 2>/dev/null || echo "No requirements.txt"

# Install Python packages
RUN pip install --no-cache-dir \
    fastapi uvicorn aiohttp python-dotenv \
    pandas numpy scipy websockets \
    libsql-client pytest

# Try optional packages (may fail on some architectures)
RUN pip install --no-cache-dir chromadb ccxt || true
RUN pip install --no-cache-dir langgraph langchain-openai || true

# Copy application code
COPY . .

EXPOSE 8000

CMD ["python", "vps/main.py"]
