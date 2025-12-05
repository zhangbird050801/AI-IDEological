import time
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.ideological import (
    PromptAssistantRequest,
    PromptAssistantResponse,
    PromptAssistantSessionRequest,
    PromptAssistantSessionResponse,
    PromptAssistantConversation,
)
from app.models.ideological import (
    PromptAssistantConversation as PromptAssistantConversationModel,
    PromptAssistantTemplate as PromptAssistantTemplateModel,
)
from app.models.admin import User
from app.models.enums import PromptAssistantSession
from app.core.dependency import AuthControl
from app.services.prompt_assistant import PromptAssistantService

router = APIRouter()
prompt_assistant_service = PromptAssistantService()


# PromptAssistantService 已移至 app/services/prompt_assistant/service.py

# === API路由定义 ===

@router.post("/chat", summary="与提示词助手对话")
async def chat_with_assistant(
    request: PromptAssistantRequest,
    current_user: User = Depends(AuthControl.is_authed)
) -> PromptAssistantResponse:
    """与提示词助手进行对话"""
    start_time = time.time()

    try:
        response = await prompt_assistant_service.process_message(request, current_user.id)

        # 记录生成时间
        generation_time = int((time.time() - start_time) * 1000)
        response.generation_time = generation_time

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理消息时出错: {str(e)}")


@router.post("/chat/stream", summary="与提示词助手对话（流式输出）")
async def chat_with_assistant_stream(
    request: PromptAssistantRequest,
    current_user: User = Depends(AuthControl.is_authed)
):
    """与提示词助手进行对话，使用流式输出"""
    from fastapi.responses import StreamingResponse
    import json
    
    async def generate():
        try:
            async for chunk in prompt_assistant_service.process_message_stream(request, current_user.id):
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
        except Exception as e:
            import traceback
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            print(f"流式输出错误: {error_msg}")
            error_data = {"type": "error", "error": str(e)}
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.get("/session/{session_id}", summary="获取会话信息")
async def get_session(
    session_id: str,
    current_user: User = Depends(AuthControl.is_authed)
) -> PromptAssistantSessionResponse:
    """获取指定会话的详细信息"""
    return await prompt_assistant_service.get_session(session_id, current_user.id)


@router.get("/sessions", summary="获取用户的会话列表")
async def get_user_sessions(
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(AuthControl.is_authed)
):
    """获取用户的所有会话列表"""
    # 获取用户的所有对话，按会话ID分组
    conversations = await PromptAssistantConversationModel.filter(
        user_id=current_user.id
    ).order_by('-created_at')

    # 按会话ID分组
    sessions = {}
    for conv in conversations:
        if conv.session_id not in sessions:
            sessions[conv.session_id] = {
                'session_id': conv.session_id,
                'created_at': conv.created_at,
                'last_updated': conv.updated_at,
                'current_stage': conv.session_stage,
                'is_completed': conv.session_stage == PromptAssistantSession.COMPLETED,
                'message_count': 0,
                'has_final_prompt': False
            }

        sessions[conv.session_id]['message_count'] += 1
        sessions[conv.session_id]['last_updated'] = max(
            sessions[conv.session_id]['last_updated'],
            conv.updated_at
        )

        if conv.final_prompt and not sessions[conv.session_id]['has_final_prompt']:
            sessions[conv.session_id]['has_final_prompt'] = True

    # 转换为列表并排序
    session_list = sorted(
        sessions.values(),
        key=lambda x: x['last_updated'],
        reverse=True
    )

    # 分页
    total = len(session_list)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_sessions = session_list[start:end]

    return {
        'items': paginated_sessions,
        'total': total,
        'page': page,
        'page_size': page_size,
        'pages': (total + page_size - 1) // page_size
    }


@router.delete("/session/{session_id}", summary="删除会话")
async def delete_session(
    session_id: str,
    current_user: User = Depends(AuthControl.is_authed)
):
    """删除指定会话及其所有对话记录"""
    deleted_count = await PromptAssistantConversationModel.filter(
        session_id=session_id,
        user_id=current_user.id
    ).delete()

    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="会话不存在")

    return {"message": "会话删除成功", "deleted_count": deleted_count}


@router.get("/templates", summary="获取提示词助手模板")
async def get_assistant_templates(
    template_type: str = None,
    current_user: User = Depends(AuthControl.is_authed)
):
    """获取预置的提示词助手模板"""
    query = PromptAssistantTemplateModel.filter(is_active=True)

    if template_type:
        query = query.filter(template_type=template_type)

    templates = await query.order_by('-rating', '-usage_count')

    return [template for template in templates]


@router.post("/templates/{template_id}/use", summary="使用模板")
async def use_template(
    template_id: int,
    current_user: User = Depends(AuthControl.is_authed)
):
    """使用指定的助手模板"""
    template = await PromptAssistantTemplateModel.get_or_none(
        id=template_id,
        is_active=True
    )

    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    # 增加使用次数
    await template.update_from_dict({
        'usage_count': template.usage_count + 1
    })
    await template.save()

    return {
        "template": template,
        "message": "模板使用成功"
    }