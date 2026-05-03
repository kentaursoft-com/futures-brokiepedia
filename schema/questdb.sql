-- Futures Brokiepedia — QuestDB Schema
-- Run these in QuestDB console or via REST API

CREATE TABLE IF NOT EXISTS ohlcv_1m (
 symbol SYMBOL,
 ts TIMESTAMP,
 open DOUBLE,
 high DOUBLE,
 low DOUBLE,
 close DOUBLE,
 volume DOUBLE
) timestamp(ts) PARTITION BY DAY;

CREATE TABLE IF NOT EXISTS ohlcv_5m (
 symbol SYMBOL,
 ts TIMESTAMP,
 open DOUBLE,
 high DOUBLE,
 low DOUBLE,
 close DOUBLE,
 volume DOUBLE
) timestamp(ts) PARTITION BY DAY;

CREATE TABLE IF NOT EXISTS ohlcv_1h (
 symbol SYMBOL,
 ts TIMESTAMP,
 open DOUBLE,
 high DOUBLE,
 low DOUBLE,
 close DOUBLE,
 volume DOUBLE
) timestamp(ts) PARTITION BY MONTH;

CREATE TABLE IF NOT EXISTS indicators (
 symbol SYMBOL,
 ts TIMESTAMP,
 rsi DOUBLE,
 ema20 DOUBLE,
 ema50 DOUBLE,
 atr DOUBLE,
 vwap DOUBLE,
 adx DOUBLE,
 volume_avg DOUBLE
) timestamp(ts) PARTITION BY DAY;

CREATE TABLE IF NOT EXISTS funding_rates (
 symbol SYMBOL,
 ts TIMESTAMP,
 rate DOUBLE,
 open_interest DOUBLE,
 exchange SYMBOL
) timestamp(ts) PARTITION BY DAY;
