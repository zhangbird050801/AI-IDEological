"""提示词助手工具函数"""
import re
from typing import Dict, Any, Tuple, List, Optional
from app.models.enums import PromptAssistantSession


def extract_requirements(
    user_message: str, 
    conversation_history: List = None
) -> Dict[str, Any]:
    """从用户消息中提取需求信息"""
    requirements = {
        'task_type': None,
        'content_type': None,
        'style': None,
        'length': None,
        'audience': None,
        'format': None,
        'key_elements': [],
        'constraints': [],
    }

    # 任务类型识别
    task_keywords = {
        'writing': ['写', '创作', '编写', '写作', '生成', 'write', 'create'],
        'analysis': ['分析', '总结', 'summarize', 'analyze'],
        'coding': ['编程', '代码', '程序', 'code', 'programming'],
        'creative': ['创意', '想象', 'creative', 'imaginative'],
        'explanation': ['解释', '说明', '讲解', 'explain', 'describe'],
        'teaching': ['教学', '课程', '教育', 'teaching', 'education'],
    }

    for task_type, keywords in task_keywords.items():
        if any(keyword in user_message.lower() for keyword in keywords):
            requirements['task_type'] = task_type
            break

    # 风格识别
    if any(word in user_message for word in ['正式', '专业', 'professional', 'formal']):
        requirements['style'] = '正式'
    elif any(word in user_message for word in ['随意', '友好', 'casual', 'friendly']):
        requirements['style'] = '随意'

    # 长度识别
    if any(word in user_message for word in ['短', '简短', 'short', 'brief']):
        requirements['length'] = '简短'
    elif any(word in user_message for word in ['长', '详细', 'detailed', 'comprehensive']):
        requirements['length'] = '详细'

    return requirements


def extract_prompt_from_response(
    assistant_message: str,
    user_message: str,
    conversation_history: List = None
) -> Tuple[Optional[str], Optional[str], PromptAssistantSession]:
    """
    从AI回复中智能提取提示词
    
    Returns:
        (suggested_prompt, final_prompt, next_stage)
    """
    suggested_prompt = None
    final_prompt = None
    next_stage = PromptAssistantSession.REQUIREMENT_GATHERING
    
    # 提取代码块中的提示词
    code_blocks = re.findall(
        r'```(?:prompt|提示词)?\s*([\s\S]*?)```', 
        assistant_message, 
        re.IGNORECASE
    )
    
    if code_blocks:
        suggested_prompt = code_blocks[0].strip()
        next_stage = PromptAssistantSession.DRAFTING
        
        # 检查用户是否表示满意
        satisfaction_keywords = [
            '满意', '可以', '好的', '不错', '很好', '完美',
            'ok', 'good', 'great', 'perfect', 'yes'
        ]
        
        if any(word in user_message.lower() for word in satisfaction_keywords):
            final_prompt = suggested_prompt
            next_stage = PromptAssistantSession.FINALIZATION
    
    return suggested_prompt, final_prompt, next_stage


def format_prompt_for_display(prompt: str) -> str:
    """格式化提示词用于显示"""
    if not prompt:
        return ""
    
    # 移除多余的空行
    lines = [line for line in prompt.split('\n') if line.strip()]
    return '\n'.join(lines)


def validate_prompt(prompt: str) -> Tuple[bool, str]:
    """
    验证提示词的质量
    
    Returns:
        (is_valid, message)
    """
    if not prompt or len(prompt.strip()) < 10:
        return False, "提示词太短，至少需要10个字符"
    
    if len(prompt) > 5000:
        return False, "提示词太长，建议不超过5000个字符"
    
    # 检查是否包含基本的指令性语言
    instruction_keywords = [
        '你是', '请', '帮我', '生成', '创建', '写', '分析',
        'you are', 'please', 'help', 'generate', 'create', 'write'
    ]
    
    has_instruction = any(keyword in prompt.lower() for keyword in instruction_keywords)
    if not has_instruction:
        return False, "提示词应该包含明确的指令"
    
    return True, "提示词格式正确"
