import asyncio
import os

async def init_turso():
    try:
        import libsql_client
    except ImportError:
        print("libsql_client not installed, using sqlite3 fallback")
        import sqlite3
        conn = sqlite3.connect("brokiepedia.db")
        statements = [
            """CREATE TABLE IF NOT EXISTS strategies (
                id TEXT PRIMARY KEY, version INTEGER, parent_id TEXT,
                name TEXT, definition_json TEXT, status TEXT,
                win_rate REAL, sharpe REAL, expectancy REAL,
                prompt_version_id TEXT, rejection_reason TEXT,
                created_at INTEGER, promoted_at INTEGER)""",
            """CREATE TABLE IF NOT EXISTS backtest_results (
                id TEXT PRIMARY KEY, strategy_id TEXT,
                win_rate REAL, sharpe REAL, max_drawdown REAL,
                expectancy REAL, total_trades INTEGER,
                fee_adjusted INTEGER, regime TEXT,
                passed_gate INTEGER, created_at INTEGER)""",
            """CREATE TABLE IF NOT EXISTS trade_journal (
                id TEXT PRIMARY KEY, strategy_id TEXT,
                exchange TEXT, symbol TEXT, side TEXT,
                entry_price REAL, exit_price REAL,
                size REAL, pnl REAL, fee REAL, regime TEXT,
                agent_reasoning_json TEXT,
                paper INTEGER, created_at INTEGER)""",
            """CREATE TABLE IF NOT EXISTS ledger (
                id TEXT PRIMARY KEY, balance REAL,
                equity REAL, unrealized_pnl REAL,
                daily_pnl REAL, daily_drawdown_pct REAL,
                timestamp INTEGER)""",
            """CREATE TABLE IF NOT EXISTS prompt_versions (
                id TEXT PRIMARY KEY, department TEXT,
                prompt_text TEXT, win_rate_attribution REAL,
                created_at INTEGER)""",
            """CREATE TABLE IF NOT EXISTS audit_log (
                id TEXT PRIMARY KEY, event_type TEXT,
                payload_json TEXT, created_at INTEGER)"""
        ]
        for sql in statements:
            conn.execute(sql)
        conn.commit()
        conn.close()
        print("SQLite tables created successfully (fallback)")
        return

    client = libsql_client.create_client(
        url=os.environ['TURSO_DB_URL'],
        auth_token=os.environ['TURSO_DB_TOKEN']
    )
    statements = [
        """CREATE TABLE IF NOT EXISTS strategies (
            id TEXT PRIMARY KEY, version INTEGER, parent_id TEXT,
            name TEXT, definition_json TEXT, status TEXT,
            win_rate REAL, sharpe REAL, expectancy REAL,
            prompt_version_id TEXT, rejection_reason TEXT,
            created_at INTEGER, promoted_at INTEGER)""",
        """CREATE TABLE IF NOT EXISTS backtest_results (
            id TEXT PRIMARY KEY, strategy_id TEXT,
            win_rate REAL, sharpe REAL, max_drawdown REAL,
            expectancy REAL, total_trades INTEGER,
            fee_adjusted INTEGER, regime TEXT,
            passed_gate INTEGER, created_at INTEGER)""",
        """CREATE TABLE IF NOT EXISTS trade_journal (
            id TEXT PRIMARY KEY, strategy_id TEXT,
            exchange TEXT, symbol TEXT, side TEXT,
            entry_price REAL, exit_price REAL,
            size REAL, pnl REAL, fee REAL, regime TEXT,
            agent_reasoning_json TEXT,
            paper INTEGER, created_at INTEGER)""",
        """CREATE TABLE IF NOT EXISTS ledger (
            id TEXT PRIMARY KEY, balance REAL,
            equity REAL, unrealized_pnl REAL,
            daily_pnl REAL, daily_drawdown_pct REAL,
            timestamp INTEGER)""",
        """CREATE TABLE IF NOT EXISTS prompt_versions (
            id TEXT PRIMARY KEY, department TEXT,
            prompt_text TEXT, win_rate_attribution REAL,
            created_at INTEGER)""",
        """CREATE TABLE IF NOT EXISTS audit_log (
            id TEXT PRIMARY KEY, event_type TEXT,
            payload_json TEXT, created_at INTEGER)"""
    ]
    for sql in statements:
        await client.execute(sql)
    await client.close()
    print("All Turso tables created successfully")

if __name__ == "__main__":
    asyncio.run(init_turso())
