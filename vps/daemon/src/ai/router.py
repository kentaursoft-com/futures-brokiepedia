"""AI Model Router for enhanced trading signals."""
import logging
import requests
import json
import time
from typing import Dict, Optional, List

from ..config.settings import settings

logger = logging.getLogger(__name__)

class AIModelRouter:
    """Routes requests between OpenRouter and DeepSeek APIs."""
    
    def __init__(self):
        self.openrouter_key = settings.ai.OPENROUTER_API_KEY
        self.deepseek_key = settings.ai.DEEPSEEK_API_KEY
        self.default_model = getattr(settings.ai, 'DEFAULT_MODEL', 'openrouter')
        
        self.models = {
            'openrouter': {
                'base_url': 'https://openrouter.ai/api/v1',
                'model': 'deepseek/deepseek-chat'
            },
            'deepseek': {
                'base_url': 'https://api.deepseek.com/v1',
                'model': 'deepseek-chat'
            }
        }
        
        logger.info("✅ AI Model Router initialized")
    
    def _call_openrouter(self, messages: List[Dict], temperature: float = 0.7) -> Optional[str]:
        """Call OpenRouter API."""
        if not self.openrouter_key:
            return None
        
        headers = {
            'Authorization': f'Bearer {self.openrouter_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://futures.brokiepedia.com',
            'X-Title': 'Futures Brokiepedia AI'
        }
        
        payload = {
            'model': self.models['openrouter']['model'],
            'messages': messages,
            'temperature': temperature,
            'max_tokens': 1000
        }
        
        try:
            start = time.time()
            response = requests.post(
                f"{self.models['openrouter']['base_url']}/chat/completions",
                headers=headers, json=payload, timeout=30
            )
            elapsed = (time.time() - start) * 1000
            
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                logger.info(f"✅ OpenRouter response in {elapsed:.0f}ms")
                return content
            else:
                logger.error(f"OpenRouter error: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"OpenRouter exception: {e}")
            return None
    
    def _call_deepseek(self, messages: List[Dict], temperature: float = 0.7) -> Optional[str]:
        """Call DeepSeek API."""
        if not self.deepseek_key:
            return None
        
        headers = {
            'Authorization': f'Bearer {self.deepseek_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': self.models['deepseek']['model'],
            'messages': messages,
            'temperature': temperature,
            'max_tokens': 1000
        }
        
        try:
            start = time.time()
            response = requests.post(
                f"{self.models['deepseek']['base_url']}/chat/completions",
                headers=headers, json=payload, timeout=30
            )
            elapsed = (time.time() - start) * 1000
            
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                logger.info(f"✅ DeepSeek response in {elapsed:.0f}ms")
                return content
            else:
                logger.error(f"DeepSeek error: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"DeepSeek exception: {e}")
            return None
    
    def analyze_market(self, symbol: str, price: float, indicators: Dict, 
                       provider: str = None) -> Optional[Dict]:
        """Get AI market analysis for a trading signal."""
        provider = provider or self.default_model
        
        system_prompt = """You are an expert crypto futures trading analyst. 
        Analyze the provided technical indicators and give a recommendation.
        Respond in JSON format:
        - recommendation: STRONG_BUY, BUY, HOLD, SELL, or STRONG_SELL
        - confidence: number 0-100
        - reasoning: brief explanation
        - risk_level: LOW, MEDIUM, or HIGH"""
        
        user_prompt = f"Analyze {symbol} at ${price:.2f}: {json.dumps(indicators)}"
        
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]
        
        response = self._call_openrouter(messages) if provider == 'openrouter' else self._call_deepseek(messages)
        
        if response:
            try:
                # Extract JSON from response
                if '```json' in response:
                    json_str = response.split('```json')[1].split('```')[0].strip()
                elif '```' in response:
                    json_str = response.split('```')[1].split('```')[0].strip()
                else:
                    json_str = response.strip()
                
                return json.loads(json_str)
            except json.JSONDecodeError:
                logger.error("Failed to parse AI response")
                return None
        
        return None
    
    def health_check(self) -> Dict:
        """Check AI model API health."""
        health = {'openrouter': False, 'deepseek': False}
        
        if self.openrouter_key:
            try:
                resp = requests.get('https://openrouter.ai/api/v1/auth/key',
                    headers={'Authorization': f'Bearer {self.openrouter_key}'}, timeout=5)
                health['openrouter'] = resp.status_code == 200
            except:
                pass
        
        if self.deepseek_key:
            try:
                resp = requests.get('https://api.deepseek.com/user/balance',
                    headers={'Authorization': f'Bearer {self.deepseek_key}'}, timeout=5)
                health['deepseek'] = resp.status_code == 200
            except:
                pass
        
        return health
