"""Configuration settings for the trading daemon."""
import os
from dataclasses import dataclass
from typing import List

@dataclass
class RiskConfig:
    MAX_RISK_PER_TRADE_PCT: float = 2.0
    MAX_CONCURRENT_POSITIONS: int = 4
    SOFT_DRAWDOWN_PCT: float = 3.0
    HARD_DRAWDOWN_PCT: float = 6.0
    MAX_LEVERAGE: float = 5.0
    MIN_REWARD_RISK_RATIO: float = 1.5
    CORRELATION_BLOCK_THRESHOLD: float = 0.7

@dataclass
class ExchangeConfig:
    API_KEY: str = ""
    API_SECRET: str = ""
    TESTNET: bool = True  # Default to paper trading
    ENABLED_EXCHANGES: List[str] = None
    
    def __post_init__(self):
        if self.ENABLED_EXCHANGES is None:
            self.ENABLED_EXCHANGES = [
                'binance', 'bybit', 'bitget', 'mexc',
                'kucoin', 'bingx', 'okx', 'gateio'
            ]

@dataclass
class DatabaseConfig:
    QUESTDB_HOST: str = "questdb"
    QUESTDB_PORT: int = 8812
    QUESTDB_USER: str = "admin"
    QUESTDB_PASSWORD: str = "brokiepedia_quest_2026"
    QUESTDB_DB: str = "qdb"
    
    CHROMA_HOST: str = "chromadb"
    CHROMA_PORT: int = 8000
    
    TURSO_URL: str = ""
    TURSO_TOKEN: str = ""

@dataclass
class AIConfig:
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    FAST_MODEL: str = "deepseek-chat"
    DEEP_MODEL: str = "deepseek-reasoner"
    LANGSMITH_TRACING: bool = True
    LANGSMITH_API_KEY: str = ""

@dataclass
class NotificationConfig:
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""

class Settings:
    def __init__(self):
        self.risk = RiskConfig()
        self.exchange = ExchangeConfig(
            API_KEY=os.getenv('BINANCE_API_KEY', ''),
            API_SECRET=os.getenv('BINANCE_SECRET_KEY', ''),
            TESTNET=os.getenv('TRADING_MODE', 'paper') == 'paper'
        )
        self.database = DatabaseConfig(
            TURSO_URL=os.getenv('TURSO_DB_URL', ''),
            TURSO_TOKEN=os.getenv('TURSO_DB_TOKEN', '')
        )
        self.ai = AIConfig(
            DEEPSEEK_API_KEY=os.getenv('DEEPSEEK_API_KEY', ''),
            LANGSMITH_API_KEY=os.getenv('LANGCHAIN_API_KEY', ''),
            LANGSMITH_TRACING=os.getenv('LANGCHAIN_TRACING_V2', 'false').lower() == 'true'
        )
        self.notification = NotificationConfig(
            TELEGRAM_BOT_TOKEN=os.getenv('TELEGRAM_BOT_TOKEN', ''),
            TELEGRAM_CHAT_ID=os.getenv('TELEGRAM_CHAT_ID', '')
        )
        
    def is_paper_trading(self) -> bool:
        return self.exchange.TESTNET

settings = Settings()
