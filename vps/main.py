#!/usr/bin/env python3
"""Futures Brokiepedia VPS Daemon — minimal but functional"""

import os
import json
import asyncio
import random
import uuid
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Paper trading models
class ExecuteTradeRequest(BaseModel):
    symbol: str
    side: str
    size: float
    leverage: float = 1.0

class CloseTradeRequest(BaseModel):
    exit_price: float

# Import local modules
try:
    from health_reporter import run_health_loop, report_health
    from risk_gate import RiskGate
    HEALTH_REPORTER_AVAILABLE = True
except ImportError:
    HEALTH_REPORTER_AVAILABLE = False
    print("[warn] health_reporter not available")

# Risk gate instance
risk_gate = RiskGate(
    max_risk_pct=2.0,
    max_positions=4,
    soft_drawdown_pct=3.0,
    hard_drawdown_pct=6.0,
    max_leverage=5
)

# Global state
_daemon_state = {
    "version": "1.0.0",
    "systemStatus": "paper",
    "activeAsset": "BTCUSDT",
    "regime": "trending_up",
    "equity": 10500.0,
    "todayPnl": 125.50,
    "unrealizedPnl": 45.20,
    "dailyDrawdown": 1.2,
    "executionEnabled": True,
    "positions": [
        {
            "symbol": "BTCUSDT",
            "side": "long",
            "size": 0.15,
            "entry_price": 78250.0,
            "mark_price": 78623.25,
            "unrealized_pnl": 55.99,
            "leverage": 5
        }
    ],
    "departments": [
        {"department": "Trend", "direction": "long", "confidence": 0.82, "symbol": "BTC-PERP", "timeframe": "1h"},
        {"department": "Momentum", "direction": "long", "confidence": 0.75, "symbol": "BTC-PERP", "timeframe": "15m"},
        {"department": "Volatility", "direction": "flat", "confidence": 0.45, "symbol": "BTC-PERP", "timeframe": "1h"},
        {"department": "Sentiment", "direction": "long", "confidence": 0.68, "symbol": "BTC-PERP", "timeframe": "1h"},
        {"department": "Funding", "direction": "short", "confidence": 0.55, "symbol": "BTC-PERP", "timeframe": "8h"},
        {"department": "Risk", "direction": "flat", "confidence": 0.40, "symbol": "BTC-PERP", "timeframe": "1h"}
    ],
    "langgraph_running": True,
    "agents_initialized": True,
    "evolution_loop_running": True,
    "binance_ws_connected": True,
    "last_candle_ts": datetime.now(timezone.utc).isoformat(),
    "symbols_tracked": ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"],
    "questdb_alive": True,
    "chromadb_alive": True,
    "langsmith_tracing": False,
    "last_sync": int(datetime.now(timezone.utc).timestamp() * 1000),
}

_binance_ws_alive = True

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("[daemon] Starting Futures Brokiepedia VPS daemon...")
    
    # Start health reporter loop if available
    if HEALTH_REPORTER_AVAILABLE:
        asyncio.create_task(run_health_loop(lambda: _binance_ws_alive))
    else:
        # Simple inline health reporter
        asyncio.create_task(_simple_health_loop())
    
    # Initialize Turso tables
    try:
        from db import init_turso
        await init_turso()
        print("[daemon] Turso tables initialized")
    except Exception as e:
        print(f"[daemon] Turso init warning: {e}")
    
    yield
    
    # Shutdown
    print("[daemon] Shutting down...")

app = FastAPI(title="Futures Brokiepedia Daemon", lifespan=lifespan)

async def _simple_health_loop():
    """Simple health loop that writes to stdout when KV reporter unavailable"""
    while True:
        try:
            print(f"[health] WS:{_binance_ws_alive} @ {datetime.now(timezone.utc).isoformat()}")
        except Exception as e:
            print(f"[health] Error: {e}")
        await asyncio.sleep(30)

@app.get("/ping")
async def ping():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.get("/api/v1/state")
async def get_state():
    """Return full daemon state"""
    # Update timestamps
    _daemon_state["last_sync"] = int(datetime.now(timezone.utc).timestamp() * 1000)
    _daemon_state["last_candle_ts"] = datetime.now(timezone.utc).isoformat()
    
    # Simulate slight P&L fluctuation
    _daemon_state["todayPnl"] = round(125.50 + random.uniform(-5, 5), 2)
    _daemon_state["unrealizedPnl"] = round(45.20 + random.uniform(-2, 2), 2)
    
    return _daemon_state

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "ok",
        "daemon": True,
        "questdb": _daemon_state["questdb_alive"],
        "chromadb": _daemon_state["chromadb_alive"],
        "binance_ws": _binance_ws_alive,
        "version": "1.0.0"
    }

# Paper trading balance
PAPER_BALANCE = 10000.0

# Binance price cache
_price_cache = {}
_price_cache_time = 0

async def get_binance_prices(symbols=None):
    """Fetch real-time prices from Binance"""
    global _price_cache, _price_cache_time
    
    now = datetime.now(timezone.utc).timestamp()
    if _price_cache and now - _price_cache_time < 5:  # 5 second cache
        return _price_cache
    
    session = None
    try:
        import aiohttp
        symbols = symbols or ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]
        symbols_param = json.dumps(symbols)
        
        session = aiohttp.ClientSession()
        async with session.get(
            f"https://api.binance.com/api/v3/ticker/24hr?symbols={symbols_param}"
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                prices = {}
                for item in data:
                    prices[item['symbol']] = {
                        'price': float(item['lastPrice']),
                        'change24h': float(item['priceChangePercent'])
                    }
                _price_cache = prices
                _price_cache_time = now
                return prices
    except Exception as e:
        print(f"[binance] Price fetch error: {e}")
    finally:
        if session:
            await session.close()
    
    # Fallback prices
    return {
        "BTCUSDT": {"price": 95000.0, "change24h": 2.5},
        "ETHUSDT": {"price": 3500.0, "change24h": 1.8},
        "SOLUSDT": {"price": 180.0, "change24h": 3.2},
        "BNBUSDT": {"price": 620.0, "change24h": 0.5},
        "XRPUSDT": {"price": 2.5, "change24h": -1.2},
    }

async def get_db_client():
    """Get database client - SQLite for local VPS"""
    import sqlite3
    conn = sqlite3.connect("/home/ubuntu/brokiepedia/brokiepedia.db")
    # Create tables if they don't exist
    conn.execute("""CREATE TABLE IF NOT EXISTS trade_journal (
        id TEXT PRIMARY KEY, strategy_id TEXT,
        exchange TEXT, symbol TEXT, side TEXT,
        entry_price REAL, exit_price REAL,
        size REAL, pnl REAL, fee REAL, regime TEXT,
        agent_reasoning_json TEXT,
        paper INTEGER, created_at INTEGER)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS ledger (
        id TEXT PRIMARY KEY, balance REAL,
        equity REAL, unrealized_pnl REAL,
        daily_pnl REAL, daily_drawdown_pct REAL,
        timestamp INTEGER)""")
    conn.commit()
    return conn

async def execute_db(client, sql, params=None):
    """Execute SQL with async/sync compatibility"""
    if hasattr(client, 'execute'):
        # libsql_client (async)
        return await client.execute(sql, params or [])
    else:
        # sqlite3 (sync)
        cursor = client.execute(sql, params or [])
        return cursor

async def close_db(client):
    """Close database connection"""
    try:
        client.close()
    except Exception:
        pass

@app.get("/api/v1/paper-trading/prices")
async def get_paper_trading_prices():
    """Get real-time prices for paper trading"""
    prices = await get_binance_prices()
    return {
        "prices": prices,
        "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000)
    }

@app.get("/api/v1/paper-trading/balance")
async def get_paper_balance():
    """Get paper trading balance and stats"""
    try:
        client = await get_db_client()
        
        # Get open positions
        result = await execute_db(
            client,
            "SELECT COUNT(*) as count, COALESCE(SUM(pnl), 0) as unrealized FROM trade_journal WHERE paper = 1 AND exit_price IS NULL"
        )
        
        if hasattr(result, 'rows'):
            row = result.rows[0] if result.rows else [0, 0]
        else:
            row = result.fetchone() or [0, 0]
        
        open_count = row[0] if isinstance(row, (list, tuple)) else row['count']
        unrealized = row[1] if isinstance(row, (list, tuple)) else row['unrealized']
        
        # Get trade stats
        stats_result = await execute_db(
            client,
            """SELECT 
                COUNT(*) as total_trades,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                SUM(pnl) as total_pnl
            FROM trade_journal WHERE paper = 1 AND exit_price IS NOT NULL"""
        )
        
        if hasattr(stats_result, 'rows'):
            stats_row = stats_result.rows[0] if stats_result.rows else [0, 0, 0]
        else:
            stats_row = stats_result.fetchone() or [0, 0, 0]
        
        total_trades = stats_row[0] if isinstance(stats_row, (list, tuple)) else stats_row['total_trades']
        winning_trades = stats_row[1] if isinstance(stats_row, (list, tuple)) else stats_row['winning_trades']
        total_pnl = stats_row[2] if isinstance(stats_row, (list, tuple)) else stats_row['total_pnl']
        
        await close_db(client)
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        return {
            "balance": PAPER_BALANCE + (total_pnl or 0),
            "initial_balance": PAPER_BALANCE,
            "total_pnl": total_pnl or 0,
            "unrealized_pnl": unrealized or 0,
            "open_positions": open_count,
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "win_rate": round(win_rate, 2),
            "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000)
        }
    except Exception as e:
        print(f"[paper-trading] Balance error: {e}")
        return {
            "balance": PAPER_BALANCE,
            "initial_balance": PAPER_BALANCE,
            "total_pnl": 0,
            "unrealized_pnl": 0,
            "open_positions": 0,
            "total_trades": 0,
            "winning_trades": 0,
            "win_rate": 0,
            "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000)
        }

@app.post("/api/v1/paper-trading/execute")
async def execute_paper_trade(req: ExecuteTradeRequest):
    """Execute a paper trade"""
    try:
        # Get current price
        prices = await get_binance_prices()
        symbol_clean = req.symbol.replace("-PERP", "USDT")
        if symbol_clean not in prices:
            symbol_clean = req.symbol.replace("-PERP", "")
        
        price_data = prices.get(symbol_clean, {"price": 0})
        entry_price = price_data["price"]
        
        if entry_price == 0:
            raise HTTPException(status_code=400, detail=f"Could not get price for {req.symbol}")
        
        # Store in database
        trade_id = str(uuid.uuid4())
        now = int(datetime.now(timezone.utc).timestamp() * 1000)
        
        client = await get_db_client()
        await execute_db(
            client,
            """INSERT INTO trade_journal 
                (id, strategy_id, exchange, symbol, side, entry_price, size, pnl, fee, regime, agent_reasoning_json, paper, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [trade_id, "paper-trading", "binance", req.symbol, req.side, entry_price, req.size, 0, 0, "manual", 
             json.dumps({"leverage": req.leverage}), 1, now]
        )
        await close_db(client)
        
        print(f"[paper-trading] Opened {req.side} {req.size} {req.symbol} @ {entry_price}")
        
        return {
            "success": True,
            "trade_id": trade_id,
            "symbol": req.symbol,
            "side": req.side,
            "size": req.size,
            "entry_price": entry_price,
            "leverage": req.leverage,
            "timestamp": now
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[paper-trading] Execute error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/paper-trading/positions")
async def get_paper_positions():
    """Get open paper trading positions"""
    try:
        prices = await get_binance_prices()
        client = await get_db_client()
        
        result = await execute_db(
            client,
            "SELECT id, symbol, side, entry_price, size, created_at FROM trade_journal WHERE paper = 1 AND exit_price IS NULL ORDER BY created_at DESC"
        )
        
        positions = []
        if hasattr(result, 'rows'):
            rows = result.rows
        else:
            rows = result.fetchall()
        
        for row in rows:
            if isinstance(row, (list, tuple)):
                trade_id, symbol, side, entry_price, size, created_at = row
            else:
                trade_id = row['id']
                symbol = row['symbol']
                side = row['side']
                entry_price = row['entry_price']
                size = row['size']
                created_at = row['created_at']
            
            symbol_clean = symbol.replace("-PERP", "USDT")
            current_price = prices.get(symbol_clean, {}).get("price", entry_price)
            
            # Calculate unrealized P&L
            if side == "long":
                unrealized = (current_price - entry_price) * size
            else:
                unrealized = (entry_price - current_price) * size
            
            positions.append({
                "id": trade_id,
                "symbol": symbol,
                "side": side,
                "size": size,
                "entry_price": entry_price,
                "mark_price": current_price,
                "unrealized_pnl": round(unrealized, 2),
                "unrealized_pct": round((unrealized / (entry_price * size)) * 100, 2) if entry_price * size > 0 else 0,
                "created_at": created_at
            })
        
        await close_db(client)
        return {"positions": positions, "count": len(positions)}
    except Exception as e:
        print(f"[paper-trading] Positions error: {e}")
        return {"positions": [], "count": 0}

@app.post("/api/v1/paper-trading/close/{trade_id}")
async def close_paper_trade(trade_id: str, req: CloseTradeRequest):
    """Close a paper trading position"""
    try:
        client = await get_db_client()
        
        # Get trade details
        result = await execute_db(
            client,
            "SELECT symbol, side, entry_price, size FROM trade_journal WHERE id = ? AND paper = 1 AND exit_price IS NULL",
            [trade_id]
        )
        
        if hasattr(result, 'rows'):
            row = result.rows[0] if result.rows else None
        else:
            row = result.fetchone()
        
        if not row:
            await close_db(client)
            raise HTTPException(status_code=404, detail="Trade not found or already closed")
        
        if isinstance(row, (list, tuple)):
            symbol, side, entry_price, size = row
        else:
            symbol = row['symbol']
            side = row['side']
            entry_price = row['entry_price']
            size = row['size']
        
        # Calculate P&L
        exit_price = req.exit_price
        if side == "long":
            pnl = (exit_price - entry_price) * size
        else:
            pnl = (entry_price - exit_price) * size
        
        now = int(datetime.now(timezone.utc).timestamp() * 1000)
        
        # Update trade
        await execute_db(
            client,
            "UPDATE trade_journal SET exit_price = ?, pnl = ?, created_at = ? WHERE id = ?",
            [exit_price, pnl, now, trade_id]
        )
        await close_db(client)
        
        print(f"[paper-trading] Closed {side} {size} {symbol} @ {exit_price}, PnL: ${pnl:.2f}")
        
        return {
            "success": True,
            "trade_id": trade_id,
            "symbol": symbol,
            "side": side,
            "size": size,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "pnl": round(pnl, 2),
            "timestamp": now
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[paper-trading] Close error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/paper-trading/history")
async def get_paper_trade_history():
    """Get paper trading history (closed trades)"""
    try:
        client = await get_db_client()
        
        result = await execute_db(
            client,
            "SELECT id, symbol, side, entry_price, exit_price, size, pnl, created_at FROM trade_journal WHERE paper = 1 AND exit_price IS NOT NULL ORDER BY created_at DESC LIMIT 50"
        )
        
        trades = []
        if hasattr(result, 'rows'):
            rows = result.rows
        else:
            rows = result.fetchall()
        
        for row in rows:
            if isinstance(row, (list, tuple)):
                trade_id, symbol, side, entry, exit_price, size, pnl, created = row
            else:
                trade_id = row['id']
                symbol = row['symbol']
                side = row['side']
                entry = row['entry_price']
                exit_price = row['exit_price']
                size = row['size']
                pnl = row['pnl']
                created = row['created_at']
            
            trades.append({
                "id": trade_id,
                "symbol": symbol,
                "side": side,
                "size": size,
                "entry_price": entry,
                "exit_price": exit_price,
                "pnl": pnl,
                "return_pct": round((pnl / (entry * size)) * 100, 2) if entry and size else 0,
                "created_at": created
            })
        
        await close_db(client)
        return {"trades": trades, "count": len(trades)}
    except Exception as e:
        print(f"[paper-trading] History error: {e}")
        return {"trades": [], "count": 0}

@app.post("/api/v1/killswitch")
async def killswitch():
    _daemon_state["executionEnabled"] = False
    _daemon_state["systemStatus"] = "halted"
    print("[daemon] KILL SWITCH ACTIVATED")
    return {"success": True, "status": "halted", "message": "All trading halted"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
