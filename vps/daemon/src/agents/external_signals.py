"""External Signals Handler — ingests signals from Discord agents via API keys.

Each department (Quantitative, Technical, Sentiment, Fundamental, Statistical,
Qualitative) has unique API keys. Discord agents authenticate with these keys
and submit long/short signals. The handler stores them in Turso and feeds them
into the LangGraph pipeline on the next analysis cycle.
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

DEPARTMENT_NAMES = [
    'Quantitative', 'Technical', 'Sentiment',
    'Fundamental', 'Statistical', 'Qualitative'
]

DEPARTMENT_SLUGS = {
    'quantitative': 'Quantitative',
    'technical': 'Technical',
    'sentiment': 'Sentiment',
    'fundamental': 'Fundamental',
    'statistical': 'Statistical',
    'qualitative': 'Qualitative',
}


class ExternalSignalStore:
    """Stores and retrieves external signals from Discord agents."""

    def __init__(self, turso_client=None):
        self.turso = turso_client
        # In-memory signal cache (fresh per cycle)
        self._signals: Dict[str, List[dict]] = {
            dept: [] for dept in DEPARTMENT_NAMES
        }

    async def ingest_signal(self, signal: dict) -> dict:
        """Store an incoming signal from an external agent."""
        signal_id = f"ext_{uuid.uuid4().hex[:16]}"
        entry = {
            'id': signal_id,
            'department': signal.get('department', 'unknown'),
            'api_key_id': signal.get('api_key_id', ''),
            'direction': signal.get('direction', 'flat'),
            'confidence': float(signal.get('confidence', 0.0)),
            'symbol': signal.get('symbol', 'BTCUSDT'),
            'timeframe': signal.get('timeframe', '1h'),
            'reasoning': signal.get('reasoning', ''),
            'source': signal.get('source', 'discord'),
            'consumed': 0,
            'consumed_at': None,
            'created_at': int(datetime.now(timezone.utc).timestamp())
        }

        # Store in Turso
        if self.turso and self.turso.client:
            try:
                self.turso.client.execute("""
                    INSERT INTO external_signals (
                        id, department, api_key_id, direction, confidence,
                        symbol, timeframe, reasoning, source,
                        consumed, consumed_at, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, NULL, ?)
                """, [
                    entry['id'], entry['department'], entry['api_key_id'],
                    entry['direction'], entry['confidence'],
                    entry['symbol'], entry['timeframe'], entry['reasoning'],
                    entry['source'], entry['created_at']
                ])
                logger.info(f"External signal stored: {entry['department']} → {entry['direction']} ({entry['symbol']})")
            except Exception as e:
                logger.error(f"Failed to store external signal in Turso: {e}")

        # Also cache in memory for immediate LangGraph consumption
        dept_normalized = entry['department'].capitalize() if entry['department'] else 'Unknown'
        if dept_normalized in self._signals:
            # Keep at most 3 recent signals per department
            self._signals[dept_normalized].append(entry)
            if len(self._signals[dept_normalized]) > 3:
                self._signals[dept_normalized] = self._signals[dept_normalized][-3:]
            logger.info(f"External signal cached: {dept_normalized} has {len(self._signals[dept_normalized])} pending signals")
        else:
            logger.warning(f"Unknown department for external signal: {dept_normalized}")

        return entry

    def get_latest_signal(self, department: str) -> Optional[dict]:
        """Get the latest unconsumed signal for a department (memory cache)."""
        signals = self._signals.get(department, [])
        if not signals:
            return None
        return signals[-1]

    def mark_consumed(self, department: str, signal_id: str) -> None:
        """Mark a signal as consumed by the LangGraph pipeline."""
        signals = self._signals.get(department, [])
        self._signals[department] = [
            s for s in signals if s.get('id') != signal_id
        ]

        if self.turso and self.turso.client:
            try:
                self.turso.client.execute("""
                    UPDATE external_signals SET consumed = 1, consumed_at = ?
                    WHERE id = ?
                """, [int(datetime.now(timezone.utc).timestamp()), signal_id])
            except Exception as e:
                logger.error(f"Failed to mark signal consumed: {e}")

    def get_all_pending(self) -> Dict[str, List[dict]]:
        """Get all pending signals grouped by department."""
        return {
            dept: signals
            for dept, signals in self._signals.items()
            if signals
        }

    async def load_pending_from_db(self) -> int:
        """Load any unconsumed signals from Turso into memory (on startup)."""
        count = 0
        if self.turso and self.turso.client:
            try:
                rows = self.turso.client.execute("""
                    SELECT * FROM external_signals
                    WHERE consumed = 0
                    ORDER BY created_at ASC
                    LIMIT 50
                """)
                for row in rows:
                    dept_normalized = row.get('department', '').capitalize()
                    if dept_normalized in self._signals:
                        self._signals[dept_normalized].append(dict(row))
                        count += 1
            except Exception as e:
                logger.error(f"Failed to load pending signals: {e}")
        return count


def validate_signal_body(body: dict) -> Optional[str]:
    """Validate an incoming signal body. Returns error message or None."""
    if not body:
        return "Empty request body"

    direction = body.get('direction', '').lower()
    if direction not in ('long', 'short', 'flat'):
        return f"Invalid direction: '{direction}'. Must be 'long', 'short', or 'flat'"

    confidence = body.get('confidence')
    if confidence is not None:
        try:
            val = float(confidence)
            if val < 0 or val > 1:
                return f"Confidence must be between 0 and 1, got {val}"
        except (ValueError, TypeError):
            return f"Invalid confidence value: {confidence}"

    symbol = body.get('symbol', '')
    if not symbol:
        body['symbol'] = 'BTCUSDT'  # Default

    return None  # Valid
