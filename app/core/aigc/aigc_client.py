import os
from typing import Any, Dict, List

import httpx
from app.settings.config import settings


class AIGCClient:
    def __init__(self):
        self.provider = (getattr(settings, "AIGC_PROVIDER", None) or os.getenv("AIGC_PROVIDER", "deepseek")).lower()
        self.model = getattr(settings, "AIGC_MODEL", None) or os.getenv("AIGC_MODEL", "deepseek-chat")

        if self.provider in {"kimi", "moonshot"}:
            self.api_key = getattr(settings, "MOONSHOT_API_KEY", None) or os.getenv("MOONSHOT_API_KEY", "")
            self.base_url = (
                getattr(settings, "MOONSHOT_API_BASE", None)
                or os.getenv("MOONSHOT_API_BASE", "https://api.moonshot.cn/v1")
            ).rstrip("/")
        else:
            self.api_key = getattr(settings, "DEEPSEEK_API_KEY", None) or os.getenv("DEEPSEEK_API_KEY", "")
            self.base_url = (
                getattr(settings, "DEEPSEEK_API_BASE", None)
                or os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com")
            ).rstrip("/")

        if not self.api_key:
            raise RuntimeError("AIGC API key is not configured in environment")

        raw_timeout = getattr(settings, "AIGC_TIMEOUT", None) or os.getenv("AIGC_TIMEOUT", "60000")
        try:
            t = int(raw_timeout)
            self.timeout = t / 1000 if t >= 1000 else float(t)
        except Exception:
            try:
                self.timeout = float(raw_timeout)
            except Exception:
                self.timeout = 60.0

    def _sanitize_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove truly empty messages and ensure assistant/tool-call messages have non-empty content."""
        cleaned: List[Dict[str, Any]] = []
        for msg in messages or []:
            if not isinstance(msg, dict):
                continue

            # drop None values but keep useful keys
            msg = {k: v for k, v in msg.items() if v is not None}
            role = msg.get("role")
            content = msg.get("content")
            tool_calls = msg.get("tool_calls")

            if role == "assistant":
                if (content is None or str(content).strip() == "") and not tool_calls:
                    # skip empty assistant messages entirely
                    continue
                if tool_calls and (content is None or str(content).strip() == ""):
                    # Kimi要求assistant消息非空；添加简短占位
                    msg["content"] = "Using $web_search"
            else:
                if content is None or (isinstance(content, str) and content.strip() == ""):
                    # skip empty non-assistant messages
                    continue

            cleaned.append(msg)
        return cleaned

    def _build_url(self, path: str) -> str:
        base = self.base_url
        if base.endswith("/v1"):
            return f"{base}{path}"
        return f"{base}/v1{path}"

    @staticmethod
    def _format_error(e: Exception) -> str:
        """Human-friendly error string with type fallback when str(e) is empty."""
        msg = str(e) or ""
        if msg.strip():
            return msg
        return f"{e.__class__.__name__}"

    async def chat(self, messages: List[Dict[str, Any]], enable_web_search: bool = False):
        url = self._build_url("/chat/completions")
        messages = self._sanitize_messages(messages)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }
        
        # 如果启用联网搜索且是 Kimi，添加 $web_search 内置函数
        # 根据 Kimi 文档：使用 builtin_function 类型和 $web_search 函数名
        if enable_web_search and self.provider in {"kimi", "moonshot"}:
            payload["tools"] = [
                {
                    "type": "builtin_function",
                    "function": {
                        "name": "$web_search"
                    }
                }
            ]

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            
            # 处理 tool_calls 的情况
            if data.get("choices") and data["choices"][0].get("finish_reason") == "tool_calls":
                # 将 assistant 消息添加到上下文，确保 content 不为空
                assistant_msg = data["choices"][0]["message"]
                if "content" in assistant_msg and not assistant_msg["content"]:
                    # Kimi 不接受空 content，所以我们不添加 content 字段
                    assistant_msg = {
                        "role": assistant_msg["role"],
                        "tool_calls": assistant_msg.get("tool_calls", [])
                    }
                messages.append(assistant_msg)
                
                # 处理每个 tool_call
                for tool_call in data["choices"][0]["message"].get("tool_calls", []):
                    if tool_call["function"]["name"] == "$web_search":
                        import json
                        # 对于 $web_search，直接将参数原封不动返回
                        tool_result = json.loads(tool_call["function"]["arguments"])

                        # 添加 tool 消息
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "name": "$web_search",
                            "content": json.dumps(tool_result)
                        })

                # 再次调用 API 获取最终结果
                payload["messages"] = self._sanitize_messages(messages)
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()

            return data

    async def chat_stream(self, messages: List[Dict[str, Any]], enable_web_search: bool = False):
        """
        流式聊天。如果启用联网搜索，会先完成 tool_calls 流程，然后流式输出最终结果。
        """
        import logging
        import json as json_module
        logger = logging.getLogger(__name__)
        messages = self._sanitize_messages(messages)
        
        url = self._build_url("/chat/completions")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # 如果启用联网搜索，需要先处理 tool_calls
        if enable_web_search and self.provider in {"kimi", "moonshot"}:
            logger.info(f"联网搜索已启用，当前模型: {self.model}")
            
            # 第一步：发送非流式请求，检查是否需要 tool_calls
            check_payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "tools": [
                    {
                        "type": "builtin_function",
                        "function": {
                            "name": "$web_search"
                        }
                    }
                ]
            }
            
            logger.info(f"发送请求到 Kimi API: {json_module.dumps(check_payload, ensure_ascii=False)[:500]}")
            
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.post(url, json=check_payload, headers=headers)
                    resp.raise_for_status()
                    data = resp.json()
                    
                    finish_reason = data.get('choices', [{}])[0].get('finish_reason')
                    logger.info(f"第一次请求完成，finish_reason: {finish_reason}")
                    logger.info(f"响应数据: {json_module.dumps(data, ensure_ascii=False)[:1000]}")
                    
                    # 如果需要 tool_calls，处理它
                    if data.get("choices") and finish_reason == "tool_calls":
                        import json
                        logger.info("检测到 tool_calls，开始处理联网搜索")
                        # 将 assistant 消息添加到上下文
                        messages = list(messages)  # 复制一份，避免修改原始消息
                        
                        # 添加 assistant 消息，确保 content 不为空
                        assistant_msg = data["choices"][0]["message"]
                        logger.info(f"原始 assistant 消息: {assistant_msg}")
                        
                        # 如果 content 为空，设置为空字符串或删除该字段
                        if "content" in assistant_msg and not assistant_msg["content"]:
                            # Kimi 不接受空 content，所以我们不添加 content 字段
                            assistant_msg = {
                                "role": assistant_msg["role"],
                                "tool_calls": assistant_msg.get("tool_calls", [])
                            }
                            logger.info(f"修正后的 assistant 消息: {assistant_msg}")
                        messages.append(assistant_msg)
                        
                        # 处理每个 tool_call
                        for tool_call in data["choices"][0]["message"].get("tool_calls", []):
                            if tool_call["function"]["name"] == "$web_search":
                                # 对于 $web_search，直接将参数原封不动返回
                                tool_result = json.loads(tool_call["function"]["arguments"])
                                logger.info(f"$web_search 参数: {tool_result}")
                                
                                # 添加 tool 消息
                                messages.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call["id"],
                                    "name": "$web_search",
                                    "content": json.dumps(tool_result)
                                })
                        
                        logger.info(f"准备发送的完整消息列表（共{len(messages)}条）:")
                        for i, msg in enumerate(messages):
                            logger.info(f"  消息{i}: role={msg.get('role')}, has_content={('content' in msg)}, content_empty={msg.get('content') == '' if 'content' in msg else 'N/A'}")

                        # 现在用更新后的 messages 进行流式请求
                        stream_payload = {
                            "model": self.model,
                            "messages": messages,
                            "stream": True,
                            "tools": check_payload["tools"]
                        }
                    else:
                        # 如果不需要 tool_calls，直接返回结果
                        logger.info("未触发 tool_calls，直接返回结果")
                        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                        yield content
                        return
            except httpx.HTTPStatusError as e:
                logger.error(f"Kimi API 返回错误: {e.response.status_code}")
                logger.error(f"错误详情: {e.response.text}")
                raise
            except Exception as e:
                logger.exception(f"请求失败: {str(e)}")
                raise
        else:
            # 不启用联网搜索，直接流式请求
            stream_payload = {
                "model": self.model,
                "messages": messages,
                "stream": True,
            }

        # 执行流式请求
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", url, json=stream_payload, headers=headers) as resp:
                resp.raise_for_status()
                async for chunk in resp.aiter_bytes():
                    if not chunk:
                        continue
                    try:
                        text = chunk.decode("utf-8")
                    except Exception:
                        text = chunk.decode("latin-1", errors="ignore")

                    for line in text.splitlines():
                        line = line.strip()
                        if not line:
                            continue
                        if line.startswith("data:"):
                            data_part = line[len("data:") :].strip()
                            if data_part == "[DONE]":
                                return
                            
                            # 解析 JSON 并提取 content
                            try:
                                import json
                                chunk_data = json.loads(data_part)
                                # 提取 delta.content
                                if isinstance(chunk_data, dict) and "choices" in chunk_data:
                                    for choice in chunk_data.get("choices", []):
                                        delta = choice.get("delta", {})
                                        content = delta.get("content", "")
                                        if content:
                                            yield content
                                else:
                                    # 如果不是标准格式，直接输出
                                    yield data_part
                            except json.JSONDecodeError:
                                # 如果不是 JSON，直接输出
                                yield data_part
                        else:
                            # 非 data: 开头的行，尝试解析
                            try:
                                import json
                                chunk_data = json.loads(line)
                                if isinstance(chunk_data, dict) and "choices" in chunk_data:
                                    for choice in chunk_data.get("choices", []):
                                        delta = choice.get("delta", {})
                                        content = delta.get("content", "")
                                        if content:
                                            yield content
                                else:
                                    yield line
                            except json.JSONDecodeError:
                                yield line

    async def upload_file(self, file_path: str, purpose: str = "file-extract", timeout: float = None) -> Dict[str, Any]:
        url = self._build_url("/files")
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {"purpose": purpose}
        use_timeout = timeout if timeout is not None else self.timeout
        async with httpx.AsyncClient(timeout=use_timeout) as client:
            with open(file_path, "rb") as handle:
                files = {"file": (os.path.basename(file_path), handle)}
                resp = await client.post(url, headers=headers, files=files, data=data)
                resp.raise_for_status()
                return resp.json()

    async def get_file_content(self, file_id: str) -> str:
        url = self._build_url(f"/files/{file_id}/content")
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            return resp.text

    async def delete_file(self, file_id: str) -> None:
        url = self._build_url(f"/files/{file_id}")
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.delete(url, headers=headers)
            resp.raise_for_status()

    async def extract_file_text(self, file_path: str, max_retries: int = 3) -> str:
        """提取文件文本内容，使用更长的超时时间，支持重试"""
        # 文件处理需要更长的超时时间（5分钟）
        file_timeout = max(self.timeout * 5, 300.0)
        
        last_error = None
        for attempt in range(max_retries):
            file_id = None
            try:
                # 上传文件时也使用更长的超时时间
                file_obj = await self.upload_file(file_path, purpose="file-extract", timeout=file_timeout)
                file_id = file_obj.get("id")
                if not file_id:
                    raise RuntimeError("file upload failed: missing file id")
                
                # 使用更长的超时时间获取文件内容
                url = self._build_url(f"/files/{file_id}/content")
                headers = {"Authorization": f"Bearer {self.api_key}"}
                async with httpx.AsyncClient(timeout=file_timeout) as client:
                    resp = await client.get(url, headers=headers)
                    resp.raise_for_status()
                    return resp.text
                    
            except httpx.HTTPStatusError as e:
                last_error = e
                # 如果是 502/503/504 这类服务端错误，可以重试
                if e.response.status_code in [502, 503, 504] and attempt < max_retries - 1:
                    import asyncio
                    # 等待一段时间后重试（指数退避）
                    wait_time = (attempt + 1) * 2
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise
            except Exception as e:
                last_error = e
                raise
            finally:
                # 清理文件
                if file_id:
                    try:
                        await self.delete_file(file_id)
                    except Exception:
                        pass
        
        # 如果所有重试都失败了
        if last_error:
            raise last_error
        raise RuntimeError("file extraction failed after all retries")

    async def extract_url_content(self, url: str, max_chars: int = 3000) -> str:
        """使用 Kimi 的联网功能提取 URL 内容"""
        if self.provider not in {"kimi", "moonshot"}:
            raise RuntimeError("URL content extraction is only supported with Kimi provider")
        
        messages = [
            {
                "role": "system",
                "content": "你是一个网页内容提取助手。请提取网页的主要文本内容，去除广告、导航等无关信息。"
            },
            {
                "role": "user",
                "content": f"请访问这个网址并提取主要内容（限制在{max_chars}字符内）：{url}"
            }
        ]
        
        try:
            # 使用 enable_web_search=True 会自动处理 tool_calls 流程
            response = await self.chat(messages, enable_web_search=True)
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # 限制字符数
            if len(content) > max_chars:
                content = content[:max_chars] + "..."
            
            return content
        except Exception as e:
            raise RuntimeError(f"Failed to extract URL content: {e}") from e

