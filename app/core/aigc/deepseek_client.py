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
        """Async generator that yields parsed content from streaming responses.

        This method parses the SSE stream and yields only the actual content text,
        not the raw JSON chunks. This makes it easier for consumers to use.
        """
        url = f"{self.base_url}/v1/chat/completions"

        if not self.api_key:
            raise RuntimeError("API key is not configured in environment")

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
                buffer = ""
                async for chunk in resp.aiter_bytes():
                    if not chunk:
                        continue
                    try:
                        text = chunk.decode('utf-8')
                    except Exception:
                        text = chunk.decode('latin-1', errors='ignore')

                    buffer += text
                    
                    # Process complete lines
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        
                        if not line:
                            continue
                        
                        # Skip empty data markers
                        if line == 'data:' or line == 'data: ':
                            continue
                            
                        # Handle SSE format: "data: {...}"
                        if line.startswith('data:'):
                            data_part = line[5:].strip()  # Remove "data:" prefix
                            
                            # Check for [DONE] marker
                            if data_part == '[DONE]':
                                return
                            
                            # Parse JSON and extract content - NEVER output raw JSON
                            try:
                                import json
                                chunk_data = json.loads(data_part)
                                
                                # Extract content from delta
                                if isinstance(chunk_data, dict) and 'choices' in chunk_data:
                                    choices = chunk_data.get('choices', [])
                                    if choices and len(choices) > 0:
                                        choice = choices[0]
                                        delta = choice.get('delta', {})
                                        content = delta.get('content')
                                        
                                        # Only yield if content is a non-empty string
                                        if content and isinstance(content, str):
                                            yield content
                                        
                            except json.JSONDecodeError as e:
                                # Log parsing error but NEVER output the raw data
                                print(f"⚠️ SSE JSON解析失败: {e}, 数据: {data_part[:100]}")
                                # Skip this chunk completely
                                continue
                            except Exception as e:
                                # Catch any other errors and skip
                                print(f"⚠️ 处理SSE数据时出错: {e}")
                                continue
                        else:
                            # Try to parse as JSON directly (non-SSE format)
                            # This handles cases where the stream doesn't use SSE format
                            try:
                                import json
                                chunk_data = json.loads(line)
                                
                                # Extract content from delta
                                if isinstance(chunk_data, dict) and 'choices' in chunk_data:
                                    choices = chunk_data.get('choices', [])
                                    if choices and len(choices) > 0:
                                        choice = choices[0]
                                        delta = choice.get('delta', {})
                                        content = delta.get('content')
                                        
                                        # Only yield if content is a non-empty string
                                        if content and isinstance(content, str):
                                            yield content
                                        
                            except json.JSONDecodeError:
                                # Not JSON, skip silently
                                # NEVER output raw text to avoid leaking JSON chunks
                                pass
                            except Exception:
                                # Catch any other errors and skip
                                pass
