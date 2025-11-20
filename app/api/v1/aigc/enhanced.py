from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
from app.core.aigc.deepseek_client import DeepseekClient
from app.schemas.ideological import (
    AIGCGenerationRequest,
    AIGCGenerationResponse,
    GenerationHistoryCreate,
    GenerationHistoryUpdate,
    GenerationHistoryInDB,
)
from app.models.ideological import (
    GenerationHistory as GenerationHistoryModel,
    PromptTemplate as PromptTemplateModel,
    IdeologicalCase as IdeologicalCaseModel,
)
from app.models.admin import User
from app.core.dependency import AuthControl
from fastapi.responses import StreamingResponse
import time
import json

router = APIRouter()

class EnhancedAIGCService:
    def __init__(self):
        self.client = DeepseekClient()

    async def generate_with_template(
        self,
        request: AIGCGenerationRequest,
        user_id: int
    ) -> AIGCGenerationResponse:
        start_time = time.time()
        token_count = 0

        try:
            # 如果使用了模板，先渲染模板
            if request.template_id and request.template_variables:
                template = await PromptTemplateModel.get_or_none(
                    id=request.template_id,
                    is_active=True
                )
                if not template:
                    raise HTTPException(status_code=404, detail="模板不存在或已禁用")

                # 渲染模板
                prompt = template.template_content
                for var, value in request.template_variables.items():
                    placeholder = f"{{{{{var}}}}}"
                    prompt = prompt.replace(placeholder, str(value))

                # 增加模板使用次数
                await template.update_from_dict({
                    "usage_count": template.usage_count + 1
                })
                await template.save()
            else:
                prompt = request.prompt

            # 构建系统提示词，增强思政教育效果
            system_prompt = self._build_system_prompt(
                request.generation_type,
                request.software_engineering_chapter,
                request.ideological_theme
            )

            # 构建消息数组
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]

            # 调用AI生成内容
            data = await self.client.chat(messages)
            content = data["choices"][0]["message"]["content"]

            # 计算Token消耗和生成时间
            generation_time = int((time.time() - start_time) * 1000)  # 转换为毫秒
            # 注意：这里简化处理，实际应该从API响应中获取token数量
            token_count = len(content.split()) * 1.3  # 估算token数

            # 保存生成历史
            history_data = GenerationHistoryCreate(
                user_input=prompt,
                generated_content=content,
                prompt_template_id=request.template_id,
                generation_type=request.generation_type,
                software_engineering_chapter=request.software_engineering_chapter,
                ideological_theme=request.ideological_theme,
                token_count=int(token_count),
                generation_time=generation_time,
                user_id=user_id
            )

            history = await GenerationHistoryModel.create(**history_data.dict())

            return AIGCGenerationResponse(
                content=content,
                generation_id=history.id,
                token_count=int(token_count),
                generation_time=generation_time
            )

        except Exception as e:
            raise HTTPException(status_code=502, detail=f"生成失败: {str(e)}")

    async def generate_stream_with_template(
        self,
        request: AIGCGenerationRequest,
        user_id: int
    ):
        """流式生成内容"""
        start_time = time.time()
        token_count = 0

        try:
            # 如果使用了模板，先渲染模板
            if request.template_id and request.template_variables:
                template = await PromptTemplateModel.get_or_none(
                    id=request.template_id,
                    is_active=True
                )
                if not template:
                    raise HTTPException(status_code=404, detail="模板不存在或已禁用")

                # 渲染模板
                prompt = template.template_content
                for var, value in request.template_variables.items():
                    placeholder = f"{{{{{var}}}}}"
                    prompt = prompt.replace(placeholder, str(value))

                # 增加模板使用次数
                await template.update_from_dict({
                    "usage_count": template.usage_count + 1
                })
                await template.save()
            else:
                prompt = request.prompt

            # 构建系统提示词
            system_prompt = self._build_system_prompt(
                request.generation_type,
                request.software_engineering_chapter,
                request.ideological_theme
            )

            # 构建消息数组
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]

            # 用于收集完整内容
            full_content = []

            async def event_generator():
                nonlocal token_count
                try:
                    async for chunk in self.client.chat_stream(messages):
                        # 处理chunk内容
                        chunk_content = self._extract_content_from_chunk(chunk)
                        if chunk_content:
                            full_content.append(chunk_content)
                            yield f"data: {json.dumps({'content': chunk_content})}\n\n"

                    # 生成完成后，保存历史记录
                    complete_content = ''.join(full_content)
                    generation_time = int((time.time() - start_time) * 1000)
                    token_count = len(complete_content.split()) * 1.3  # 估算

                    history_data = GenerationHistoryCreate(
                        user_input=prompt,
                        generated_content=complete_content,
                        prompt_template_id=request.template_id,
                        generation_type=request.generation_type,
                        software_engineering_chapter=request.software_engineering_chapter,
                        ideological_theme=request.ideological_theme,
                        token_count=int(token_count),
                        generation_time=generation_time,
                        user_id=user_id
                    )

                    history = await GenerationHistoryModel.create(**history_data.dict())
                    # 发送完成信号
                    yield f"data: {json.dumps({'type': 'complete', 'generation_id': history.id})}\n\n"

                except Exception as e:
                    yield f"event: error\ndata: {str(e)}\n\n"

            return StreamingResponse(event_generator(), media_type='text/event-stream')

        except Exception as e:
            raise HTTPException(status_code=502, detail=f"流式生成失败: {str(e)}")

    def _build_system_prompt(
        self,
        generation_type: str,
        software_engineering_chapter: Optional[str],
        ideological_theme: Optional[str]
    ) -> str:
        """构建系统提示词，增强思政教育效果"""

        base_prompt = """你是一位专业的软件工程课程思政教育专家，擅长将软件工程知识与思政教育理念有机结合。

你的任务是：
1. 生成高质量的课程思政教学内容
2. 确保技术知识与思政元素的有机融合
3. 提供具有教育意义和实用价值的内容
4. 语言表达准确、生动，适合课堂教学使用

请确保生成的内容：
- 符合教育教学规律
- 具有正确的价值导向
- 体现工匠精神、创新精神、责任担当等思政元素
- 与软件工程专业知识紧密结合
- 具有启发性和引导性"""

        if generation_type == "case":
            base_prompt += """

对于案例生成，请包含以下要素：
1. 案例背景：描述真实的软件工程场景
2. 思政元素：融入职业道德、工匠精神等
3. 技术知识点：结合软件工程具体技术
4. 讨论思考：提出引导学生思考的问题
5. 教学建议：提供教学使用建议"""
        elif generation_type == "discussion":
            base_prompt += """

对于讨论题生成，请：
1. 结合软件工程实际场景
2. 体现职业伦理和价值判断
3. 设计具有思辨性的问题
4. 提供多角度思考方向
5. 引导学生深入探讨"""
        elif generation_type == "thinking":
            base_prompt += """

对于思考题生成，请：
1. 聚具体的技术或管理问题
2. 融入职业精神和社会责任
3. 培养批判性思维
4. 引导创新意识
5. 强调团队协作精神"""

        if software_engineering_chapter:
            base_prompt += f"\n\n当前章节：{software_engineering_chapter}"

        if ideological_theme:
            base_prompt += f"\n\n思政主题：{ideological_theme}"

        return base_prompt

    def _extract_content_from_chunk(self, chunk: str) -> str:
        """从流式响应中提取内容"""
        try:
            import json
            data = json.loads(chunk)
            if data.get("choices"):
                for choice in data["choices"]:
                    if choice.get("delta"):
                        content = choice["delta"].get("content", "")
                        if content:
                            return content
            return ""
        except:
            return ""

aigc_service = EnhancedAIGCService()

@router.post("/generate", summary="智能生成课程思政内容")
async def generate_content(
    request: AIGCGenerationRequest,
    current_user: User = Depends(AuthControl.is_authed)
):
    if request.use_stream:
        return await aigc_service.generate_stream_with_template(request, current_user.id)
    else:
        return await aigc_service.generate_with_template(request, current_user.id)

@router.get("/history", summary="获取生成历史")
async def get_generation_history(
    page: int = 1,
    page_size: int = 20,
    generation_type: str = None,
    current_user: User = Depends(AuthControl.is_authed)
):
    query = GenerationHistoryModel.filter(user_id=current_user.id)

    if generation_type:
        query = query.filter(generation_type=generation_type)

    total = await query.count()
    items = await query.order_by("-created_at").offset(
        (page - 1) * page_size
    ).limit(page_size)

    histories = [GenerationHistoryInDB.from_orm(item) for item in items]

    return {
        "items": histories,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }

@router.post("/history/{history_id}/rate", summary="评价生成内容")
async def rate_generation_history(
    history_id: int,
    rating: int,  # 1-5分
    current_user: User = Depends(AuthControl.is_authed)
):
    history = await GenerationHistoryModel.get_or_none(
        id=history_id,
        user_id=current_user.id
    )
    if not history:
        raise HTTPException(status_code=404, detail="生成记录不存在")

    await history.update_from_dict({
        "user_rating": rating,
        "user_feedback": f"用户评分: {rating}分"
    })
    await history.save()

    return {"message": "评分成功"}

@router.post("/history/{history_id}/save-as-case", summary="将生成内容保存为案例")
async def save_as_case(
    history_id: int,
    case_data: dict,
    current_user: User = Depends(AuthControl.is_authed)
):
    # 检查生成历史
    history = await GenerationHistoryModel.get_or_none(
        id=history_id,
        user_id=current_user.id
    )
    if not history:
        raise HTTPException(status_code=404, detail="生成记录不存在")

    # 创建案例
    from app.schemas.ideological import IdeologicalCaseCreate
    case_data["content"] = history.generated_content
    case_data["software_engineering_chapter"] = case_data.get(
        "software_engineering_chapter",
        history.software_engineering_chapter or ""
    )
    case_data["ideological_theme"] = case_data.get(
        "ideological_theme",
        history.ideological_theme or ""
    )

    case_in = IdeologicalCaseCreate(**case_data)
    case = await IdeologicalCaseModel.create(
        **case_in.dict(),
        author_id=current_user.id
    )

    # 更新历史记录
    await history.update_from_dict({
        "is_saved_to_case": True,
        "case_id": case.id
    })
    await history.save()

    return {"message": "保存成功", "case_id": case.id}