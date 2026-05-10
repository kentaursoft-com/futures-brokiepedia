"""FastAPI server for dashboard integration - Phase 5."""
import logging
from datetime import datetime
from typing import Dict, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .middleware import RateLimitMiddleware, LoggingMiddleware
from ..agents.external_signals import ExternalSignalStore, validate_signal_body

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
    'performance': {},
    'health': {
        'vps': True,
        'binance': False,
        'deepseek': False,
        'turso': False,
        'exchanges': 0
    }
}

# References to daemon components (injected at startup)
daemon_refs = {}

app = FastAPI(title="Futures Brokiepedia API", version="1.0.0")

# Add middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=120)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://futures-brokiepedia.pages.dev", "https://futures.brokiepedia.com"],
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

# === Phase 5: Analytics Endpoints ===

@app.get("/api/v1/performance")
async def get_performance():
    """Get performance analytics."""
    analytics = daemon_refs.get('analytics')
    if analytics:
        return analytics.get_full_report()
    return daemon_state.get('performance', {})

@app.get("/api/v1/performance/equity-curve")
async def get_equity_curve(days: int = 30):
    """Get equity curve data."""
    execution = daemon_refs.get('execution')
    if execution and execution.turso:
        history = await execution.turso.get_equity_curve(days)
        return {'equity_history': history}
    return {'equity_history': []}

@app.get("/api/v1/trades")
async def get_trades(limit: int = 100, paper_only: bool = True):
    """Get trade history."""
    execution = daemon_refs.get('execution')
    if execution:
        trades = execution.positions.get_trade_history(limit)
        return {'trades': trades, 'count': len(trades)}
    return {'trades': [], 'count': 0}

@app.get("/api/v1/trades/stats")
async def get_trade_stats(days: int = 30):
    """Get trade statistics."""
    execution = daemon_refs.get('execution')
    if execution and execution.turso:
        stats = await execution.turso.get_performance_stats(days)
        return stats
    return {}

@app.post("/api/v1/positions/{position_id}/close")
async def close_position(position_id: str, reason: str = 'manual'):
    """Close a specific position."""
    execution = daemon_refs.get('execution')
    if execution:
        trade = await execution.close_position(position_id, reason)
        if trade:
            return {'success': True, 'trade': trade}
    return {'success': False, 'error': 'Position not found or execution not available'}

@app.get("/api/v1/risk/status")
async def get_risk_status():
    """Get current risk status."""
    execution = daemon_refs.get('execution')
    if execution:
        positions = execution.positions
        return {
            'current_drawdown_pct': round(positions.get_current_drawdown(), 2),
            'max_drawdown_pct': round(positions.max_drawdown_pct, 2),
            'daily_pnl': round(positions.daily_pnl, 2),
            'equity': round(positions.equity, 2),
            'open_positions': len(positions.positions),
            'execution_enabled': execution.execution_enabled,
            'risk_limits': {
                'max_positions': execution.risk.MAX_CONCURRENT_POSITIONS,
                'max_risk_per_trade_pct': execution.risk.MAX_RISK_PER_TRADE_PCT,
                'soft_drawdown_pct': execution.risk.SOFT_DRAWDOWN_PCT,
                'hard_drawdown_pct': execution.risk.HARD_DRAWDOWN_PCT
            }
        }
    return {}

# === State Management ===

def update_state(key: str, value):
    """Update daemon state (called from main daemon)."""
    daemon_state[key] = value
    if key != 'last_sync':
        daemon_state['last_sync'] = int(datetime.now().timestamp())

def set_daemon_refs(refs: dict):
    """Set references to daemon components."""
    daemon_refs.update(refs)

# === AI Endpoints ===

@app.get("/api/v1/ai/health")
async def ai_health():
    """Check AI model health."""
    from ..ai.router import AIModelRouter
    router = AIModelRouter()
    return router.health_check()

@app.post("/api/v1/ai/analyze")
async def ai_analyze(request: dict):
    """Get AI market analysis."""
    from ..ai.router import AIModelRouter
    router = AIModelRouter()
    
    result = router.analyze_market(
        symbol=request.get('symbol', 'BTCUSDT'),
        price=request.get('price', 0.0),
        indicators=request.get('indicators', {}),
        provider=request.get('provider')
    )
    
    if result:
        return {'success': True, 'analysis': result}
    return {'success': False, 'error': 'AI analysis failed'}

# === Backup Endpoints ===

@app.post("/api/v1/backup")
async def create_backup():
    """Create a manual backup."""
    from ..database.backup import BackupManager
    manager = BackupManager()
    path = manager.create_backup('manual')
    
    if path:
        return {'success': True, 'path': path}
    return {'success': False, 'error': 'Backup failed'}

@app.get("/api/v1/backups")
async def list_backups():
    """List available backups."""
    from ..database.backup import BackupManager
    manager = BackupManager()
    return {
        'backups': manager.list_backups()[:20],
        'status': manager.get_backup_status()
    }

# === Phase 6: External Signal Endpoints ===

@app.post("/api/v1/departments/signal")
async def ingest_external_signal(request: dict):
    """Ingest an external signal from Discord agent (via Cloudflare Worker)."""
    signal_store = daemon_refs.get('signal_store')
    if not signal_store:
        raise HTTPException(status_code=503, detail="Signal store not available")

    # Validate body
    error = validate_signal_body(request)
    if error:
        raise HTTPException(status_code=400, detail=error)

    try:
        entry = await signal_store.ingest_signal(request)
        logger.info(f"Ingested external signal: {entry['department']} → {entry['direction']}")
        return {"success": True, "signal_id": entry['id'], "department": entry['department']}
    except Exception as e:
        logger.error(f"Failed to ingest external signal: {e}")
        raise HTTPException(status_code=500, detail="Failed to ingest signal")


@app.get("/api/v1/departments/signals/pending")
async def get_pending_signals():
    """Get all pending external signals."""
    signal_store = daemon_refs.get('signal_store')
    if not signal_store:
        return {"departments": {}, "total": 0}

    pending = signal_store.get_all_pending()
    total = sum(len(signals) for signals in pending.values())
    return {
        "departments": {
            dept: [{"id": s["id"], "direction": s["direction"],
                    "confidence": s["confidence"], "symbol": s["symbol"],
                    "timeframe": s["timeframe"], "reasoning": s["reasoning"][:100]}
                   for s in signals]
            for dept, signals in pending.items()
        },
        "total": total
    }


def start_api_server(host: str = "0.0.0.0", port: int = 8080):
    """Start the API server."""
    uvicorn.run(app, host=host, port=port, log_level="info")
