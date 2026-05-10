-- Futures Brokiepedia — Turso Schema
-- Run this to create all 6 tables

CREATE TABLE IF NOT EXISTS strategies (
 id TEXT PRIMARY KEY,
 version INTEGER,
 parent_id TEXT,
 name TEXT,
 definition_json TEXT,
 status TEXT, -- draft | backtesting | paper | live | rejected | demoted
 win_rate REAL,
 sharpe REAL,
 expectancy REAL,
 prompt_version_id TEXT,
 rejection_reason TEXT,
 created_at INTEGER,
 promoted_at INTEGER
);

CREATE TABLE IF NOT EXISTS backtest_results (
 id TEXT PRIMARY KEY,
 strategy_id TEXT,
 win_rate REAL,
 sharpe REAL,
 max_drawdown REAL,
 expectancy REAL,
 total_trades INTEGER,
 fee_adjusted INTEGER, -- 0 or 1
 regime TEXT,
 passed_gate INTEGER, -- 0 or 1
 created_at INTEGER
);

CREATE TABLE IF NOT EXISTS trade_journal (
 id TEXT PRIMARY KEY,
 strategy_id TEXT,
 exchange TEXT,
 symbol TEXT,
 side TEXT, -- long | short
 entry_price REAL,
 exit_price REAL,
 size REAL,
 pnl REAL,
 fee REAL,
 regime TEXT,
 agent_reasoning_json TEXT,
 paper INTEGER, -- 0=live 1=paper
 created_at INTEGER
);

CREATE TABLE IF NOT EXISTS ledger (
 id TEXT PRIMARY KEY,
 balance REAL,
 equity REAL,
 unrealized_pnl REAL,
 daily_pnl REAL,
 daily_drawdown_pct REAL,
 timestamp INTEGER
);

CREATE TABLE IF NOT EXISTS prompt_versions (
 id TEXT PRIMARY KEY,
 department TEXT,
 prompt_text TEXT,
 win_rate_attribution REAL,
 created_at INTEGER
);

CREATE TABLE IF NOT EXISTS audit_log (
 id TEXT PRIMARY KEY,
 event_type TEXT,
 payload_json TEXT,
 created_at INTEGER
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_strategies_status ON strategies(status);
CREATE INDEX IF NOT EXISTS idx_strategies_created ON strategies(created_at);
CREATE INDEX IF NOT EXISTS idx_backtest_strategy ON backtest_results(strategy_id);
CREATE INDEX IF NOT EXISTS idx_trade_journal_created ON trade_journal(created_at);
CREATE INDEX IF NOT EXISTS idx_trade_journal_strategy ON trade_journal(strategy_id);
CREATE INDEX IF NOT EXISTS idx_ledger_timestamp ON ledger(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_log(created_at);

-- Department API Keys (Phase 6 - External Agent Integration)
CREATE TABLE IF NOT EXISTS department_api_keys (
 id TEXT PRIMARY KEY,
 department TEXT NOT NULL,
 label TEXT,
 api_key_hash TEXT NOT NULL,
 api_key_prefix TEXT NOT NULL,
 is_active INTEGER DEFAULT 1,
 created_by TEXT,
 last_used_at INTEGER,
 created_at INTEGER
);
CREATE INDEX IF NOT EXISTS idx_dept_api_keys_dept ON department_api_keys(department);
CREATE INDEX IF NOT EXISTS idx_dept_api_keys_active ON department_api_keys(is_active);

-- External Agent Signals (submitted by Discord agents)
CREATE TABLE IF NOT EXISTS external_signals (
 id TEXT PRIMARY KEY,
 department TEXT NOT NULL,
 api_key_id TEXT,
 direction TEXT NOT NULL, -- long | short | flat
 confidence REAL,
 symbol TEXT,
 timeframe TEXT,
 reasoning TEXT,
 source TEXT DEFAULT 'discord',
 consumed INTEGER DEFAULT 0, -- 0=pending, 1=consumed by LangGraph
 consumed_at INTEGER,
 created_at INTEGER
);
CREATE INDEX IF NOT EXISTS idx_ext_signals_dept ON external_signals(department);
CREATE INDEX IF NOT EXISTS idx_ext_signals_consumed ON external_signals(consumed);

-- Settings storage
CREATE TABLE IF NOT EXISTS settings (
 id TEXT PRIMARY KEY,
 payload_json TEXT,
 created_at INTEGER
);
