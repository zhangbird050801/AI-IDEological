import httpx
import os
from typing import List, Dict, Any
from app.settings.config import settings


class DeepseekClient:
    def __init__(self):
        # 从 settings 对象读取 AIGC_PROVIDER（会自动加载 .env 文件）
        provider = getattr(settings, 'AIGC_PROVIDER', 'deepseek').lower()
        
        if provider == 'kimi' or provider == 'moonshot':
            # 使用 Kimi/Moonshot API
            self.api_key = getattr(settings, 'MOONSHOT_API_KEY', None) or ''
            self.base_url = (getattr(settings, 'MOONSHOT_API_BASE', None) or 'https://api.moonshot.cn/v1').rstrip('/')
            self.model = getattr(settings, 'AIGC_MODEL', None) or 'moonshot-v1-8k'
        else:
            # 使用 DeepSeek API (默认)
            self.api_key = getattr(settings, 'DEEPSEEK_API_KEY', None) or ''
            self.base_url = (getattr(settings, 'DEEPSEEK_API_BASE', None) or 'https://api.deepseek.com').rstrip('/')
            self.model = getattr(settings, 'AIGC_MODEL', None) or 'deepseek-chat'

        # AIGC_TIMEOUT may be expressed in milliseconds in your .env; accept ms or seconds
        raw_timeout = getattr(settings, 'AIGC_TIMEOUT', None) or '60000'
        try:
            t = int(raw_timeout)
            # if large (>=1000) assume ms
            self.timeout = t / 1000 if t >= 1000 else float(t)
        except Exception:
            try:
                self.timeout = float(raw_timeout)
            except Exception:
                self.timeout = 60.0
        
        print(f"🤖 AIGC Provider: {provider}")
        print(f"🔗 API Base URL: {self.base_url}")
        print(f"📦 Model: {self.model}")

    async def chat(self, messages: List[Dict[str, Any]]):
        """Call DeepSeek/OpenAI-compatible chat completions endpoint.

        Raises RuntimeError if API key is not configured. Raises httpx.HTTPError for network/HTTP errors.
        Returns the parsed JSON response on success.
        """
        url = f"{self.base_url}/v1/chat/completions"

        if not self.api_key:
            # Fail fast and with a clear message instead of sending an empty Authorization header
            raise RuntimeError("DEEPSEEK_API_KEY is not configured in environment")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            return resp.json()

    async def chat_stream(self, messages: List[Dict[str, Any]]):
        """Async generator that yields string chunks from DeepSeek streaming responses.

        The DeepSeek/OpenAI-compatible streaming protocol often emits lines prefixed with `data:`.
        This function reads the response stream and yields decoded text fragments for the caller
        to forward to clients (or aggregate into a single string).
        """
        url = f"{self.base_url}/v1/chat/completions"

        if not self.api_key:
            raise RuntimeError("DEEPSEEK_API_KEY is not configured in environment")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", url, json=payload, headers=headers) as resp:
                resp.raise_for_status()
                async for chunk in resp.aiter_bytes():
                    if not chunk:
                        continue
                    try:
                        text = chunk.decode('utf-8')
                    except Exception:
                        text = chunk.decode('latin-1', errors='ignore')

                    # If server uses SSE `data: ...\n\n`, extract payloads
                    for line in text.splitlines():
                        line = line.strip()
                        if not line:
                            continue
                        if line.startswith('data:'):
                            data_part = line[len('data:'):].strip()
                            # Some streams use [DONE] marker
                            if data_part == '[DONE]':
                                return
                            yield data_part
                        else:
                            # plain chunk
                            yield line
