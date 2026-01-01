from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from app.core.aigc.aigc_client import AIGCClient
from app.settings.config import settings
from fastapi.responses import StreamingResponse

router = APIRouter()

class Message(BaseModel):
	role: str
	content: str

class ChatRequest(BaseModel):
	messages: List[Message]
	enable_web_search: Optional[bool] = False

class ChatResponse(BaseModel):
	reply: str

@router.post('/chat', response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
	client = AIGCClient()
	try:
		data = await client.chat([m.dict() for m in req.messages], enable_web_search=req.enable_web_search)
		reply = data["choices"][0]["message"]["content"]
		return ChatResponse(reply=reply)
	except Exception as e:
		raise HTTPException(status_code=502, detail=str(e))


class DiagResponse(BaseModel):
	has_key: bool
	base_url: str
	model: str
	timeout_seconds: float


@router.get('/diag', response_model=DiagResponse)
async def diag():
	# Return diagnostic info about AIGC configuration without revealing the API key
	provider = getattr(settings, 'AIGC_PROVIDER', None) or 'deepseek'
	if provider in {"kimi", "moonshot"}:
		api_key = getattr(settings, 'MOONSHOT_API_KEY', None)
		base = getattr(settings, 'MOONSHOT_API_BASE', None) or ''
	else:
		api_key = getattr(settings, 'DEEPSEEK_API_KEY', None)
		base = getattr(settings, 'DEEPSEEK_API_BASE', None) or ''
	model = getattr(settings, 'AIGC_MODEL', None) or ''
	raw_timeout = getattr(settings, 'AIGC_TIMEOUT', None) or '60000'
	try:
		t = int(raw_timeout)
		timeout_seconds = t / 1000 if t >= 1000 else float(t)
	except Exception:
		try:
			timeout_seconds = float(raw_timeout)
		except Exception:
			timeout_seconds = 60.0

	return DiagResponse(
		has_key=bool(api_key),
		base_url=base,
		model=model,
		timeout_seconds=timeout_seconds,
	)


@router.post('/chat/stream')
async def chat_stream_endpoint(req: ChatRequest):
	import logging
	import json
	logger = logging.getLogger(__name__)
	logger.info(f"收到流式聊天请求，enable_web_search={req.enable_web_search}")
	
	client = AIGCClient()

	async def event_generator():
		try:
			async for chunk in client.chat_stream([m.dict() for m in req.messages], enable_web_search=req.enable_web_search):
				# Always JSON SSE, consistent with prompt-assistant.
				yield f"data: {json.dumps({'type': 'content', 'content': chunk}, ensure_ascii=False)}\n\n"
			# finished
			yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"
		except Exception as e:
			msg = str(e) or e.__class__.__name__
			yield f"data: {json.dumps({'type': 'error', 'error': msg}, ensure_ascii=False)}\n\n"

	return StreamingResponse(event_generator(), media_type='text/event-stream')
