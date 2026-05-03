"""QuestDB client for time-series data."""
import logging
from datetime import datetime
from typing import List, Dict, Any
import psycopg2
from psycopg2.extras import execute_values

logger = logging.getLogger(__name__)

class QuestDBClient:
    """Client for QuestDB time-series database."""
    
    def __init__(self, host: str = "questdb", port: int = 8812,
                 user: str = "admin", password: str = "brokiepedia_quest_2026",
                 database: str = "qdb"):
        self.conn_params = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'database': database
        }
        self.conn = None
        
    def connect(self):
        """Establish database connection."""
        try:
            self.conn = psycopg2.connect(**self.conn_params)
            logger.info("Connected to QuestDB")
        except Exception as e:
            logger.error(f"Failed to connect to QuestDB: {e}")
            raise
    
    def create_tables(self):
        """Create required tables."""
        tables = [
            """
            CREATE TABLE IF NOT EXISTS ohlcv_1m (
                symbol SYMBOL,
                ts TIMESTAMP,
                open DOUBLE,
                high DOUBLE,
                low DOUBLE,
                close DOUBLE,
                volume DOUBLE
            ) TIMESTAMP(ts) PARTITION BY DAY
            """,
            """
            CREATE TABLE IF NOT EXISTS ohlcv_5m (
                symbol SYMBOL,
                ts TIMESTAMP,
                open DOUBLE,
                high DOUBLE,
                low DOUBLE,
                close DOUBLE,
                volume DOUBLE
            ) TIMESTAMP(ts) PARTITION BY DAY
            """,
            """
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
            ) TIMESTAMP(ts) PARTITION BY DAY
            """,
            """
            CREATE TABLE IF NOT EXISTS funding_rates (
                symbol SYMBOL,
                ts TIMESTAMP,
                rate DOUBLE,
                open_interest DOUBLE,
                exchange SYMBOL
            ) TIMESTAMP(ts) PARTITION BY DAY
            """
        ]
        
        with self.conn.cursor() as cur:
            for table_sql in tables:
                cur.execute(table_sql)
            self.conn.commit()
        logger.info("QuestDB tables created")
    
    def insert_candle(self, candle: dict, table: str = "ohlcv_1m"):
        """Insert a single candle."""
        with self.conn.cursor() as cur:
            cur.execute(f"""
                INSERT INTO {table} (symbol, ts, open, high, low, close, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                candle['symbol'],
                candle['timestamp'],
                candle['open'],
                candle['high'],
                candle['low'],
                candle['close'],
                candle['volume']
            ))
            self.conn.commit()
    
    def insert_candles_batch(self, candles: List[dict], table: str = "ohlcv_1m"):
        """Batch insert candles for better performance."""
        if not candles:
            return
            
        values = [
            (c['symbol'], c['timestamp'], c['open'], c['high'], 
             c['low'], c['close'], c['volume'])
            for c in candles
        ]
        
        with self.conn.cursor() as cur:
            execute_values(
                cur,
                f"INSERT INTO {table} (symbol, ts, open, high, low, close, volume) VALUES %s",
                values
            )
            self.conn.commit()
    
    def get_latest_candles(self, symbol: str, limit: int = 100, 
                          table: str = "ohlcv_1m") -> List[dict]:
        """Get latest candles for symbol."""
        with self.conn.cursor() as cur:
            cur.execute(f"""
                SELECT symbol, ts, open, high, low, close, volume
                FROM {table}
                WHERE symbol = %s
                ORDER BY ts DESC
                LIMIT %s
            """, (symbol, limit))
            
            rows = cur.fetchall()
            return [
                {
                    'symbol': r[0],
                    'timestamp': r[1],
                    'open': r[2],
                    'high': r[3],
                    'low': r[4],
                    'close': r[5],
                    'volume': r[6]
                }
                for r in reversed(rows)
            ]
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("QuestDB connection closed")
