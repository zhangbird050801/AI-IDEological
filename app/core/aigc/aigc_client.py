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

    def _build_url(self, path: str) -> str:
        base = self.base_url
        if base.endswith("/v1"):
            return f"{base}{path}"
        return f"{base}/v1{path}"

    async def chat(self, messages: List[Dict[str, Any]]):
        url = self._build_url("/chat/completions")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            return resp.json()

    async def chat_stream(self, messages: List[Dict[str, Any]]):
        url = self._build_url("/chat/completions")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", url, json=payload, headers=headers) as resp:
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
                            yield data_part
                        else:
                            yield line

    async def upload_file(self, file_path: str, purpose: str = "file-extract") -> Dict[str, Any]:
        url = self._build_url("/files")
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {"purpose": purpose}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
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

    async def extract_file_text(self, file_path: str) -> str:
        file_obj = await self.upload_file(file_path, purpose="file-extract")
        file_id = file_obj.get("id")
        if not file_id:
            raise RuntimeError("file upload failed: missing file id")
        try:
            return await self.get_file_content(file_id)
        finally:
            try:
                await self.delete_file(file_id)
            except Exception:
                pass
