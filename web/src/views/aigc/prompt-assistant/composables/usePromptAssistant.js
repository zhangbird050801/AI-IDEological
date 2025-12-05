/**
 * 提示词助手组合式函数
 * 封装提示词助手的核心逻辑
 */
import { ref, computed } from 'vue'
import { useMessage } from 'naive-ui'
import { promptAssistantApi } from '@/api/ideological'

export function usePromptAssistant() {
  const message = useMessage()
  
  const isLoading = ref(false)
  const currentSessionId = ref('')
  const currentStage = ref('准备开始')
  const isCompleted = ref(false)
  const messages = ref([])

  // 阶段标签映射
  const stageLabels = {
    'greeting': '问候阶段',
    'requirement_gathering': '需求收集中',
    'clarification': '澄清需求中',
    'drafting': '草稿生成中',
    'refinement': '优化中',
    'finalization': '已完成',
    'completed': '已完成'
  }

  /**
   * 发送消息到提示词助手
   */
  const sendMessage = async (userMessage) => {
    if (!userMessage.trim() || isLoading.value) return false

    // 添加用户消息到界面
    messages.value.push({
      type: 'user',
      content: userMessage.trim(),
      timestamp: new Date()
    })

    isLoading.value = true

    try {
      // 调用后端提示词助手API
      const response = await promptAssistantApi.chat({
        message: userMessage.trim(),
        session_id: currentSessionId.value || null
      })

      // 更新会话ID
      if (!currentSessionId.value && response.session_id) {
        currentSessionId.value = response.session_id
      }

      // 更新当前阶段
      if (response.session_stage) {
        currentStage.value = stageLabels[response.session_stage] || '进行中'
      }

      // 构建助手消息
      const assistantMessage = {
        type: 'assistant',
        content: response.assistant_message || '',
        timestamp: new Date(),
        isStreaming: false
      }

      // 如果有建议的提示词
      if (response.suggested_prompt) {
        assistantMessage.suggestedPrompt = response.suggested_prompt
      }

      // 如果有最终提示词
      if (response.final_prompt) {
        assistantMessage.finalPrompt = response.final_prompt
        isCompleted.value = true
        currentStage.value = '可以继续优化'
      }

      // 添加助手消息到界面
      messages.value.push(assistantMessage)

      return true
    } catch (error) {
      console.error('发送消息失败:', error)
      message.error('发送消息失败，请重试')

      // 添加错误消息
      messages.value.push({
        type: 'assistant',
        content: '抱歉，我遇到了一些问题。请稍后再试。',
        timestamp: new Date()
      })

      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 开始新会话
   */
  const startNewSession = () => {
    messages.value = []
    currentSessionId.value = ''
    currentStage.value = '准备开始'
    isCompleted.value = false
    localStorage.removeItem('prompt-assistant-messages')
    localStorage.removeItem('prompt-assistant-session-id')
  }

  /**
   * 从localStorage恢复会话
   */
  const restoreSession = () => {
    const savedMessages = localStorage.getItem('prompt-assistant-messages')
    const savedSessionId = localStorage.getItem('prompt-assistant-session-id')

    if (savedMessages) {
      try {
        messages.value = JSON.parse(savedMessages)
        if (messages.value.length > 0) {
          message.info('已恢复上次的对话')
          
          // 检查是否已完成
          const lastMessage = messages.value[messages.value.length - 1]
          if (lastMessage.finalPrompt) {
            isCompleted.value = true
            currentStage.value = '可以继续优化'
          }
        }
      } catch (e) {
        console.warn('Failed to load saved messages:', e)
      }
    }

    if (savedSessionId) {
      currentSessionId.value = savedSessionId
    }
  }

  /**
   * 保存会话到localStorage
   */
  const saveSession = () => {
    if (messages.value.length > 0) {
      localStorage.setItem('prompt-assistant-messages', JSON.stringify(messages.value))
    }
    if (currentSessionId.value) {
      localStorage.setItem('prompt-assistant-session-id', currentSessionId.value)
    }
  }

  /**
   * 智能分析提示词内容
   */
  const analyzePromptContent = (content) => {
    const analysis = {
      suggestedName: '',
      suggestedDescription: '',
      suggestedType: null,
      suggestedCategory: null,
      keywords: []
    }

    // 从对话历史中提取用户需求
    const userRequests = messages.value
      .filter(m => m.type === 'user')
      .map(m => m.content)
      .join(' ')

    // 关键词检测
    const keywordMap = {
      '写作': ['写', '创作', '编写', '文章', '内容', '写作'],
      '编程': ['代码', '程序', '编程', '开发', 'code', 'programming'],
      '分析': ['分析', '总结', '评估', '研究', 'analyze'],
      '创意': ['创意', '想象', '故事', '设计', 'creative'],
      '教学': ['教学', '课程', '学习', '教育', 'teaching'],
      '思政': ['思政', '价值观', '道德', '伦理', '思想政治']
    }

    for (const [category, words] of Object.entries(keywordMap)) {
      if (words.some(word => userRequests.includes(word) || content.includes(word))) {
        analysis.keywords.push(category)
      }
    }

    // 生成建议的名称
    const keywordStr = analysis.keywords.length > 0 ? analysis.keywords.join('_') : '通用'
    const date = new Date().toLocaleDateString('zh-CN').replace(/\//g, '-')
    analysis.suggestedName = `${keywordStr}提示词模板_${date}`

    // 生成建议的描述
    analysis.suggestedDescription = `通过AI助手生成的${keywordStr}相关提示词模板，适用于${analysis.keywords.join('、')}等场景。`

    // 智能选择模板类型和分类
    if (analysis.keywords.includes('教学')) {
      analysis.suggestedType = 'teaching_design'
      analysis.suggestedCategory = '教学方法'
    } else if (analysis.keywords.includes('写作')) {
      analysis.suggestedType = 'content_optimization'
      analysis.suggestedCategory = '内容优化'
    } else if (analysis.keywords.includes('编程')) {
      analysis.suggestedType = 'practice'
      analysis.suggestedCategory = '实践指导'
    } else if (analysis.keywords.includes('分析')) {
      analysis.suggestedType = 'knowledge_point'
      analysis.suggestedCategory = '知识点讲解'
    } else if (analysis.keywords.includes('思政')) {
      analysis.suggestedType = 'case_generation'
      analysis.suggestedCategory = '思政案例'
    } else {
      analysis.suggestedType = 'case_generation'
      analysis.suggestedCategory = '思政案例'
    }

    return analysis
  }

  return {
    // 状态
    isLoading,
    currentSessionId,
    currentStage,
    isCompleted,
    messages,
    
    // 方法
    sendMessage,
    startNewSession,
    restoreSession,
    saveSession,
    analyzePromptContent,
  }
}
