"""DeepSeek API Client for Orchestrator-level decisions."""

import os
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any
import aiohttp

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"  # DeepSeek V4 Flash


class DeepSeekClient:
    """Client for DeepSeek API with usage tracking."""

    def __init__(self, model: str = DEEPSEEK_MODEL):
        self.model = model
        self.api_key = DEEPSEEK_API_KEY
        self.total_calls = 0
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost = 0.0
        self.call_history = []

    async def analyze(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Send analysis request to DeepSeek and track usage."""
        if not self.api_key or self.api_key == "your_key_here":
            return {
                "error": "No DEEPSEEK_API_KEY configured",
                "direction": "flat",
                "confidence": 0.0,
            }

        start_time = datetime.now(timezone.utc)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    DEEPSEEK_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        "temperature": 0.2,
                        "max_tokens": 800,
                        "response_format": {"type": "json_object"},
                    },
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as resp:

                    response_time = (datetime.now(timezone.utc) - start_time).total_seconds()

                    if resp.status == 200:
                        data = await resp.json()

                        usage = data.get("usage", {})
                        prompt_tokens = usage.get("prompt_tokens", 0)
                        completion_tokens = usage.get("completion_tokens", 0)
                        total_tokens = usage.get("total_tokens", 0)

                        # Track usage
                        self.total_calls += 1
                        self.total_prompt_tokens += prompt_tokens
                        self.total_completion_tokens += completion_tokens

                        # Cost: DeepSeek V4 Flash is very cheap
                        # ~$0.0001 per 1K tokens
                        cost = (total_tokens / 1000) * 0.0001
                        self.total_cost += cost

                        call_log = {
                            "timestamp": start_time.isoformat(),
                            "model": self.model,
                            "prompt_tokens": prompt_tokens,
                            "completion_tokens": completion_tokens,
                            "total_tokens": total_tokens,
                            "cost_usd": round(cost, 6),
                            "response_time_ms": int(response_time * 1000),
                            "status": "success",
                        }
                        self.call_history.append(call_log)

                        content = data["choices"][0]["message"]["content"]
                        result = json.loads(content)

                        return {
                            "success": True,
                            "direction": result.get("direction", "flat"),
                            "confidence": result.get("confidence", 0.0),
                            "reason": result.get("reason", ""),
                            "metrics": result.get("metrics", {}),
                            "usage": {
                                "prompt_tokens": prompt_tokens,
                                "completion_tokens": completion_tokens,
                                "total_tokens": total_tokens,
                                "cost_usd": round(cost, 6),
                                "response_time_ms": int(response_time * 1000),
                            },
                        }
                    else:
                        error_text = await resp.text()
                        return {
                            "error": f"DeepSeek API error {resp.status}: {error_text[:200]}",
                            "direction": "flat",
                            "confidence": 0.0,
                        }

        except asyncio.TimeoutError:
            return {
                "error": "DeepSeek API timeout (>30s)",
                "direction": "flat",
                "confidence": 0.0,
            }
        except Exception as e:
            return {
                "error": f"DeepSeek error: {str(e)}",
                "direction": "flat",
                "confidence": 0.0,
            }

    def get_usage_stats(self) -> Dict:
        """Get usage statistics."""
        return {
            "model": self.model,
            "total_calls": self.total_calls,
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_prompt_tokens + self.total_completion_tokens,
            "total_cost_usd": round(self.total_cost, 6),
            "recent_calls": self.call_history[-10:],
        }
