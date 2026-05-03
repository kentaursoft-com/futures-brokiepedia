"""Main daemon entry point for Futures Brokiepedia."""
import asyncio
import logging
import signal
import sys
from datetime import datetime

from .config.settings import settings
from .ingestion.binance_ws import BinanceFuturesIngestion
from .ingestion.questdb_client import QuestDBClient
from .agents.departments import DepartmentAgents
from .agents.regime_classifier import MarketRegimeClassifier
from .exchanges.exchange_layer import ExchangeAbstractionLayer
from .exchanges.execution import ExecutionAgent
from .notifications.telegram import TelegramNotifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/app/logs/daemon.log')
    ]
)
logger = logging.getLogger(__name__)

class TradingDaemon:
    """Main trading daemon orchestrating all components."""
    
    def __init__(self):
        self.running = False
        self.ingestion = None
        self.questdb = None
        self.departments = None
        self.regime_classifier = None
        self.exchanges = None
        self.execution = None
        self.notifier = None
        self.candle_buffer = []
        
    async def initialize(self):
        """Initialize all components."""
        logger.info("Initializing Futures Brokiepedia Daemon...")
        
        # Initialize QuestDB
        self.questdb = QuestDBClient(
            host=settings.database.QUESTDB_HOST,
            port=settings.database.QUESTDB_PORT,
            user=settings.database.QUESTDB_USER,
            password=settings.database.QUESTDB_PASSWORD
        )
        self.questdb.connect()
        self.questdb.create_tables()
        logger.info("QuestDB initialized")
        
        # Initialize exchange layer (paper mode by default)
        self.exchanges = ExchangeAbstractionLayer()
        await self.exchanges.initialize(['binance'])
        logger.info("Exchange layer initialized (PAPER MODE)")
        
        # Initialize execution agent
        self.execution = ExecutionAgent(self.exchanges)
        logger.info("Execution agent initialized")
        
        # Initialize AI departments
        self.departments = DepartmentAgents(
            api_key=settings.ai.DEEPSEEK_API_KEY,
            base_url=settings.ai.DEEPSEEK_BASE_URL
        )
        logger.info("AI departments initialized")
        
        # Initialize regime classifier
        self.regime_classifier = MarketRegimeClassifier()
        logger.info("Regime classifier initialized")
        
        # Initialize notifications
        self.notifier = TelegramNotifier(
            bot_token=settings.notification.TELEGRAM_BOT_TOKEN,
            chat_id=settings.notification.TELEGRAM_CHAT_ID
        )
        logger.info("Notification service initialized")
        
        # Initialize ingestion
        self.ingestion = BinanceFuturesIngestion(
            symbols=['btcusdt'],
            on_candle=self._on_candle
        )
        logger.info("Market data ingestion initialized")
        
    async def _on_candle(self, candle: dict):
        """Handle new candle from WebSocket."""
        # Buffer candles for analysis
        self.candle_buffer.append(candle)
        if len(self.candle_buffer) > 1000:
            self.candle_buffer.pop(0)
        
        # Write to QuestDB
        try:
            self.questdb.insert_candle(candle)
        except Exception as e:
            logger.error(f"Failed to write candle to QuestDB: {e}")
        
        # Only analyze on closed candles
        if candle.get('is_closed'):
            await self._analyze_market()
    
    async def _analyze_market(self):
        """Run analysis cycle."""
        try:
            if len(self.candle_buffer) < 50:
                return
            
            # Classify regime
            regime_result = self.regime_classifier.classify(self.candle_buffer)
            regime = regime_result['regime']
            
            # Prepare market data
            latest = self.candle_buffer[-1]
            market_data = {
                'close': latest['close'],
                'high': latest['high'],
                'low': latest['low'],
                'volume': latest['volume'],
                'ema20': sum(c['close'] for c in self.candle_buffer[-20:]) / 20,
                'ema50': sum(c['close'] for c in self.candle_buffer[-50:]) / 50,
            }
            
            # Run department analysis
            result = await self.departments.analyze(
                symbol='BTCUSDT',
                market_data=market_data,
                regime=regime
            )
            
            signal = result.get('aggregated_signal', {})
            
            if result.get('should_trade') and result.get('risk_check_passed'):
                logger.info(f"TRADE SIGNAL: {signal}")
                
                # Execute in paper mode
                if settings.is_paper_trading():
                    await self.execution.execute_signal(
                        signal={
                            'symbol': 'BTCUSDT',
                            'direction': signal['direction'],
                            'entry_price': latest['close'],
                            'size_multiplier': signal.get('size_reduction', 1.0)
                        },
                        strategy={'name': 'ai_aggregated', 'stop_loss_pct': 0.02}
                    )
            
        except Exception as e:
            logger.error(f"Analysis cycle error: {e}")
    
    async def run(self):
        """Main daemon loop."""
        self.running = True
        logger.info("Daemon started - running in PAPER TRADING mode")
        
        # Send startup notification
        await self.notifier.send_alert('evolution_start', {'status': 'daemon_online'})
        
        # Start ingestion
        await self.ingestion.connect()
    
    async def shutdown(self):
        """Graceful shutdown."""
        logger.info("Shutting down daemon...")
        self.running = False
        
        if self.ingestion:
            await self.ingestion.disconnect()
        
        if self.exchanges:
            await self.exchanges.close()
        
        if self.questdb:
            self.questdb.close()
        
        logger.info("Daemon shutdown complete")

# Global daemon instance
daemon = TradingDaemon()

async def main():
    """Entry point."""
    # Handle signals
    loop = asyncio.get_event_loop()
    
    def signal_handler(sig):
        logger.info(f"Received signal {sig}")
        asyncio.create_task(daemon.shutdown())
        loop.stop()
    
    loop.add_signal_handler(signal.SIGTERM, lambda: signal_handler('SIGTERM'))
    loop.add_signal_handler(signal.SIGINT, lambda: signal_handler('SIGINT'))
    
    try:
        await daemon.initialize()
        await daemon.run()
    except Exception as e:
        logger.critical(f"Daemon fatal error: {e}")
        await daemon.shutdown()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
