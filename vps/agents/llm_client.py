"""OpenRouter LLM Client with usage tracking."""

import os
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import aiohttp

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Free models from OpenRouter
FREE_MODELS = [
    "openrouter/free",  # Router - picks best free model automatically
    "meta-llama/llama-3.3-70b-instruct",
    "meta-llama/llama-3.2-3b-instruct",
    "openai/gpt-oss-20b",
]


class LLMClient:
    """Client for OpenRouter API with usage tracking."""
    
    def __init__(self, model: str = "openrouter/free"):
        self.model = model
        self.api_key = OPENROUTER_API_KEY
        self.total_calls = 0
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost = 0.0
        self.call_history = []
        
    async def analyze(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Send analysis request to LLM and track usage."""
        if not self.api_key:
            return {
                "error": "No OPENROUTER_API_KEY configured",
                "direction": "flat",
                "confidence": 0.0,
            }
        
        start_time = datetime.now(timezone.utc)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    OPENROUTER_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://futures.brokiepedia.com",
                        "X-Title": "Futures Brokiepedia Trading Agents",
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        "temperature": 0.3,
                        "max_tokens": 500,
                        "response_format": {"type": "json_object"},
                    },
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as resp:
                    
                    response_time = (datetime.now(timezone.utc) - start_time).total_seconds()
                    
                    if resp.status == 200:
                        data = await resp.json()
                        
                        # Extract usage
                        usage = data.get("usage", {})
                        prompt_tokens = usage.get("prompt_tokens", 0)
                        completion_tokens = usage.get("completion_tokens", 0)
                        total_tokens = usage.get("total_tokens", 0)
                        
                        # Track usage
                        self.total_calls += 1
                        self.total_prompt_tokens += prompt_tokens
                        self.total_completion_tokens += completion_tokens
                        
                        # Cost calculation (free models = $0, but track anyway)
                        cost = 0.0  # Free models
                        self.total_cost += cost
                        
                        # Log call
                        call_log = {
                            "timestamp": start_time.isoformat(),
                            "model": self.model,
                            "prompt_tokens": prompt_tokens,
                            "completion_tokens": completion_tokens,
                            "total_tokens": total_tokens,
                            "cost_usd": cost,
                            "response_time_ms": int(response_time * 1000),
                            "status": "success",
                        }
                        self.call_history.append(call_log)
                        
                        # Parse response
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
                                "cost_usd": cost,
                                "response_time_ms": int(response_time * 1000),
                            },
                        }
                    else:
                        error_text = await resp.text()
                        return {
                            "error": f"API error {resp.status}: {error_text[:200]}",
                            "direction": "flat",
                            "confidence": 0.0,
                        }
                        
        except asyncio.TimeoutError:
            return {
                "error": "LLM API timeout (>30s)",
                "direction": "flat",
                "confidence": 0.0,
            }
        except Exception as e:
            return {
                "error": f"LLM error: {str(e)}",
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
            "total_cost_usd": self.total_cost,
            "recent_calls": self.call_history[-10:],  # Last 10 calls
        }
