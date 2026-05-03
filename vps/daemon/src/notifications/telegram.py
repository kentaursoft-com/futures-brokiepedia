"""Telegram notification service."""
import logging
from typing import Optional
import aiohttp

logger = logging.getLogger(__name__)

class TelegramNotifier:
    """Send notifications via Telegram Bot API."""
    
    def __init__(self, bot_token: str, chat_id: str = ""):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
    async def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """Send a text message."""
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram credentials not configured")
            return False
        
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": parse_mode
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        logger.info("Telegram message sent")
                        return True
                    else:
                        logger.error(f"Telegram API error: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    async def send_alert(self, event_type: str, details: dict):
        """Send formatted alert based on event type."""
        messages = {
            'kill_switch': f"🛑 <b>KILL-SWITCH TRIGGERED</b>\n\nAll trading halted.\nReason: {details.get('reason', 'Manual')}",
            'soft_drawdown': f"⚠️ <b>Soft Drawdown Alert</b>\n\nCurrent: {details.get('drawdown', 0):.2f}%\nThreshold: 3%\nReducing position sizes by 50%.",
            'hard_drawdown': f"🔴 <b>HARD DRAWDOWN - HALTING</b>\n\nCurrent: {details.get('drawdown', 0):.2f}%\nThreshold: 6%\nAll trading stopped immediately!",
            'gate1_pass': f"✅ <b>Strategy Gate 1 Passed</b>\n\nStrategy: {details.get('strategy', 'Unknown')}\nWin Rate: {details.get('win_rate', 0):.1f}%\nSharpe: {details.get('sharpe', 0):.2f}",
            'gate2_pass': f"✅ <b>Strategy Gate 2 Passed</b>\n\nStrategy: {details.get('strategy', 'Unknown')}\nPaper trades: {details.get('trades', 0)}\nWin Rate: {details.get('win_rate', 0):.1f}%",
            'promotion': f"🚀 <b>Strategy Promoted to LIVE</b>\n\nStrategy: {details.get('strategy', 'Unknown')}\nCapital transition: 70% → 30% → Full",
            'demotion': f"📉 <b>Strategy Demoted</b>\n\nStrategy: {details.get('strategy', 'Unknown')}\nWin rate dropped {details.get('drop', 0):.1f}% below baseline",
            'evolution_start': f"🔄 <b>New Evolution Cycle Started</b>\n\nSearching for new strategies...",
            'daemon_offline': f"🔴 <b>VPS Daemon Offline</b>\n\nNo heartbeat received for {details.get('seconds', 0)}s",
            'api_failure': f"⚠️ <b>Exchange API Failure</b>\n\nExchange: {details.get('exchange', 'Unknown')}\nError: {details.get('error', 'Unknown')}",
            'turso_sync_fail': f"⚠️ <b>Turso Sync Failure</b>\n\nDatabase sync has been failing for {details.get('minutes', 0)} minutes"
        }
        
        message = messages.get(event_type, f"📢 <b>Alert: {event_type}</b>\n\n{details}")
        return await self.send_message(message)
