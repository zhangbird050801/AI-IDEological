<template>
  <AppPage>
    <div class="prompt-assistant-page">
      <!-- 页面头部 -->
      <n-card class="page-header" :bordered="false">
        <div class="header-content">
          <div class="title-section">
            <h1>提示词助手</h1>
          </div>
          <div class="actions-section">
            <n-space>
              <n-button @click="goBackToTemplates" v-if="fromTemplatePage" text>
                <template #icon>
                  <n-icon><Icon icon="mdi:arrow-left" /></n-icon>
                </template>
                返回模板库
              </n-button>
              <n-button @click="startNewSession" type="primary">
                <template #icon>
                  <n-icon><Icon icon="mdi:refresh" /></n-icon>
                </template>
                清空对话
              </n-button>
            </n-space>
          </div>
        </div>
      </n-card>

      <!-- 主内容区 -->
      <n-grid :cols="1" :x-gap="16" class="main-content">
        <!-- 聊天界面 -->
        <n-grid-item :span="24">
          <n-card class="chat-container" :bordered="false">
            <template #header>
              <div class="chat-header">
                <div class="assistant-info">
                  <n-avatar round :size="40" class="assistant-avatar">
                    <n-icon size="24"><Icon icon="mdi:robot" /></n-icon>
                  </n-avatar>
                  <div class="assistant-details">
                    <h3>PromptSmith</h3>
                    <p class="status-text">{{ currentStage }} {{ isCompleted ? '(已完成)' : '' }}</p>
                  </div>
                </div>
                <div class="chat-actions">
                  <n-button text @click="clearChat">
                    <template #icon>
                      <n-icon><Icon icon="mdi:clear" /></n-icon>
                    </template>
                  </n-button>
                </div>
              </div>
            </template>

            <!-- 消息列表 -->
            <div class="messages-container" ref="messagesContainer">
              <div v-if="messages.length === 0" class="welcome-message">
                <div class="welcome-content">
                  <n-icon size="48" color="#7c3aed">
                    <Icon icon="mdi:message" />
                  </n-icon>
                  <h3>欢迎使用提示词助手</h3>
                  <p>告诉我你想要制作什么类型的提示词，我会帮你生成高质量的提示词模板</p>
                  <div class="quick-start-buttons">
                    <n-space wrap>
                      <n-button
                        v-for="example in quickStartExamples"
                        :key="example.title"
                        @click="sendQuickStart(example.message)"
                        dashed
                      >
                        {{ example.title }}
                      </n-button>
                    </n-space>
                  </div>
                </div>
              </div>

              <div v-else class="messages-list">
                <div
                  v-for="(message, index) in messages"
                  :key="index"
                  class="message-item"
                  :class="{ 'user-message': message.type === 'user', 'assistant-message': message.type === 'assistant' }"
                >
                  <div class="message-avatar">
                    <n-avatar round :size="32" v-if="message.type === 'user'">
                      <n-icon><Icon icon="mdi:account" /></n-icon>
                    </n-avatar>
                    <n-avatar round :size="32" v-else class="assistant-avatar">
                      <n-icon><Icon icon="mdi:robot" /></n-icon>
                    </n-avatar>
                  </div>
                  <div class="message-content">
                    <div class="message-text" v-html="formatMessage(message.content)"></div>

                    <!-- 流式加载指示器 -->
                    <div class="typing-indicator" v-if="message.isStreaming">
                      <n-space>
                        <n-spin size="small" />
                        <span>正在输入...</span>
                      </n-space>
                    </div>

                    <div class="message-time">{{ formatTime(message.timestamp) }}</div>

                    <!-- 提示词建议卡片 -->
                    <div v-if="message.suggestedPrompt" class="prompt-suggestion-card">
                      <n-card title="建议的提示词" size="small" :bordered="false">
                        <template #header-extra>
                          <n-space>
                            <n-button size="small" @click="copyPrompt(message.suggestedPrompt)">
                              <template #icon>
                                <n-icon><Icon icon="mdi:content-copy" /></n-icon>
                              </template>
                              复制
                            </n-button>
                            <n-button size="small" type="primary" @click="acceptPrompt(message.suggestedPrompt)">
                              <template #icon>
                                <n-icon><Icon icon="mdi:check" /></n-icon>
                              </template>
                              接受
                            </n-button>
                          </n-space>
                        </template>
                        <n-code :code="message.suggestedPrompt" language="text" :line-height="1.6" />
                      </n-card>
                    </div>

                    <!-- 最终提示词 -->
                    <div v-if="message.finalPrompt" class="final-prompt-card">
                      <n-card title="🎉 最终提示词" size="small" type="success" :bordered="false">
                        <template #header-extra>
                          <n-space>
                            <n-button size="small" @click="copyPrompt(message.finalPrompt)">
                              <template #icon>
                                <n-icon><Icon icon="mdi:content-copy" /></n-icon>
                              </template>
                              复制
                            </n-button>
                            <n-button size="small" type="warning" @click="saveAsTemplate(message.finalPrompt)">
                              <template #icon>
                                <n-icon><Icon icon="mdi:content-save" /></n-icon>
                              </template>
                              💾 保存到模板库
                            </n-button>
                            <n-button size="small" type="primary" @click="usePromptInChat(message.finalPrompt)">
                              <template #icon>
                                <n-icon><Icon icon="mdi:play" /></n-icon>
                              </template>
                              在聊天中使用
                            </n-button>
                          </n-space>
                        </template>
                        <n-code :code="message.finalPrompt" language="text" :line-height="1.6" />

                        <!-- 添加快速保存提示 -->
                        <div class="save-hint">
                          <n-alert type="info" size="small" :closable="false">
                            <template #icon>
                              <n-icon><Icon icon="mdi:lightbulb" /></n-icon>
                            </template>
                            💡 提示：点击"保存到模板库"可以将这个提示词保存到你的个人模板库中，方便以后使用！
                          </n-alert>
                        </div>
                      </n-card>
                    </div>
                  </div>
                </div>

                </div>
            </div>

            <!-- 输入区域 -->
            <div class="input-container">
              <n-space vertical>
                <n-input
                  v-model:value="inputMessage"
                  type="textarea"
                  placeholder="请输入你的需求..."
                  :autosize="{ minRows: 2, maxRows: 6 }"
                  @keydown.enter.prevent="sendMessage"
                  :loading="isLoading"
                />
                <n-space justify="space-between">
                  <n-space>
                    <n-button text @click="showTemplates" size="small">
                      <template #icon>
                        <n-icon><Icon icon="mdi:apps" /></n-icon>
                      </template>
                      模板库
                    </n-button>
                    <n-button text @click="showTips" size="small">
                      <template #icon>
                        <n-icon><Icon icon="mdi:lightbulb" /></n-icon>
                      </template>
                      使用技巧
                    </n-button>
                  </n-space>
                  <n-button
                    type="primary"
                    @click="sendMessage"
                    :disabled="!inputMessage.trim() || isLoading"
                    :loading="isLoading"
                  >
                    发送
                  </n-button>
                </n-space>
              </n-space>
            </div>
          </n-card>
        </n-grid-item>

        </n-grid>
    </div>

  
    <!-- 模板选择弹窗 -->
    <n-modal
      v-model:show="templatesVisible"
      preset="dialog"
      title="选择模板"
      style="width: 800px"
    >
      <div class="templates-grid">
        <n-grid :cols="2" :x-gap="16">
          <n-grid-item v-for="template in templates" :key="template.id">
            <n-card
              class="template-card"
              hoverable
              @click="selectTemplate(template)"
            >
              <template #header>
                {{ template.name }}
              </template>
              <p>{{ template.description }}</p>
              <div class="template-meta">
                <n-space size="small">
                  <n-tag size="small">{{ template.template_type }}</n-tag>
                  <n-tag size="small">使用 {{ template.usage_count }} 次</n-tag>
                </n-space>
              </div>
            </n-card>
          </n-grid-item>
        </n-grid>
      </div>
    </n-modal>

    <!-- 保存为模板弹窗 -->
    <n-modal
      v-model:show="saveTemplateVisible"
      :mask-closable="false"
      preset="dialog"
      style="width: 700px"
      title="保存为提示词模板"
    >
      <n-form
        ref="templateFormRef"
        :model="templateForm"
        :rules="templateFormRules"
        label-placement="left"
        :label-width="100"
        require-mark-placement="right-hanging"
      >
        <n-form-item label="模板名称" path="name">
          <n-input
            v-model:value="templateForm.name"
            placeholder="请输入模板名称"
            maxlength="100"
            show-count
          />
        </n-form-item>

        <n-form-item label="模板描述" path="description">
          <n-input
            v-model:value="templateForm.description"
            type="textarea"
            placeholder="请输入模板描述"
            :autosize="{ minRows: 2, maxRows: 4 }"
            maxlength="500"
            show-count
          />
        </n-form-item>

        <n-form-item label="模板类型" path="template_type">
          <n-select
            v-model:value="templateForm.template_type"
            placeholder="选择模板类型"
            :options="templateTypeOptions"
          />
        </n-form-item>

        <n-form-item label="分类" path="category">
          <n-select
            v-model:value="templateForm.category"
            placeholder="选择分类"
            :options="categoryOptions"
            filterable
            tag
          />
        </n-form-item>

        <n-grid :cols="2" :x-gap="16">
          <n-form-item-grid-item label="软件工程章节" path="software_engineering_chapter">
            <n-select
              v-model:value="templateForm.software_engineering_chapter"
              placeholder="选择章节（可选）"
              :options="chapterOptions"
              clearable
            />
          </n-form-item-grid-item>

          <n-form-item-grid-item label="思政主题" path="ideological_theme">
            <n-select
              v-model:value="templateForm.ideological_theme"
              placeholder="选择主题（可选）"
              :options="themeOptions"
              clearable
            />
          </n-form-item-grid-item>
        </n-grid>

        <n-form-item label="模板内容" path="template_content">
          <n-input
            v-model:value="templateForm.template_content"
            type="textarea"
            placeholder="模板内容将自动填入"
            :autosize="{ minRows: 6, maxRows: 12 }"
            maxlength="5000"
            show-count
          />
          <template #feedback>
            <n-text depth="3" style="font-size: 12px">
              模板内容由AI生成，您可以直接保存或进行修改
            </n-text>
          </template>
        </n-form-item>

        <n-form-item label="提取的变量">
          <n-space>
            <n-tag
              v-for="variable in extractedVariables"
              :key="variable"
              type="info"
              size="small"
            >
              {{ '{' + '{' + variable + '}' + '}' }}
            </n-tag>
            <n-text v-if="extractedVariables.length === 0" depth="3" style="font-size: 12px">
              未检测到变量
            </n-text>
          </n-space>
        </n-form-item>
      </n-form>

      <template #action>
        <n-space>
          <n-button @click="saveTemplateVisible = false">取消</n-button>
          <n-button type="primary" @click="handleSaveTemplate" :loading="saveLoading">
            保存模板
          </n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 使用技巧弹窗 -->
    <n-modal
      v-model:show="tipsVisible"
      preset="dialog"
      title="使用技巧"
      style="width: 600px"
    >
      <n-space vertical size="large">
        <div>
          <h4>💡 如何获得更好的提示词</h4>
          <ul>
            <li>尽可能详细地描述你的需求和期望</li>
            <li>明确指定输出格式和风格要求</li>
            <li>提供具体的示例或参考</li>
            <li>说明目标受众和使用场景</li>
          </ul>
        </div>

        <div>
          <h4>🎯 不同任务的提示词特点</h4>
          <ul>
            <li><strong>写作任务：</strong>注重风格、语调、结构要求</li>
            <li><strong>分析任务：</strong>强调分析维度、标准、深度</li>
            <li><strong>编程任务：</strong>明确技术栈、功能需求、边界条件</li>
            <li><strong>创意任务：</strong>提供灵感来源、创新方向、约束条件</li>
          </ul>
        </div>

        <div>
          <h4>⚡ 快速开始建议</h4>
          <ul>
            <li>从简单需求开始，逐步完善</li>
            <li>多利用助手提出的澄清问题</li>
            <li>不要害怕多次修改和优化</li>
            <li>保存满意的提示词模板供以后使用</li>
          </ul>
        </div>
      </n-space>
    </n-modal>
  </AppPage>
</template>

<script>
export default {
  name: 'AIGCPromptAssistant'
}
</script>

<script setup>
import { ref, reactive, onMounted, nextTick, computed } from 'vue'
import {
  NCard,
  NButton,
  NIcon,
  NSpace,
  NAvatar,
  NInput,
  NGrid,
  NGridItem,
  NTag,
  NCode,
  NModal,
  NDescriptions,
  NDescriptionsItem,
  NEmpty,
  NDropdown,
  NStatistic,
  NSpin,
  NForm,
  NFormItem,
  NSelect,
  NText,
  NAlert,
  useMessage,
  useDialog,
} from 'naive-ui'
import { Icon } from '@iconify/vue'
import AppPage from '@/components/page/AppPage.vue'
import { request } from '@/utils/http'
import { chatStream } from '@/api/aigc'

// 响应式数据
const message = useMessage()
const dialog = useDialog()

const isLoading = ref(false)
const inputMessage = ref('')
const messages = ref([])
const currentSessionId = ref('')
const currentStage = ref('准备开始')
const isCompleted = ref(false)
const messagesContainer = ref(null)
const fromTemplatePage = ref(false)

const templates = ref([])
const templatesVisible = ref(false)
const tipsVisible = ref(false)

// 保存模板相关
const saveTemplateVisible = ref(false)
const saveLoading = ref(false)
const templateFormRef = ref()
const templateForm = reactive({
  name: '',
  description: '',
  template_type: null,
  template_content: '',
  variables: [],
  category: null,
  software_engineering_chapter: null,
  ideological_theme: null,
})

// 模板选项
const templateTypeOptions = ref([])
const categoryOptions = ref([])
const chapterOptions = ref([])
const themeOptions = ref([])

// 表单验证规则
const templateFormRules = {
  name: [
    { required: true, message: '请输入模板名称', trigger: 'blur' },
    { max: 100, message: '名称长度不能超过100个字符', trigger: 'blur' },
  ],
  description: [
    { required: true, message: '请输入模板描述', trigger: 'blur' },
    { max: 500, message: '描述长度不能超过500个字符', trigger: 'blur' },
  ],
  template_type: [
    { required: true, message: '请选择模板类型', trigger: 'change' },
  ],
  template_content: [
    { required: true, message: '请输入模板内容', trigger: 'blur' },
  ],
  category: [
    { required: true, message: '请选择分类', trigger: 'change' },
  ],
}

// 提取的变量
const extractedVariables = computed(() => {
  const matches = templateForm.template_content.match(/\{\{(\w+)\}\}/g)
  if (!matches) return []
  return [...new Set(matches.map(match => match.slice(2, -2)))]
})

// 快速开始示例
const quickStartExamples = ref([
  {
    title: '写作助手',
    message: '帮我制作一个写作助手的提示词，可以帮我写各种类型的文章'
  },
  {
    title: '代码审查',
    message: '我需要一个提示词来帮助审查代码，找出潜在问题和改进建议'
  },
  {
    title: '学习计划',
    message: '制作一个个性化的学习计划生成提示词，考虑学习目标和时间安排'
  },
  {
    title: '创意故事',
    message: '帮我制作一个创意故事生成的提示词，能够根据主题生成有趣的故事'
  }
])

// 方法
const sendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return

  const userMessage = inputMessage.value.trim()
  inputMessage.value = ''

  // 添加用户消息
  messages.value.push({
    type: 'user',
    content: userMessage,
    timestamp: new Date()
  })

  isLoading.value = true
  await scrollToBottom()

  try {
    // 构建对话历史（用于保持上下文）
    let conversationHistory = ''
    const prevMessages = messages.value.slice(0, -1) // 排除当前正在处理的用户消息
    if (prevMessages.length > 0) {
      const conversationText = prevMessages.map(m => {
        const role = m.type === 'user' ? '用户' : '助手'
        return `${role}: ${m.content}`
      }).join('\n\n')
      conversationHistory = `之前的对话历史：\n${conversationText}\n\n`
    }

    // 构建提示词助手的系统提示
    const systemPrompt = `你是 **PromptSmith**，一个专业的AI提示词制作助手。你的任务是帮助用户为其他大型语言模型(LLM)制作高质量的提示词模板。

你的工作流程：
1. 理解用户的需求和目标
2. 如果需要更多信息，通过提问来澄清
3. 应用提示词工程最佳实践（清晰性、上下文、明确指令、变量、示例等）
4. 生成结构良好的提示词模板
5. 用户可以对生成的提示词提出修改建议，你需要根据反馈进行优化

提示词模板应该：
- 清晰明确地说明任务要求
- 提供必要的上下文信息
- 定义输出格式和风格
- 使用变量化设计（如：{{变量名}}）
- 包含具体的约束和指导原则

重要说明：
- 这是一个持续对话过程，用户可以多次修改和完善提示词
- 每次用户提供反馈后，都要基于之前的讨论继续优化
- 即使已经生成了提示词模板，对话也可以继续

${conversationHistory}现在请帮助用户：${userMessage}

请直接与用户对话，询问需要的信息并最终提供一个完整的提示词模板。如果用户满意生成的提示词，请用 \`\`\`代码块包裹最终的提示词模板。记住，这只是一个开始，用户可以继续提出修改要求。`

    // 添加助手占位消息（用于流式显示）
    const assistantMessage = reactive({
      type: 'assistant',
      content: '',
      timestamp: new Date(),
      isStreaming: true
    })
    messages.value.push(assistantMessage)

    // 使用AIGC流式聊天 - 构建完整的对话历史
    const conversationMessages = []
    messages.value.slice(0, -1).forEach(msg => {
      if (msg.type === 'user') {
        conversationMessages.push({ role: 'user', content: msg.content })
      } else if (msg.type === 'assistant' && msg.content) {
        conversationMessages.push({ role: 'assistant', content: msg.content })
      }
    })

    const messagesForAI = [
      { role: 'system', content: systemPrompt },
      ...conversationMessages
    ]

    const iterator = chatStream(messagesForAI)
    let fullResponse = ''

    for await (const item of iterator) {
      let textToAppend = ''
      try {
        if (item && item.type === 'chunk' && item.payload) {
          const obj = item.payload
          if (obj.choices && Array.isArray(obj.choices)) {
            for (const c of obj.choices) {
              if (c && c.delta) {
                if (typeof c.delta.content === 'string' && c.delta.content.length > 0) {
                  textToAppend += c.delta.content
                }
              }
            }
          } else if (typeof obj.data === 'string') {
            textToAppend += obj.data
          }
        } else if (item && item.type === 'text') {
          textToAppend += String(item.payload)
        }
      } catch (e) {
        textToAppend = String(item)
      }

      if (textToAppend) {
        assistantMessage.content += textToAppend
        fullResponse += textToAppend
        await scrollToBottom()
      }
    }

    // 标记流式传输结束
    assistantMessage.isStreaming = false

    // 检查是否包含提示词内容（支持多种格式）
    const promptPatterns = [
      /```(?:prompt|提示词)?\s*([\s\S]*?)```/i,
      /(?:最终提示词|提示词模板)[:：]\s*([\s\S]*?)(?=\n\n|$)/i,
      /提示词：\s*([\s\S]*?)(?=\n\n|$)/i,
    ]

    let foundPrompt = null
    for (const pattern of promptPatterns) {
      const match = fullResponse.match(pattern)
      if (match && match[1]) {
        foundPrompt = match[1].trim()
        break
      }
    }

    // 如果没有找到明确的提示词，检查是否包含变量语法
    if (!foundPrompt && fullResponse.includes('{{')) {
      // 尝试提取包含变量的段落
      const variableSections = fullResponse.split('\n').filter(line => line.includes('{{'))
      if (variableSections.length > 0) {
        foundPrompt = variableSections.join('\n').trim()
      }
    }

    if (foundPrompt) {
      assistantMessage.suggestedPrompt = foundPrompt
      // 也添加为最终提示词
      assistantMessage.finalPrompt = foundPrompt
    }

    // 更新会话状态 - 标记为有结果，但不阻止继续对话
    if (assistantMessage.suggestedPrompt) {
      isCompleted.value = true
      currentStage.value = '可以继续优化'
    }

    await scrollToBottom()

  } catch (error) {
    console.error('发送消息失败:', error)
    message.error('发送消息失败，请重试')

    // 移除流式消息并显示错误
    messages.value.pop()
    messages.value.push({
      type: 'assistant',
      content: '抱歉，我遇到了一些问题。请稍后再试。',
      timestamp: new Date()
    })
  } finally {
    isLoading.value = false
  }
}

const sendQuickStart = async (quickMessage) => {
  inputMessage.value = quickMessage
  await sendMessage()
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    // 添加一点偏移量，确保最新消息不被输入框遮挡
    const scrollHeight = messagesContainer.value.scrollHeight
    const clientHeight = messagesContainer.value.clientHeight
    const scrollTop = messagesContainer.value.scrollTop

    // 如果用户不在滚动到底部，或者有新消息，则自动滚动
    if (scrollTop + clientHeight >= scrollHeight - 100 || scrollTop === 0) {
      messagesContainer.value.scrollTop = scrollHeight
    }
  }
}

const formatMessage = (content) => {
  // 检查 content 是否为 undefined 或 null
  if (!content || typeof content !== 'string') {
    return ''
  }

  // 简单的markdown格式化
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  try {
    return new Date(timestamp).toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    return ''
  }
}

const formatSessionDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}


const startNewSession = () => {
  messages.value = []
  currentSessionId.value = ''
  currentStage.value = '准备开始'
  isCompleted.value = false
  message.success('已开始新会话')
}

const clearChat = () => {
  dialog.warning({
    title: '清空聊天记录',
    content: '确定要清空当前聊天记录吗？这将不会影响历史会话。',
    positiveText: '清空',
    negativeText: '取消',
    onPositiveClick: () => {
      messages.value = []
      message.success('聊天记录已清空')
    }
  })
}


const showTemplates = async () => {
  try {
    const response = await request.get('/ideological/prompt-assistant/templates')
    templates.value = response
    templatesVisible.value = true
  } catch (error) {
    console.error('获取模板失败:', error)
    message.error('获取模板失败')
  }
}

const selectTemplate = async (template) => {
  try {
    await request.post(`/ideological/prompt-assistant/templates/${template.id}/use`)
    message.success(`已选择模板：${template.name}`)
    templatesVisible.value = false

    // 可以根据模板内容预填充一些信息
    if (template.use_case_scenario) {
      inputMessage.value = `我想制作一个${template.name}相关的提示词，用于${template.use_case_scenario}`
    }
  } catch (error) {
    console.error('使用模板失败:', error)
    message.error('使用模板失败')
  }
}

const showTips = () => {
  tipsVisible.value = true
}

const copyPrompt = async (prompt) => {
  try {
    await navigator.clipboard.writeText(prompt)
    message.success('提示词已复制到剪贴板')
  } catch (error) {
    console.error('复制失败:', error)
    message.error('复制失败')
  }
}

const acceptPrompt = async (prompt) => {
  inputMessage.value = '这个提示词很好，请帮我进一步完善并说明如何使用。'
  await sendMessage()
}

const usePromptInChat = (prompt) => {
  // 这里可以跳转到聊天页面并预填充提示词
  message.info('提示词已准备，可以在聊天中使用')
}

const saveAsTemplate = (promptContent) => {
  // 重置表单
  Object.assign(templateForm, {
    name: '',
    description: '',
    template_type: null,
    template_content: promptContent,
    variables: [],
    category: null,
    software_engineering_chapter: null,
    ideological_theme: null,
  })

  // 自动提取变量
  templateForm.variables = extractedVariables.value

  // 根据对话内容自动生成名称和描述
  const userRequests = messages.value
    .filter(m => m.type === 'user')
    .map(m => m.content)
    .join(' ')

  // 尝试从用户请求中提取关键词
  const keywords = []
  if (userRequests.includes('写作') || userRequests.includes('文章')) keywords.push('写作')
  if (userRequests.includes('代码') || userRequests.includes('编程')) keywords.push('编程')
  if (userRequests.includes('分析') || userRequests.includes('总结')) keywords.push('分析')
  if (userRequests.includes('创意') || userRequests.includes('故事')) keywords.push('创意')
  if (userRequests.includes('教学') || userRequests.includes('课程')) keywords.push('教学')

  const keywordStr = keywords.length > 0 ? keywords.join('_') : '通用'
  templateForm.name = `${keywordStr}提示词模板_${new Date().toLocaleDateString('zh-CN')}`
  templateForm.description = `通过AI生成的${keywordStr}相关提示词模板，适用于${keywords.join('、')}等场景。`

  // 根据关键词智能选择分类
  if (keywords.includes('教学')) {
    templateForm.category = '教学方法'
  } else if (keywords.includes('写作')) {
    templateForm.category = '内容优化'
  } else if (keywords.includes('编程')) {
    templateForm.category = '实践指导'
  } else if (keywords.includes('分析')) {
    templateForm.category = '知识点讲解'
  } else {
    templateForm.category = '思政案例'
  }

  saveTemplateVisible.value = true
}

const fetchTemplateOptions = async () => {
  try {
    // 获取模板类型选项
    try {
      const typesResponse = await request.get('/ideological/templates/types/list')
      templateTypeOptions.value = Array.isArray(typesResponse.data) ? typesResponse.data : (typesResponse?.data || typesResponse || [])
    } catch (error) {
      // 使用默认模板类型数据
      templateTypeOptions.value = [
        { label: "案例生成", value: "case_generation" },
        { label: "讨论题生成", value: "discussion_generation" },
        { label: "思考题生成", value: "thinking_generation" },
        { label: "内容优化", value: "content_optimization" },
        { label: "教学设计", value: "teaching_design" },
        { label: "知识点讲解", value: "knowledge_point" }
      ]
    }

    // 获取分类选项
    try {
      const categoriesResponse = await request.get('/ideological/templates/categories/list')
      const categoriesData = Array.isArray(categoriesResponse.data) ? categoriesResponse.data : (categoriesResponse?.data || categoriesResponse || [])
      categoryOptions.value = categoriesData.map(item => ({
        label: item,
        value: item,
      }))
    } catch (error) {
      // 使用默认分类数据
      categoryOptions.value = [
        "思政案例", "教学方法", "知识点讲解", "课程设计", "实践指导", "质量评价", "前沿技术", "职业素养"
      ].map(item => ({ label: item, value: item }))
    }

    // 获取章节选项
    try {
      const chaptersResponse = await request.get('/ideological/cases/chapters/list')
      const chaptersData = Array.isArray(chaptersResponse.data) ? chaptersResponse.data : (chaptersResponse?.data || chaptersResponse || [])
      chapterOptions.value = chaptersData.map(item => ({
        label: item,
        value: item,
      }))
    } catch (error) {
      // 使用默认章节数据
      chapterOptions.value = [
        "软件工程概述", "软件过程模型", "需求分析", "系统设计", "编码实现",
        "软件测试", "软件维护", "项目管理", "软件质量", "软件工程前沿"
      ].map(item => ({ label: item, value: item }))
    }

    // 获取主题选项
    try {
      const themesResponse = await request.get('/ideological/templates/themes/list')
      const themesData = Array.isArray(themesResponse.data) ? themesResponse.data : (themesResponse?.data || themesResponse || [])
      themeOptions.value = themesData.map(item => ({
        label: item,
        value: item,
      }))
    } catch (error) {
      // 使用默认主题数据
      themeOptions.value = [
        "工匠精神", "创新精神", "团队协作", "责任担当", "诚信品质",
        "法治意识", "科学精神", "人文素养", "家国情怀", "国际视野"
      ].map(item => ({ label: item, value: item }))
    }
  } catch (error) {
    message.error('获取选项数据失败')
  }
}

const handleSaveTemplate = async () => {
  try {
    await templateFormRef.value?.validate()
    saveLoading.value = true

    const templateData = { ...templateForm }
    templateData.variables = extractedVariables.value

    await request.post('/ideological/templates/', templateData)
    message.success('模板保存成功！')

    saveTemplateVisible.value = false

    // 检查是否是从模板页面跳转过来的
    if (fromTemplatePage.value) {
      localStorage.removeItem('from_template_page')
      message.success('模板已保存！即将返回模板页面...')
      setTimeout(() => {
        window.location.href = '/aigc/prompts'
      }, 2000)
    }

  } catch (error) {
    message.error('模板保存失败')
  } finally {
    saveLoading.value = false
  }
}

const goBackToTemplates = () => {
  localStorage.removeItem('from_template_page')
  window.location.href = '/aigc/prompts'
}

// 初始化
onMounted(() => {
  // 确保开发环境有认证token
  if (import.meta.env.DEV && !localStorage.getItem('access_token')) {
    localStorage.setItem('access_token', 'dev')
    console.log('🔧 开发环境：已设置认证token')
  }

  // 检查是否是从模板页面跳转过来的
  fromTemplatePage.value = localStorage.getItem('from_template_page') === 'true'

  fetchTemplateOptions()
})
</script>

<style scoped>
.prompt-assistant-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 16px;
}

.page-header {
  margin-bottom: 16px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-section h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.main-content {
  flex: 1;
  min-height: 0;
}

.chat-container {
  height: calc(100vh - 200px);
  display: flex;
  flex-direction: column;
  position: relative;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.assistant-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.assistant-details h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.status-text {
  margin: 0;
  font-size: 12px;
  opacity: 0.8;
}

.assistant-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: 2px solid #fff;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px 0;
  min-height: 0;
  margin-bottom: 0;
  scroll-behavior: smooth;
}

.welcome-message {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
}

.welcome-content {
  max-width: 500px;
}

.welcome-content h3 {
  margin: 16px 0 8px 0;
  color: var(--n-text-color);
}

.welcome-content p {
  margin: 0 0 24px 0;
  color: var(--n-text-color-depth-3);
}

.quick-start-buttons {
  margin-top: 24px;
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-item {
  display: flex;
  gap: 12px;
  max-width: 80%;
}

.user-message {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.assistant-message {
  align-self: flex-start;
}

.message-content {
  flex: 1;
}

.message-text {
  background: var(--n-card-color);
  padding: 12px 16px;
  border-radius: 12px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  line-height: 1.6;
  word-wrap: break-word;
}

.user-message .message-text {
  background: var(--n-primary-color);
  color: black;
  font-weight: 500;
}

.message-time {
  font-size: 12px;
  color: var(--n-text-color-depth-3);
  margin-top: 4px;
  text-align: right;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: var(--n-card-color);
  border-radius: 12px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.prompt-suggestion-card {
  margin-top: 12px;
}

.final-prompt-card {
  margin-top: 12px;
}

.save-hint {
  margin-top: 12px;
}

/* 增强保存按钮的视觉效果 */
.final-prompt-card :deep(.n-button--warning) {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  border-color: #d97706;
  font-weight: 600;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.4);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(245, 158, 11, 0);
  }
}

.input-container {
  padding: 16px 0 0 0;
  border-top: 1px solid var(--n-border-color);
  background: var(--n-card-color);
  position: sticky;
  bottom: 0;
  z-index: 10;
  backdrop-filter: blur(8px);
  border-radius: 0 0 8px 8px;
  margin-top: auto;
}


.templates-grid {
  max-height: 500px;
  overflow-y: auto;
}

.template-card {
  cursor: pointer;
  transition: transform 0.2s ease;
}

.template-card:hover {
  transform: translateY(-2px);
}

.template-meta {
  margin-top: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .title-section h1 {
    font-size: 20px;
  }

  .message-item {
    max-width: 95%;
  }
}
</style>