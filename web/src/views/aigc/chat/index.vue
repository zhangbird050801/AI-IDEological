<template>
  <AppPage>
    <div class="aigc-chat-page">
      <!-- <div class="page-header">
        <div class="header-content">
          <div class="title-section">
            <h1>AIGC思政案例生成</h1>
            <p>智能生成《软件工程》课程思政教学案例，提升教学效果</p>
          </div>
          
          <div class="stats-section">
            <n-space>
              <n-statistic label="今日生成" :value="todayGenerated" />
              <n-statistic label="总计案例" :value="totalCases" />
              <n-statistic label="使用时长" :value="usageTime" suffix="分钟" />
            </n-space>
          </div>
        </div>
      </div> -->

      <div class="chat-layout">
        <div class="chat-main">
          <ChatContainer
            ref="chatContainer"
            :messages="messages"
            :is-generating="isGenerating"
            @use-example="handleUseExample"
            @regenerate="handleRegenerate"
            @save-case="handleSaveCase"
          />

          <div class="input-section">
            <ChatInput
              ref="chatInput"
              :loading="isGenerating"
              @send="handleSendMessage"
              @clear-history="handleClearHistory"
            />
          </div>
        </div>

        <div class="sidebar">
          <n-card title="生成历史" size="small">
            <div v-if="chatHistory.length === 0" class="empty-history">
              <n-empty size="small" description="暂无历史记录" />
            </div>

            <div v-else class="history-list">
              <div
                v-for="session in chatHistory"
                :key="session.id"
                class="history-item"
                :class="{ active: currentSessionId === session.id }"
                @click="loadSession(session.id)"
              >
                <div class="history-title">{{ session.title }}</div>
                <div class="history-time">{{ formatTime(session.createdAt) }}</div>
              </div>
            </div>

            <template #action>
              <n-button size="small" text @click="showAllHistory"> 查看全部 </n-button>
            </template>
          </n-card>

          <n-card title="上下文配置" size="small" style="margin-top: 16px">
            <n-space vertical>
              <n-select
                v-model:value="selectedTemplateId"
                :options="templateOptions"
                placeholder="选择提示词模板"
                clearable
                filterable
                size="small"
                @update:value="applyPromptPreset"
              />
              <n-select
                v-model:value="selectedChapterId"
                :options="chapterOptionsRich.map(c => ({ label: c.label, value: c.value }))"
                placeholder="选择章节（自动填简介）"
                clearable
                filterable
                size="small"
                @update:value="applyPromptPreset"
              />
              <n-select
                v-model:value="selectedTheme"
                :options="themeOptions"
                placeholder="选择思政主题"
                clearable
                filterable
                size="small"
                @update:value="applyPromptPreset"
              />
              <n-select
                v-model:value="selectedCaseType"
                :options="caseTypeOptions"
                placeholder="选择案例类型"
                clearable
                size="small"
                @update:value="applyPromptPreset"
              />
              <n-button size="small" block @click="applyPromptPreset">
                <template #icon>
                  <n-icon><Icon icon="ant-design:edit-outlined" /></n-icon>
                </template>
                套用模板到输入框
              </n-button>
            </n-space>
          </n-card>

          <n-card title="快捷操作" size="small" style="margin-top: 16px">
            <n-space vertical>
              <n-button size="small" block @click="showCaseLibrary">
                <template #icon
                  ><n-icon><Icon icon="ant-design:library-outlined" /></n-icon
                ></template>
                案例库
              </n-button>

              <n-button size="small" block @click="showPromptTemplates">
                <template #icon
                  ><n-icon><Icon icon="ant-design:book-outlined" /></n-icon
                ></template>
                随机加载模板
              </n-button>

              <n-button size="small" block @click="exportCurrentChat">
                <template #icon
                  ><n-icon><Icon icon="ant-design:export-outlined" /></n-icon
                ></template>
                导出对话
              </n-button>
            </n-space>
          </n-card>
        </div>
      </div>
    </div>
    
    <!-- 保存案例模态框 -->
    <n-modal
      v-model:show="saveCaseVisible"
      preset="dialog"
      title="保存为案例"
      positive-text="保存"
      negative-text="取消"
      @positive-click="confirmSaveCase"
      style="width: 700px"
    >
      <n-form :model="caseForm" label-placement="left" label-width="140px">
        <n-form-item label="案例标题" required>
          <n-input v-model:value="caseForm.title" placeholder="请输入案例标题" />
        </n-form-item>
        
        <n-form-item label="软件工程章节" required>
          <n-select
            v-model:value="caseForm.software_engineering_chapter"
            :options="chapterOptions"
            placeholder="请选择章节"
            filterable
          />
        </n-form-item>
        
        <n-form-item label="思政主题" required>
          <n-select
            v-model:value="caseForm.ideological_theme"
            :options="themeOptions"
            placeholder="请选择思政主题"
            filterable
          />
        </n-form-item>
        
        <n-form-item label="案例类型" required>
          <n-select
            v-model:value="caseForm.case_type"
            :options="caseTypeOptions"
            placeholder="请选择案例类型"
          />
        </n-form-item>
        
        <n-form-item label="难度等级">
          <n-input-number
            v-model:value="caseForm.difficulty_level"
            :min="1"
            :max="5"
            style="width: 100%"
          >
            <template #suffix>级</template>
          </n-input-number>
        </n-form-item>
        
        <n-form-item label="标签">
          <n-dynamic-tags v-model:value="caseForm.tags" />
        </n-form-item>
        
        <n-form-item label="关键知识点">
          <n-dynamic-tags v-model:value="caseForm.key_points" />
        </n-form-item>
        
        <n-form-item label="讨论问题">
          <n-dynamic-tags v-model:value="caseForm.discussion_questions" />
        </n-form-item>
        
        <n-form-item label="教学建议">
          <n-input
            v-model:value="caseForm.teaching_suggestions"
            type="textarea"
            placeholder="请输入教学建议"
            :autosize="{ minRows: 3, maxRows: 6 }"
          />
        </n-form-item>
      </n-form>
    </n-modal>
  </AppPage>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, watch } from 'vue'
import {
  NSpace,
  NStatistic,
  NCard,
  NEmpty,
  NButton,
  NIcon,
  NModal,
  NForm,
  NFormItem,
  NInput,
  NSelect,
  NInputNumber,
  NDynamicTags,
  useMessage,
  useLoadingBar,
} from 'naive-ui'
import { Icon } from '@iconify/vue'
import AppPage from '@/components/page/AppPage.vue'
import ChatContainer from '@/components/chat/ChatContainer.vue'
import ChatInput from '@/components/chat/ChatInput.vue'
import { chatAPI, chatStream } from '@/api/aigc'
import { request } from '@/utils/http'
import api from '@/api'
import { templatesApi, themeCategoriesApi } from '@/api/ideological'

// 响应式数据
const message = useMessage()
const loadingBar = useLoadingBar()
const chatContainer = ref()
const chatInput = ref()

// 聊天数据
const messages = ref([])
const isGenerating = ref(false)
const currentSessionId = ref(null)

// 统计数据
const todayGenerated = ref(0)
const totalCases = ref(0)
const usageTime = ref(0)

// 聊天历史
const chatHistory = ref([])

// 侧栏选择
const templateOptions = ref([])
const selectedTemplateId = ref(null)
const chapterOptionsRich = ref([])
const selectedChapterId = ref(null)
const chapterMap = ref({})
const selectedTheme = ref(null)
const selectedCaseType = ref(null)

// 保存案例相关
const saveCaseVisible = ref(false)
const currentSaveMessage = ref(null)
const caseForm = reactive({
  title: '',
  software_engineering_chapter: '',
  ideological_theme: '',
  case_type: 'case_study',
  tags: [],
  key_points: [],
  discussion_questions: [],
  teaching_suggestions: '',
  difficulty_level: 3,
})

// 选项数据
const chapterOptions = ref([])
const themeOptions = ref([])
const caseTypeOptions = [
  { label: '案例分析', value: 'case_study' },
  { label: '讨论题', value: 'discussion' },
  { label: '思考题', value: 'thinking' },
  { label: '示例', value: 'example' },
  { label: '实践项目', value: 'practice' },
]

// 处理发送消息
async function handleSendMessage(data) {
  const userMessage = {
    id: Date.now(),
    role: 'user',
    content: data.content,
    attachments: data.attachments,
    timestamp: new Date().toISOString(),
  }

  messages.value.push(userMessage)
  isGenerating.value = true
  loadingBar.start()

  try {
    const msgArr = [
      { role: 'system', content: 'You are a helpful assistant.' },
      ...messages.value.map((m) => ({ role: m.role, content: m.content })),
    ]

    // Create placeholder assistant message for streaming (make reactive so nested updates trigger)
    const assistantMessage = reactive({
      id: Date.now() + 1,
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString(),
      isStreaming: true,
      historyId: null, // 用于保存生成历史ID
    })
    messages.value.push(assistantMessage)

    // Try stream first
    const iterator = chatStream(msgArr)
    try {
      for await (const item of iterator) {
        // item is { type: 'chunk'|'text', payload: ... }
        let textToAppend = ''
        try {
          if (item && item.type === 'chunk' && item.payload) {
            const obj = item.payload
            if (obj.choices && Array.isArray(obj.choices)) {
              for (const c of obj.choices) {
                if (c && c.delta) {
                  // prefer delta.content, fallback to reasoning_content
                  if (typeof c.delta.content === 'string' && c.delta.content.length > 0) {
                    textToAppend += c.delta.content
                  } else if (
                    typeof c.delta.reasoning_content === 'string' &&
                    c.delta.reasoning_content.length > 0
                  ) {
                    textToAppend += c.delta.reasoning_content
                  }
                }
              }
            } else if (typeof obj.data === 'string') {
              textToAppend += obj.data
            }
          } else if (item && item.type === 'text') {
            textToAppend += String(item.payload)
          } else {
            // unknown shape, stringify
            textToAppend += JSON.stringify(item)
          }
        } catch (e) {
          textToAppend = String(item)
        }
        if (textToAppend) {
          assistantMessage.content += textToAppend
          messages.value = [...messages.value]
          await nextTick()
          chatContainer.value?.scrollToBottom()
        }
      }
      // stream finished
      assistantMessage.isStreaming = false
      loadingBar.finish()
      todayGenerated.value++
      totalCases.value++
      
      // 保存生成历史到后端（暂时注释掉，避免错误）
      // await saveGenerationHistory(userMessage.content, assistantMessage.content, assistantMessage)
      
      saveToHistory()
    } catch (streamErr) {
      console.error('Stream error, falling back to non-streaming:', streamErr)
      // remove streaming placeholder
      const idx = messages.value.findIndex((m) => m.id === assistantMessage.id)
      if (idx >= 0) messages.value.splice(idx, 1)
      // fallback to non-streaming API
      const res = await chatAPI(msgArr)
      const finalReply = (res && (res.reply ?? res.data?.reply)) || ''
      const fallbackMessage = {
        id: Date.now() + 2,
        role: 'assistant',
        content: finalReply,
        timestamp: new Date().toISOString(),
        historyId: null,
      }
      messages.value.push(fallbackMessage)
      loadingBar.finish()
      todayGenerated.value++
      totalCases.value++
      
      // 保存生成历史到后端（暂时注释掉，避免错误）
      // await saveGenerationHistory(userMessage.content, finalReply, fallbackMessage)
      
      saveToHistory()
    }
  } catch (error) {
    console.error('生成失败:', error)
    message.error('生成失败，请重试')
    loadingBar.error()
    // 如果出错，移除可能添加的空消息
    const lastMessage = messages.value[messages.value.length - 1]
    if (lastMessage && lastMessage.role === 'assistant' && !lastMessage.content) {
      messages.value.pop()
    }
  } finally {
    isGenerating.value = false
  }
}

function handleUseExample(content) {
  chatInput.value?.focus()
  handleSendMessage({ content, attachments: [] })
}

// 重新生成
function handleRegenerate(messageId) {
  const messageIndex = messages.value.findIndex((msg) => msg.id === messageId)
  if (messageIndex > 0) {
    const userMessage = messages.value[messageIndex - 1]
    // 移除原有的AI回复
    messages.value.splice(messageIndex)
    // 重新生成
    handleSendMessage({ content: userMessage.content, attachments: userMessage.attachments || [] })
  }
}

// 保存生成历史到后端
async function saveGenerationHistory(userInput, generatedContent, messageObj) {
  try {
    // 暂时为每条消息生成一个临时ID（后续需要实现真实的后端保存）
    messageObj.historyId = Date.now()
    
    // TODO: 实现真实的后端API调用
    // const historyData = {
    //   user_input: userInput,
    //   generated_content: generatedContent,
    //   generation_type: 'aigc_chat',
    //   software_engineering_chapter: '',
    //   ideological_theme: '',
    // }
    // const response = await request.post('/aigc/enhanced/history', historyData)
    // if (response && response.id) {
    //   messageObj.historyId = response.id
    // }
  } catch (error) {
    console.error('保存生成历史失败:', error)
    // 即使失败也分配一个临时ID，确保功能可用
    messageObj.historyId = Date.now()
  }
}

// 保存案例
function handleSaveCase(messageObj) {
  // 检查消息是否有内容
  if (!messageObj.content || messageObj.content.trim() === '') {
    message.error('消息内容为空，无法保存为案例')
    return
  }
  
  currentSaveMessage.value = messageObj
  
  // 重置表单
  Object.assign(caseForm, {
    title: '',
    software_engineering_chapter: '',
    ideological_theme: '',
    case_type: 'case_study',
    tags: [],
    key_points: [],
    discussion_questions: [],
    teaching_suggestions: '',
    difficulty_level: 3,
  })
  
  // 自动提取标题（取内容前50个字符）
  const titleText = messageObj.content.substring(0, 50).replace(/\n/g, ' ')
  caseForm.title = titleText + (messageObj.content.length > 50 ? '...' : '')
  
  saveCaseVisible.value = true
}

// 确认保存案例
async function confirmSaveCase() {
  return new Promise(async (resolve, reject) => {
    try {
      // 验证必填字段
      if (!caseForm.title || !caseForm.software_engineering_chapter || !caseForm.ideological_theme) {
        message.error('请填写所有必填项')
        reject(new Error('缺少必填项'))
        return
      }
      
      const caseData = {
        title: caseForm.title.trim(),
        content: currentSaveMessage.value.content, // 直接使用消息内容
        software_engineering_chapter: caseForm.software_engineering_chapter,
        ideological_theme: caseForm.ideological_theme,
        case_type: caseForm.case_type || 'case_study',
        tags: caseForm.tags || [],
        key_points: caseForm.key_points || [],
        discussion_questions: caseForm.discussion_questions || [],
        teaching_suggestions: caseForm.teaching_suggestions || '',
        difficulty_level: caseForm.difficulty_level || 3,
        is_public: true, // 默认公开
        status: 'published', // 直接发布，不需要审核
      }
      
      console.log('保存案例数据:', caseData)
      
      // 直接调用创建案例的API
      const response = await request.post('/ideological/cases/', caseData)
      
      console.log('保存成功:', response)
      message.success('案例已成功保存到案例库！')
      resolve(true)
    } catch (error) {
      console.error('保存案例失败:', error)
      // 显示更详细的错误信息
      const errorMsg = error.response?.data?.detail || error.message || '保存案例失败，请重试'
      message.error(errorMsg)
      reject(error)
    }
  })
}

// 清空历史
function handleClearHistory() {
  messages.value = []
  currentSessionId.value = null
  localStorage.removeItem('aigc-chat-current-messages')
}

// 保存到历史记录
function saveToHistory() {
  if (messages.value.length >= 2) {
    const session = {
      id: currentSessionId.value || Date.now(),
      title: messages.value[0].content.substring(0, 30) + '...',
      // store plain objects (avoid reactive proxies)
      messages: messages.value.map((m) => ({ ...m })),
      createdAt: new Date().toISOString(),
    }

    const existingIndex = chatHistory.value.findIndex((s) => s.id === session.id)
    if (existingIndex >= 0) {
      chatHistory.value[existingIndex] = session
    } else {
      chatHistory.value.unshift(session)
    }

    currentSessionId.value = session.id

    // 限制历史记录数量
    if (chatHistory.value.length > 20) {
      chatHistory.value = chatHistory.value.slice(0, 20)
    }
  }
}

// 加载会话
function loadSession(sessionId) {
  const session = chatHistory.value.find((s) => s.id === sessionId)
  if (session) {
    messages.value = [...session.messages]
    currentSessionId.value = sessionId
    nextTick(() => {
      chatContainer.value?.scrollToBottom()
    })
  }
}

// 格式化时间
function formatTime(timestamp) {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return date.toLocaleDateString()
}

// 显示案例库
function showCaseLibrary() {
  // 这里可以跳转到案例库页面或显示弹窗
  message.info('即将跳转到案例库')
}

// 显示提示词模板
function showPromptTemplates() {
  if (templateOptions.value.length === 0) {
    message.warning('暂无可用的提示词模板')
    return
  }
  // 默认加载第一个模板
  const first = templateOptions.value[0]
  selectedTemplateId.value = first.value
  applyPromptPreset()
  message.success(`已加载模板: ${first.label}`)
}

// 导出当前对话
function exportCurrentChat() {
  chatContainer.value?.exportChat()
}

// 显示全部历史
function showAllHistory() {
  message.info('查看全部历史功能开发中')
}

// 获取选项数据
async function fetchOptions() {
  try {
    const chaptersResponse = await request.get('/ideological/cases/chapters/list')
    chapterOptions.value = (chaptersResponse.data || chaptersResponse || []).map(item => ({
      label: item,
      value: item
    }))
  } catch (error) {
    console.error('获取章节选项失败:', error)
    chapterOptions.value = [
      '软件工程概述', '软件过程模型', '需求分析', '系统设计', '编码实现',
      '软件测试', '软件维护', '项目管理', '软件质量', '软件工程前沿'
    ].map(item => ({ label: item, value: item }))
  }
  
  try {
    const response = await themeCategoriesApi.getNames()
    themeOptions.value = response.map(item => ({
      label: item,
      value: item,
    }))
  } catch (error) {
    console.error('获取主题选项失败:', error)
    themeOptions.value = [
      '工匠精神', '创新精神', '团队协作', '责任担当', '诚信品质',
      '法治意识', '科学精神', '人文素养', '家国情怀', '国际视野'
    ].map(item => ({ label: item, value: item }))
  }

  // 课程章节（含描述）从课程管理获取
  try {
    const res = await api.getChaptersByCourse(1)
    const chapters = res?.data || res || []
    chapterOptionsRich.value = chapters.map((c) => ({
      label: c.name,
      value: c.id,
      desc: c.description,
    }))
    chapterMap.value = Object.fromEntries(chapters.map((c) => [c.id, c]))
  } catch (error) {
    console.error('获取章节详情失败:', error)
  }

  // 提示词模板列表
  try {
    const res = await templatesApi.getList({ page: 1, size: 50, is_active: true })
    const data = res?.data || res || {}
    const items = data.items || data || []
    templateOptions.value = items.map((t) => ({
      label: t.name,
      value: t.id,
      content: t.template_content || t.content,
    }))
  } catch (error) {
    console.error('获取提示词模板失败:', error)
    templateOptions.value = []
  }
}

function applyPromptPreset() {
  const template = templateOptions.value.find((t) => t.value === selectedTemplateId.value)
  const chapter = chapterMap.value[selectedChapterId.value]
  if (!template) return

  const parts = [template.content || '']
  if (chapter) {
    parts.push(`\n章节：${chapter.name}`)
    if (chapter.description) parts.push(`章节简介：${chapter.description}`)
  }
  if (selectedTheme.value) {
    parts.push(`思政主题：${selectedTheme.value}`)
  }
  if (selectedCaseType.value) {
    const caseLabel = caseTypeOptions.find((c) => c.value === selectedCaseType.value)?.label || selectedCaseType.value
    parts.push(`案例类型：${caseLabel}`)
  }

  chatInput.value?.setContent(parts.filter(Boolean).join('\n'))
}

// 组件挂载时初始化
onMounted(() => {
  // 模拟加载统计数据
  todayGenerated.value = 3
  totalCases.value = 156
  usageTime.value = 45

  // 获取选项数据
  fetchOptions()
  
  // 从localStorage加载历史记录
  const savedHistory = localStorage.getItem('aigc-chat-history')
  if (savedHistory) {
    try {
      chatHistory.value = JSON.parse(savedHistory)
    } catch (e) {
      console.warn('Failed to load chat history:', e)
    }
  }

  // 从localStorage加载当前对话
  const savedMessages = localStorage.getItem('aigc-chat-current-messages')
  if (savedMessages) {
    try {
      messages.value = JSON.parse(savedMessages)
      message.info('已恢复上次的对话')
    } catch (e) {
      console.warn('Failed to load current messages:', e)
    }
  }

  // 检查是否有选中的模板
  const selectedTemplate = localStorage.getItem('selected_template')
  if (selectedTemplate) {
    try {
      const template = JSON.parse(selectedTemplate)
      // 填充模板内容到输入框
      nextTick(() => {
        if (chatInput.value && template.content) {
          chatInput.value.setContent(template.content)
          message.success(`已加载模板: ${template.name}`)
        }
      })
      // 清除已使用的模板
      localStorage.removeItem('selected_template')
    } catch (e) {
      console.warn('Failed to load selected template:', e)
    }
  }
})

// 监听历史记录变化，自动保存
watch(
  chatHistory,
  (newHistory) => {
    localStorage.setItem('aigc-chat-history', JSON.stringify(newHistory))
  },
  { deep: true }
)

// 监听当前消息变化，自动保存
watch(
  messages,
  (newMessages) => {
    if (newMessages.length > 0) {
      localStorage.setItem('aigc-chat-current-messages', JSON.stringify(newMessages))
    }
  },
  { deep: true }
)
</script>

<style scoped>
.aigc-chat-page {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.page-header {
  background: linear-gradient(135deg, #ff8a65 0%, #ff7043 100%);
  color: #ffffff;
  padding: 24px;
  margin-bottom: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(255, 138, 101, 0.2);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-section h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #ffffff !important;
}

.title-section p {
  margin: 0;
  opacity: 0.9;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9) !important;
}

.stats-section {
  --n-label-text-color: rgba(255, 255, 255, 0.8) !important;
  --n-value-text-color: #ffffff !important;
}

.stats-section .n-statistic .n-statistic-label,
.stats-section .n-statistic .n-statistic-value {
  color: #ffffff !important;
}

.chat-layout {
  flex: 1;
  display: flex;
  gap: 24px;
  min-height: 0;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.input-section {
  margin-top: 16px;
}

.sidebar {
  width: 280px;
  flex-shrink: 0;
}

.empty-history {
  text-align: center;
  padding: 20px 0;
}

.history-list {
  max-height: 300px;
  overflow-y: auto;
}

.history-item {
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  border: 1px solid transparent;
}

.history-item:hover {
  background-color: var(--n-color-hover);
}

.history-item.active {
  background-color: var(--n-primary-color-suppl);
  border-color: var(--n-primary-color);
}

.history-title {
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 4px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.history-time {
  font-size: 11px;
  color: var(--n-text-color-depth-3);
}

/* 主题适配 */
[data-theme='dark'] .page-header {
  background: linear-gradient(135deg, #d84315 0%, #bf360c 100%);
  box-shadow: 0 2px 8px rgba(216, 67, 21, 0.25);
}

[data-theme='dark'] .title-section h1,
[data-theme='dark'] .title-section p {
  color: #ffffff !important;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .sidebar {
    width: 240px;
  }
}

@media (max-width: 768px) {
  .chat-layout {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    order: -1;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .title-section h1 {
    font-size: 20px;
  }
}
</style>
