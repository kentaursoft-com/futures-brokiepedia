"""Main daemon entry point for Futures Brokiepedia - Phase 5."""
import asyncio
import logging
import signal
import sys
import threading
from datetime import datetime

from .config.settings import settings
from .database.turso_client import TursoClient
from .ingestion.binance_ws import BinanceFuturesIngestion
from .ingestion.questdb_client import QuestDBClient
from .agents.departments import DepartmentAgents
from .agents.external_signals import ExternalSignalStore
from .agents.regime_classifier import MarketRegimeClassifier
from .agents.back_office import BookKeeper, JournalingAgent, ResearcherAgent, HealthMonitor
from .exchanges.exchange_layer import ExchangeAbstractionLayer
from .trading.live_execution import LiveExecutionEngine
from .analytics.performance import PerformanceAnalytics
from .notifications.telegram import TelegramNotifier
from .api.server import start_api_server, update_state, set_daemon_refs

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
    def __init__(self):
        self.running = False
        self.ingestion = None
        self.questdb = None
        self.turso = None
        self.departments = None
        self.regime_classifier = None
        self.exchanges = None
        self.execution = None
        self.analytics = None
        self.notifier = None
        self.candle_buffer = []
        self.current_regime = 'unknown'
        self.last_analysis_time = 0
        
        # Back-office agents
        self.book_keeper = BookKeeper()
        self.journaling = JournalingAgent()
        self.researcher = ResearcherAgent()
        self.health_monitor = HealthMonitor()
        
    async def initialize(self):
        logger.info("=" * 60)
        logger.info("Futures Brokiepedia Daemon v1.0.0 - Phase 5")
        logger.info("=" * 60)
        logger.info(f"Mode: {'PAPER' if settings.is_paper_trading() else 'LIVE'} TRADING")
        
        # Turso (persistent storage)
        try:
            self.turso = TursoClient()
            self.turso.connect()
            logger.info("✅ Turso connected")
        except Exception as e:
            logger.warning(f"Turso not available: {e}")
            self.turso = None
        
        # External Signal Store (Phase 6 - Discord agent integration)
        self.signal_store = ExternalSignalStore(turso_client=self.turso)
        try:
            loaded = asyncio.get_event_loop().run_until_complete(self.signal_store.load_pending_from_db())
            if loaded > 0:
                logger.info(f"✅ Loaded {loaded} pending external signals from DB")
        except Exception as e:
            logger.warning(f"Could not load pending signals: {e}")
        logger.info("✅ External signal store ready")

        # QuestDB
        
        # QuestDB
        self.questdb = QuestDBClient(
            host=settings.database.QUESTDB_HOST,
            port=settings.database.QUESTDB_PORT,
            user=settings.database.QUESTDB_USER,
            password=settings.database.QUESTDB_PASSWORD
        )
        self.questdb.connect()
        self.questdb.create_tables()
        logger.info("✅ QuestDB connected")
        
        # Exchanges
        self.exchanges = ExchangeAbstractionLayer()
        await self.exchanges.initialize(['binance'])
        logger.info("✅ Exchange layer ready (8 exchanges supported)")
        
        # Execution engine (Phase 5)
        self.execution = LiveExecutionEngine(self.exchanges, self.turso)
        logger.info("✅ Live execution engine ready")
        
        # Analytics
        self.analytics = PerformanceAnalytics()
        logger.info("✅ Performance analytics ready")
        
        # AI Departments (with external signal injection)
        self.departments = DepartmentAgents(
            api_key=settings.ai.DEEPSEEK_API_KEY,
            base_url=settings.ai.DEEPSEEK_BASE_URL,
            signal_store=self.signal_store
        )
        logger.info("✅ 6 Department agents initialized (DeepSeek V4 Pro)")
        
        # Regime Classifier
        self.regime_classifier = MarketRegimeClassifier()
        logger.info("✅ Regime classifier ready")
        
        # Notifications
        self.notifier = TelegramNotifier(
            bot_token=settings.notification.TELEGRAM_BOT_TOKEN,
            chat_id=settings.notification.TELEGRAM_CHAT_ID
        )
        
        # Health Monitor
        self.health_monitor = HealthMonitor(notifier=self.notifier)
        logger.info("✅ Health monitor ready")
        
        # Ingestion
        self.ingestion = BinanceFuturesIngestion(
            symbols=['btcusdt'],
            on_candle=self._on_candle
        )
        logger.info("✅ Binance WS ingestion ready")
        
        # Initial state update
        self._update_dashboard_state()
        
        # Set daemon refs for API server (including signal store)
        set_daemon_refs({
            'execution': self.execution,
            'analytics': self.analytics,
            'turso': self.turso,
            'signal_store': self.signal_store
        })
        
    def _update_dashboard_state(self):
        """Push current state to API server."""
        health = self.health_monitor.get_status_summary()
        exec_status = self.execution.get_status() if self.execution else {}
        
        update_state('system_status', 'paper' if settings.is_paper_trading() else 'live')
        update_state('active_asset', 'BTC-PERP')
        update_state('regime', self.current_regime)
        update_state('today_pnl', exec_status.get('daily_pnl', 0))
        update_state('unrealized_pnl', self.execution.positions.get_unrealized_pnl() if self.execution else 0)
        update_state('equity', exec_status.get('equity', 10000))
        update_state('daily_drawdown', exec_status.get('current_drawdown', 0))
        update_state('execution_enabled', exec_status.get('execution_enabled', True))
        update_state('kill_switch_triggered', not exec_status.get('execution_enabled', True))
        update_state('positions', self.execution.positions.get_all_positions() if self.execution else [])
        update_state('health', {
            'vps': True,
            'binance': self.ingestion.running if self.ingestion else False,
            'deepseek': health.get('services', {}).get('deepseek_api', False),
            'turso': health.get('services', {}).get('questdb', False),
            'exchanges': len(self.exchanges.exchanges) if self.exchanges else 0
        })
        
    async def _on_candle(self, candle: dict):
        self.candle_buffer.append(candle)
        if len(self.candle_buffer) > 500:
            self.candle_buffer.pop(0)
        
        # Write to QuestDB
        try:
            self.questdb.insert_candle(candle)
        except Exception as e:
            logger.error(f"QuestDB write error: {e}")
        
        # Update position prices
        if self.execution:
            await self.execution.update_positions()
        
        # Analyze on closed candles
        if candle.get('is_closed') and len(self.candle_buffer) >= 50:
            asyncio.create_task(self._analyze_market())
    
    async def _analyze_market(self):
        try:
            if len(self.candle_buffer) < 50:
                return
            
            # Rate limit analysis
            now = datetime.now().timestamp()
            if now - self.last_analysis_time < 60:
                return
            self.last_analysis_time = now
            
            # Regime classification
            regime_result = self.regime_classifier.classify(self.candle_buffer)
            self.current_regime = regime_result['regime']
            
            # Build market data snapshot
            latest = self.candle_buffer[-1]
            closes = [c['close'] for c in self.candle_buffer]
            
            market_data = {
                'close': latest['close'],
                'high': latest['high'],
                'low': latest['low'],
                'volume': latest['volume'],
                'ema20': sum(closes[-20:]) / 20,
                'ema50': sum(closes[-50:]) / 50,
                'rsi': self._calculate_rsi(closes),
                'atr': regime_result['atr']
            }
            
            # Run department analysis
            result = await self.departments.analyze(
                symbol='BTCUSDT',
                market_data=market_data,
                regime=self.current_regime
            )
            
            # Update department verdicts
            verdicts = result.get('verdicts', [])
            update_state('departments', [
                {
                    'name': v['department'],
                    'direction': v['direction'],
                    'confidence': v['confidence'],
                    'timeframe': v.get('timeframe', '1h'),
                    'regime_tag': v.get('regime_tag', 'unknown'),
                    'lastRun': datetime.now().strftime('%H:%M:%S')
                }
                for v in verdicts
            ])
            
            signal = result.get('aggregated_signal', {})
            
            # Execute if signal is strong
            if result.get('should_trade') and self.execution:
                trade_id = f"trade_{int(datetime.now().timestamp())}"
                
                # Log reasoning
                await self.journaling.log_reasoning(
                    trade_id=trade_id,
                    verdicts=verdicts,
                    aggregated=signal,
                    regime=self.current_regime
                )
                
                # Execute trade
                order = await self.execution.execute_signal(
                    signal={
                        'symbol': 'BTCUSDT',
                        'direction': signal['direction'],
                        'entry_price': latest['close'],
                        'size_multiplier': signal.get('size_reduction', 1.0),
                        'regime': self.current_regime,
                        'reasoning': {
                            'verdicts': verdicts,
                            'aggregated': signal
                        }
                    },
                    strategy={'name': 'AI-Aggregated', 'stop_loss_pct': 0.02}
                )
                
                if order:
                    await self.notifier.send_alert('gate1_pass', {
                        'strategy': 'AI-Aggregated',
                        'direction': signal['direction'],
                        'confidence': signal['confidence']
                    })
            
            # Update dashboard
            self._update_dashboard_state()
            
        except Exception as e:
            logger.error(f"Analysis cycle error: {e}")
    
    def _calculate_rsi(self, closes: list, period: int = 14) -> float:
        if len(closes) < period + 1:
            return 50.0
        
        deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        gains = [d if d > 0 else 0 for d in deltas[-period:]]
        losses = [-d if d < 0 else 0 for d in deltas[-period:]]
        
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    async def _health_check_loop(self):
        """Run health checks every 60 seconds."""
        while self.running:
            try:
                results = await self.health_monitor.check_all()
                healthy = sum(1 for r in results.values() if r.get('status') == 'ok')
                total = len(results)
                logger.info(f"Health check: {healthy}/{total} services healthy")
                
                self._update_dashboard_state()
                
            except Exception as e:
                logger.error(f"Health check error: {e}")
            
            await asyncio.sleep(60)
    
    async def _daily_reset_loop(self):
        """Reset daily stats at midnight."""
        while self.running:
            now = datetime.now()
            
            if now.hour == 0 and now.minute == 0:
                if self.execution:
                    self.execution.reset_daily_stats()
                
                if self.analytics and self.notifier:
                    report = self.analytics.get_full_report()
                    await self.notifier.send_message(
                        f"📊 <b>Daily Summary</b>\n\n"
                        f"Equity: ${self.execution.positions.equity:.2f}\n"
                        f"Daily P&L: ${self.execution.positions.daily_pnl:.2f}\n"
                        f"Total Return: {report.get('total_return_pct', 0):.2f}%\n"
                        f"Sharpe: {report.get('sharpe_ratio', 0):.2f}\n"
                        f"Max DD: {report.get('max_drawdown', {}).get('max_drawdown_pct', 0):.2f}%\n"
                        f"Win Rate: {report.get('win_rate', {}).get('win_rate', 0):.1f}%\n"
                        f"Trades: {report.get('total_trades', 0)}"
                    )
                
                await asyncio.sleep(3600)  # Sleep for an hour to avoid multiple triggers
            else:
                await asyncio.sleep(30)  # Check every 30 seconds
    
    async def run(self):
        self.running = True
        logger.info("=" * 60)
        logger.info("Daemon STARTED")
        logger.info("=" * 60)
        
        # Send startup notification
        if self.notifier:
            await self.notifier.send_message(
                "🚀 <b>Futures Brokiepedia Daemon Online</b>\n\n"
                f"Mode: {'PAPER' if settings.is_paper_trading() else 'LIVE'}\n"
                f"Time: {datetime.now().isoformat()}"
            )
        
        # Start tasks
        tasks = [
            asyncio.create_task(self.ingestion.connect()),
            asyncio.create_task(self._health_check_loop()),
            asyncio.create_task(self._daily_reset_loop())
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def shutdown(self):
        logger.info("Shutting down daemon...")
        self.running = False
        
        if self.ingestion:
            await self.ingestion.disconnect()
        if self.exchanges:
            await self.exchanges.close()
        if self.questdb:
            self.questdb.close()
        if self.turso:
            self.turso.close()
        
        logger.info("Daemon shutdown complete")


daemon = TradingDaemon()


async def main():
    loop = asyncio.get_event_loop()
    
    def signal_handler(sig):
        logger.info(f"Received signal {sig}")
        asyncio.create_task(daemon.shutdown())
        loop.stop()
    
    loop.add_signal_handler(signal.SIGTERM, lambda: signal_handler('SIGTERM'))
    loop.add_signal_handler(signal.SIGINT, lambda: signal_handler('SIGINT'))
    
    try:
        await daemon.initialize()
        
        # Start API server in background thread
        api_thread = threading.Thread(
            target=start_api_server,
            kwargs={'host': '0.0.0.0', 'port': 8080},
            daemon=True
        )
        api_thread.start()
        logger.info("✅ API server started on :8080")
        
        await daemon.run()
    except Exception as e:
        logger.critical(f"Daemon fatal error: {e}")
        await daemon.shutdown()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
