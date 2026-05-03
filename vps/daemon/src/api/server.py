"""FastAPI server for dashboard integration."""
import logging
from datetime import datetime
from typing import Dict, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

logger = logging.getLogger(__name__)

# Global state (will be injected from main daemon)
daemon_state = {
    'system_status': 'paper',
    'active_asset': 'BTC-PERP',
    'regime': 'unknown',
    'last_sync': 0,
    'today_pnl': 0.0,
    'unrealized_pnl': 0.0,
    'equity': 10000.0,
    'daily_drawdown': 0.0,
    'execution_enabled': True,
    'kill_switch_triggered': False,
    'departments': [],
    'positions': [],
    'active_strategy': None,
    'health': {
        'vps': True,
        'binance': False,
        'deepseek': False,
        'turso': False,
        'exchanges': 0
    }
}

app = FastAPI(title="Futures Brokiepedia API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "timestamp": int(datetime.now().timestamp()),
        "daemon_status": daemon_state.get('system_status', 'unknown')
    }

@app.get("/api/v1/state")
async def get_state():
    """Get current dashboard state."""
    return daemon_state

@app.get("/api/v1/departments")
async def get_departments():
    """Get latest department verdicts."""
    return {
        "departments": daemon_state.get('departments', []),
        "last_update": daemon_state.get('last_sync', 0)
    }

@app.get("/api/v1/positions")
async def get_positions():
    """Get open positions."""
    return {
        "positions": daemon_state.get('positions', []),
        "count": len(daemon_state.get('positions', []))
    }

@app.get("/api/v1/strategy")
async def get_active_strategy():
    """Get active strategy info."""
    return daemon_state.get('active_strategy', {
        "name": "None",
        "status": "idle"
    })

@app.get("/api/v1/health/services")
async def get_service_health():
    """Get service health status."""
    return daemon_state.get('health', {})

@app.post("/api/v1/killswitch")
async def trigger_killswitch():
    """Trigger emergency kill-switch."""
    daemon_state['execution_enabled'] = False
    daemon_state['kill_switch_triggered'] = True
    daemon_state['system_status'] = 'halted'
    daemon_state['kill_switch_time'] = int(datetime.now().timestamp())
    
    logger.critical("KILL SWITCH triggered via API")
    
    return {
        "success": True,
        "message": "Kill switch activated",
        "timestamp": daemon_state['kill_switch_time']
    }

@app.get("/api/v1/candles/{symbol}")
async def get_candles(symbol: str, limit: int = 100):
    """Get latest candles for symbol."""
    # This would query QuestDB in production
    return {
        "symbol": symbol.upper(),
        "candles": [],  # Placeholder
        "count": 0
    }

def update_state(key: str, value):
    """Update daemon state (called from main daemon)."""
    daemon_state[key] = value
    if key != 'last_sync':
        daemon_state['last_sync'] = int(datetime.now().timestamp())

def start_api_server(host: str = "0.0.0.0", port: int = 8080):
    """Start the API server."""
    uvicorn.run(app, host=host, port=port, log_level="info")
