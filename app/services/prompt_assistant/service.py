"""提示词助手服务"""
import uuid
import re
from typing import List, Dict, Any
from app.models.ideological import PromptAssistantConversation as PromptAssistantConversationModel
from app.models.enums import PromptAssistantSession
from app.schemas.ideological import PromptAssistantRequest, PromptAssistantResponse
from app.core.aigc.deepseek_client import DeepseekClient
from .prompts import SYSTEM_PROMPT
from .utils import extract_requirements, extract_prompt_from_response


class PromptAssistantService:
    """提示词助手服务类"""
    
    def __init__(self):
        self.system_prompt = SYSTEM_PROMPT
        self.deepseek_client = DeepseekClient()
    
    async def process_message(
        self,
        request: PromptAssistantRequest,
        user_id: int
    ) -> PromptAssistantResponse:
        """处理用户消息并生成回复"""
        session_id = request.session_id

        # 如果没有会话ID，创建新会话
        if not session_id:
            session_id = str(uuid.uuid4())

        # 获取会话历史
        conversation_history = await self._get_conversation_history(session_id, user_id)

        # 构建对话消息
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # 添加历史对话
        for conv in conversation_history:
            messages.append({"role": "user", "content": conv.user_message})
            messages.append({"role": "assistant", "content": conv.assistant_message})
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": request.message})
        
        # 调用AI模型生成回复
        response = await self.deepseek_client.chat(messages)
        assistant_message = response['choices'][0]['message']['content']
        
        # 提取需求信息
        extracted_requirements = extract_requirements(request.message, conversation_history)
        
        # 智能提取提示词
        suggested_prompt, final_prompt, next_stage = extract_prompt_from_response(
            assistant_message, 
            request.message,
            conversation_history
        )
        
        # 保存对话
        await self._save_conversation(
            session_id=session_id,
            user_message=request.message,
            assistant_message=assistant_message,
            session_stage=next_stage,
            extracted_requirements=extracted_requirements,
            suggested_prompt=suggested_prompt,
            final_prompt=final_prompt,
            is_final_prompt_generated=bool(final_prompt),
            user_id=user_id
        )

        return PromptAssistantResponse(
            session_id=session_id,
            assistant_message=assistant_message,
            session_stage=next_stage,
            extracted_requirements=extracted_requirements,
            suggested_prompt=suggested_prompt,
            final_prompt=final_prompt,
            is_final_prompt_ready=bool(final_prompt)
        )
    
    async def process_message_stream(
        self,
        request: PromptAssistantRequest,
        user_id: int
    ):
        """处理用户消息并生成流式回复"""
        session_id = request.session_id

        # 如果没有会话ID，创建新会话
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # 先发送会话ID
        yield {
            "type": "session_id",
            "session_id": session_id
        }

        # 获取会话历史
        conversation_history = await self._get_conversation_history(session_id, user_id)

        # 构建对话消息
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # 添加历史对话
        for conv in conversation_history:
            messages.append({"role": "user", "content": conv.user_message})
            messages.append({"role": "assistant", "content": conv.assistant_message})
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": request.message})
        
        # 流式生成回复
        full_response = ""
        try:
            async for chunk in self.deepseek_client.chat_stream(messages):
                # chunk 是 JSON 字符串，需要解析
                try:
                    import json
                    chunk_data = json.loads(chunk)
                    if 'choices' in chunk_data and len(chunk_data['choices']) > 0:
                        delta = chunk_data['choices'][0].get('delta', {})
                        content = delta.get('content', '')
                        if content:
                            full_response += content
                            yield {
                                "type": "content",
                                "content": content
                            }
                except json.JSONDecodeError:
                    # 如果不是JSON，直接使用
                    if chunk:
                        full_response += chunk
                        yield {
                            "type": "content",
                            "content": chunk
                        }
        except Exception as e:
            print(f"流式生成错误: {e}")
            import traceback
            traceback.print_exc()
            raise
        
        # 提取需求信息
        extracted_requirements = extract_requirements(request.message, conversation_history)
        
        # 智能提取提示词
        suggested_prompt, final_prompt, next_stage = extract_prompt_from_response(
            full_response, 
            request.message,
            conversation_history
        )
        
        # 保存对话
        await self._save_conversation(
            session_id=session_id,
            user_message=request.message,
            assistant_message=full_response,
            session_stage=next_stage,
            extracted_requirements=extracted_requirements,
            suggested_prompt=suggested_prompt,
            final_prompt=final_prompt,
            is_final_prompt_generated=bool(final_prompt),
            user_id=user_id
        )
        
        # 发送完成信息
        yield {
            "type": "done",
            "session_stage": next_stage.value if next_stage else None,
            "suggested_prompt": suggested_prompt,
            "final_prompt": final_prompt
        }
    
    async def _get_conversation_history(
        self, 
        session_id: str, 
        user_id: int
    ) -> List[PromptAssistantConversationModel]:
        """获取对话历史"""
        return await PromptAssistantConversationModel.filter(
            session_id=session_id,
            user_id=user_id
        ).order_by('created_at')
    
    async def _save_conversation(
        self,
        session_id: str,
        user_message: str,
        assistant_message: str,
        session_stage: PromptAssistantSession,
        user_id: int,
        extracted_requirements: Dict[str, Any] = None,
        suggested_prompt: str = None,
        final_prompt: str = None,
        is_final_prompt_generated: bool = False
    ):
        """保存对话记录"""
        await PromptAssistantConversationModel.create(
            session_id=session_id,
            user_message=user_message,
            assistant_message=assistant_message,
            session_stage=session_stage,
            extracted_requirements=extracted_requirements or {},
            suggested_prompt=suggested_prompt,
            final_prompt=final_prompt,
            is_final_prompt_generated=is_final_prompt_generated,
            user_id=user_id
        )
