<template>
  <AppPage>
    <div class="prompt-assistant-page">
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
                  <n-button quaternary size="small" @click="startNewSession">
                    <template #icon>
                      <n-icon><Icon icon="mdi:refresh" /></n-icon>
                    </template>
                    清空对话
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
                  <div class="preset-panel">
                    <n-space wrap align="center">
                      <n-select
                        v-model:value="presetForm.course_id"
                        placeholder="预设课程"
                        :options="courseOptions"
                        clearable
                        style="min-width: 180px"
                        @update:value="handleCourseChange"
                      />
                      <n-select
                        v-model:value="presetForm.software_engineering_chapter"
                        placeholder="预设软件工程章节"
                        :options="chapterOptions"
                        clearable
                        style="min-width: 180px"
                      />
                      <n-select
                        v-model:value="presetForm.knowledge_point"
                        placeholder="预设知识点"
                        :options="knowledgePointOptions"
                        clearable
                        style="min-width: 180px"
                      />
                      <n-select
                        v-model:value="presetForm.ideological_theme"
                        placeholder="预设思政主题"
                        :options="themeOptions"
                        clearable
                        style="min-width: 180px"
                      />
                      <n-button size="small" type="primary" @click="applyPresetToInput">
                        填入提示
                      </n-button>
                      <n-button size="small" text @click="resetPreset">
                        清空预设
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
                        <pre class="prompt-code-display">{{ message.suggestedPrompt }}</pre>
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
                        <pre class="prompt-code-display">{{ message.finalPrompt }}</pre>

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
                  @keydown.enter="handleEnterKey"
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

          <n-form-item-grid-item label="思政主题" path="theme_category_id">
            <n-select
              v-model:value="templateForm.theme_category_id"
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
import { ref, reactive, onMounted, nextTick, computed, watch } from 'vue'
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
} from 'naive-ui'
import { Icon } from '@iconify/vue'
import AppPage from '@/components/page/AppPage.vue'
import { request } from '@/utils/http'
import { themeCategoriesApi } from '@/api/ideological'
import * as courseApi from '@/api/courses'
import { getToken } from '@/utils/auth/token'
import MarkdownIt from 'markdown-it'

// 初始化markdown渲染器
const md = new MarkdownIt({
  html: true,
  linkify: true,
  // 将单个换行渲染为<br>，结合 CSS 去掉 pre-wrap 可以避免额外空行
  breaks: true,
})

// 响应式数据
const message = useMessage()

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
  theme_category_id: null,
})

// 模板选项
const templateTypeOptions = ref([])
const categoryOptions = ref([])
const chapterOptions = ref([])
const themeOptions = ref([])
const knowledgePointOptions = ref([])
const chapterIdMap = ref({})
const courseIdForPreset = ref(null)
const courseOptions = ref([])

// 预设表单
const presetForm = reactive({
  course_id: null,
  software_engineering_chapter: null,
  knowledge_point: null,
  ideological_theme: null,
})

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
  const matches = templateForm.template_content.match(/\{\{\s*([^}]+?)\s*\}\}/g)
  if (!matches) return []
  return [
    ...new Set(
      matches
        .map(match => match.replace(/^\{\{\s*|\s*\}\}$/g, '').trim())
        .filter(Boolean)
    )
  ]
})

// 快速开始示例
const quickStartExamples = ref([])

// 知识点默认映射已由后端提供，前端仅在无数据时使用空兜底
const knowledgePointMap = {}

const loadChaptersAndKnowledge = async () => {
  try {
    // 取课程列表
    const coursesResp = await courseApi.getAllCourses(true)
    const courses = coursesResp?.data || coursesResp || []
    if (Array.isArray(courses) && courses.length > 0) {
      courseOptions.value = courses.map(c => ({ label: c.name, value: c.id }))
      if (!presetForm.course_id) {
        courseIdForPreset.value = courses[0].id
        presetForm.course_id = courses[0].id
      }
    }

    // 拉取章节（包含ID）用于知识点查询
    if (presetForm.course_id) {
      const chaptersResp = await courseApi.getChaptersByCourse(presetForm.course_id)
      const chapters = chaptersResp?.data || chaptersResp || []
      chapterOptions.value = chapters.map(ch => ({ label: ch.name, value: ch.id }))
      chapterIdMap.value = chapters.reduce((map, ch) => {
        map[ch.id] = ch.name
        return map
      }, {})
    }

    // 初始化知识点选项（仅在有章节数据时）
    const initialChapterId = presetForm.software_engineering_chapter || chapterOptions.value?.[0]?.value
    if (initialChapterId) {
      await fetchKnowledgePoints(initialChapterId)
    } else {
      knowledgePointOptions.value = []
    }
  } catch (error) {
    console.error('❗ [PromptAssistant] 加载章节/知识点失败:', error)
    // 兜底：避免抛错但不提供硬编码数据
    chapterOptions.value = []
    chapterIdMap.value = {}
    knowledgePointOptions.value = []
  }
}

const fetchKnowledgePoints = async (chapterId) => {
  // 优先调用后端接口获取知识点列表
  if (chapterId) {
    try {
      const kpResp = await courseApi.getKnowledgePointsByChapter(chapterId)
      const kpList = kpResp?.data || kpResp || []
      if (Array.isArray(kpList) && kpList.length > 0) {
        knowledgePointOptions.value = kpList.map(kp => ({
          label: kp.name,
          value: kp.name,
        }))
        return
      }
    } catch (error) {
      console.error('❗ [PromptAssistant] 获取知识点失败，使用本地兜底:', error)
    }
  }

  // 后端无数据或失败，兜底为空列表
  knowledgePointOptions.value = []
}

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

  // 创建助手消息对象（流式更新）
  const assistantMessage = reactive({
    type: 'assistant',
    content: '',
    timestamp: new Date(),
    isStreaming: true
  })
  messages.value.push(assistantMessage)

  try {
    // 获取token
    const token = getToken()
    if (!token) {
      throw new Error('未登录，请先登录')
    }

    // 使用流式API
    const response = await fetch('/api/v1/ideological/prompt-assistant/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'token': token
      },
      body: JSON.stringify({
        message: userMessage,
        session_id: currentSessionId.value || null
      })
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error('请求失败:', response.status, errorText)
      throw new Error(`网络请求失败: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      
      // 保留最后一行（可能不完整）
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.trim() === '') continue
        
        if (line.startsWith('data: ')) {
          try {
            const jsonStr = line.slice(6).trim()
            if (!jsonStr) continue
            
            const data = JSON.parse(jsonStr)
            
            if (data.type === 'session_id') {
              currentSessionId.value = data.session_id
            } else if (data.type === 'content') {
              assistantMessage.content += data.content
              await scrollToBottom()
            } else if (data.type === 'done') {
              assistantMessage.isStreaming = false
              
              // 更新阶段
              if (data.session_stage) {
                currentStage.value = stageLabels[data.session_stage] || '进行中'
              }
              
              // 设置建议的提示词
              if (data.suggested_prompt) {
                assistantMessage.suggestedPrompt = data.suggested_prompt
              }
              
              // 设置最终提示词
              if (data.final_prompt) {
                assistantMessage.finalPrompt = data.final_prompt
                isCompleted.value = true
                currentStage.value = '可以继续优化'
              }
            } else if (data.type === 'error' || data.error) {
              console.error('❌ 服务器错误:', data.error)
              throw new Error(data.error || '未知错误')
            }
          } catch (e) {
            console.warn('解析SSE数据失败:', line, e)
          }
        }
      }
    }

  } catch (error) {
    console.error('❌ 发送消息失败:', error)
    message.error(`发送消息失败: ${error.message}`)
    
    if (assistantMessage.content === '') {
      assistantMessage.content = '抱歉，我遇到了一些问题。请稍后再试。'
    }
    assistantMessage.isStreaming = false
  } finally {
    isLoading.value = false
    await scrollToBottom()
  }
}

const sendQuickStart = async (quickMessage) => {
  inputMessage.value = quickMessage
  await sendMessage()
}

const handleEnterKey = (event) => {
  // Shift+Enter 换行，单独 Enter 发送
  if (event.shiftKey) {
    return
  }
  event.preventDefault()
  sendMessage()
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

const getOptionLabel = (options, value) => {
  const list = Array.isArray(options?.value) ? options.value : options
  const found = list?.find?.(item => item?.value === value)
  return found?.label || value || ''
}

const getChapterLabelById = (id) => chapterIdMap.value?.[id] || getOptionLabel(chapterOptions, id)

const matchOptionValueByLabel = (options, text) => {
  if (!text) return null
  const list = Array.isArray(options?.value) ? options.value : options
  const hit = list?.find?.(opt =>
    opt?.label === text ||
    opt?.label?.includes?.(text) ||
    text?.includes?.(opt?.label)
  )
  return hit?.value || null
}

const splitSegments = (raw) => (raw || '')
  .split(/[、，,;；\n]/)
  .map(item => item.trim())
  .filter(Boolean)

const extractPromptMeta = (promptContent = '') => {
  const meta = {
    chapters: [],
    knowledgePoints: [],
    themes: [],
    deliverables: [],
    variables: [],
  }

  const chapterMatches = promptContent.match(/(?:软件工程)?章节[:：]\s*([^\n；;]+)/g)
  chapterMatches?.forEach(match => {
    const value = match.split(/[:：]/)[1]
    meta.chapters.push(...splitSegments(value))
  })

  const kpMatches = promptContent.match(/(?:知识点|适用知识点|核心知识点)[:：]\s*([^\n；;]+)/g)
  kpMatches?.forEach(match => {
    const value = match.split(/[:：]/)[1]
    meta.knowledgePoints.push(...splitSegments(value))
  })

  const themeMatches = promptContent.match(/(?:思政主题|价值观|思政元素)[:：]\s*([^\n；;]+)/g)
  themeMatches?.forEach(match => {
    const value = match.split(/[:：]/)[1]
    meta.themes.push(...splitSegments(value))
  })

  const deliverableMatches = promptContent.match(/(?:输出格式|交付物|产出|最终输出)[:：]\s*([^\n；;]+)/g)
  deliverableMatches?.forEach(match => {
    const value = match.split(/[:：]/)[1]
    meta.deliverables.push(...splitSegments(value))
  })

  const variableMatches = promptContent.match(/\{\{([^}]+)\}\}/g)
  if (variableMatches) {
    meta.variables = [...new Set(variableMatches.map(v => v.slice(2, -2).trim()).filter(Boolean))]
  }

  return meta
}

const handleCourseChange = async (courseId) => {
  presetForm.course_id = courseId
  presetForm.software_engineering_chapter = null
  presetForm.knowledge_point = null
  chapterOptions.value = []
  knowledgePointOptions.value = []
  if (courseId) {
    await loadChaptersAndKnowledge()
  }
}

const applyPresetToInput = () => {
  const chapterLabel = presetForm.software_engineering_chapter
    ? getChapterLabelById(presetForm.software_engineering_chapter)
    : ''
  const knowledgeLabel = presetForm.knowledge_point
    ? getOptionLabel(knowledgePointOptions, presetForm.knowledge_point)
    : ''
  const themeLabel = presetForm.ideological_theme
    ? getOptionLabel(themeOptions, presetForm.ideological_theme)
    : ''

  if (!chapterLabel && !knowledgeLabel && !themeLabel) {
    message.warning('请选择至少一项预设内容')
    return
  }

  const presetText = `请基于《软件工程》${chapterLabel ? `的${chapterLabel}章节` : ''}${knowledgeLabel ? `（知识点：${knowledgeLabel}）` : ''}${themeLabel ? `，强调${themeLabel}思政主题` : ''}，生成一段可直接喂给LLM的提示词模板。提示词应包含：1）课堂背景与受众；2）技术知识点与思政融入点；3）期望产出/输出格式（案例/讨论题/教学设计等，条目或表格均可）；4）可替换变量用{{变量名}}标记；5）2-3条学生讨论或实践指令。`

  inputMessage.value = inputMessage.value
    ? `${inputMessage.value.trim()}\n${presetText}`
    : presetText
  message.success('已填入更详细的预设，可直接发送或继续补充需求')
}

const resetPreset = () => {
  presetForm.software_engineering_chapter = null
  presetForm.knowledge_point = null
  presetForm.ideological_theme = null
}

const formatMessage = (content) => {
  // 检查 content 是否为 undefined 或 null
  if (!content || typeof content !== 'string') {
    return ''
  }

  // 清理多余的空行
  let cleanedContent = content
    // 移除行尾空格
    .replace(/[ \t]+$/gm, '')
    // 将3个或更多连续换行符替换为2个
    .replace(/\n{3,}/g, '\n\n')
    // 移除开头和结尾的空行
    .trim()
  
  // 使用markdown-it渲染
  return md.render(cleanedContent)
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

const startNewSession = () => {
  messages.value = []
  currentSessionId.value = ''
  currentStage.value = '准备开始'
  isCompleted.value = false
  localStorage.removeItem('prompt-assistant-messages')
  message.success('已开始新会话')
}

const showTemplates = async () => {
  try {
    const response = await request.get('/ideological/prompt-assistant/templates')
    // 处理多种可能的响应格式
    if (Array.isArray(response)) {
      templates.value = response
    } else if (response?.data && Array.isArray(response.data)) {
      templates.value = response.data
    } else if (response?.items && Array.isArray(response.items)) {
      templates.value = response.items
    } else {
      templates.value = []
    }
    
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
    theme_category_id: null,
  })

  // 自动提取变量
  const meta = extractPromptMeta(promptContent)
  templateForm.variables = meta.variables.length > 0 ? meta.variables : extractedVariables.value

  // 🔧 增强：智能分析提示词内容
  const userRequests = messages.value
    .filter(m => m.type === 'user')
    .map(m => m.content)
    .join(' ')

  // 关键词检测
  const keywords = []
  const keywordMap = {
    '写作': ['写', '创作', '编写', '文章', '内容', '写作'],
    '编程': ['代码', '程序', '编程', '开发', 'code', 'programming'],
    '分析': ['分析', '总结', '评估', '研究'],
    '创意': ['创意', '想象', '故事', '设计'],
    '教学': ['教学', '课程', '学习', '教育'],
    '思政': ['思政', '价值观', '道德', '伦理']
  }

  for (const [category, words] of Object.entries(keywordMap)) {
    if (words.some(word => userRequests.includes(word) || promptContent.includes(word))) {
      keywords.push(category)
    }
  }

  // 🔧 增强：基于提示词内容提取章节/主题并反填
  if (meta.chapters.length > 0) {
    templateForm.software_engineering_chapter = matchOptionValueByLabel(chapterOptions, meta.chapters[0]) || meta.chapters[0]
  }
  if (meta.themes.length > 0) {
    templateForm.theme_category_id = matchOptionValueByLabel(themeOptions, meta.themes[0]) || templateForm.theme_category_id
  }
  // 若提取失败，回退使用当前预设选择
  if (!templateForm.software_engineering_chapter && presetForm.software_engineering_chapter) {
    templateForm.software_engineering_chapter = presetForm.software_engineering_chapter
  }
  if (!templateForm.theme_category_id && presetForm.ideological_theme) {
    templateForm.theme_category_id = presetForm.ideological_theme
  }

  // 🔧 增强：智能填充名称和描述
  const date = new Date().toLocaleDateString('zh-CN').replace(/\//g, '-')
  const mainChapter = meta.chapters[0] || getChapterLabelById(presetForm.software_engineering_chapter) || '软件工程'
  const mainKnowledge = meta.knowledgePoints[0] || presetForm.knowledge_point || ''
  const mainTheme = meta.themes[0] || getOptionLabel(themeOptions, presetForm.ideological_theme) || '思政主题'
  const keywordStr = keywords.length > 0 ? keywords.join('_') : (mainChapter || '通用')

  templateForm.name = `${mainChapter}${mainKnowledge ? `-${mainKnowledge}` : ''}提示词模板_${date}`
  templateForm.description = `面向《软件工程》${mainChapter}章节${mainKnowledge ? `（${mainKnowledge}）` : ''}，融合${mainTheme}，适用于${keywordStr}相关场景的提示词模板。`

  // 🔧 增强：智能选择类型和分类
  const deliverableHint = meta.deliverables.join('、')

  if (deliverableHint.includes('讨论') || keywords.includes('分析')) {
    templateForm.template_type = 'discussion_generation'
    templateForm.category = '思政讨论'
  } else if (deliverableHint.includes('教学设计') || deliverableHint.includes('教案') || keywords.includes('教学')) {
    templateForm.template_type = 'teaching_design'
    templateForm.category = '教学方法'
  } else if (deliverableHint.includes('思考') || deliverableHint.includes('练习')) {
    templateForm.template_type = 'thinking_generation'
    templateForm.category = '思考题'
  } else if (deliverableHint.includes('评价') || deliverableHint.includes('复盘')) {
    templateForm.template_type = 'knowledge_point'
    templateForm.category = '质量评价'
  } else if (keywords.includes('写作')) {
    templateForm.template_type = 'content_optimization'
    templateForm.category = '内容优化'
  } else if (keywords.includes('编程')) {
    templateForm.template_type = 'practice'
    templateForm.category = '实践指导'
  } else if (keywords.includes('分析')) {
    templateForm.template_type = 'knowledge_point'
    templateForm.category = '知识点讲解'
  } else if (keywords.includes('思政')) {
    templateForm.template_type = 'case_generation'
    templateForm.category = '思政案例'
  } else {
    templateForm.template_type = 'case_generation'
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

    // 获取章节+知识点（使用数据库数据）
    await loadChaptersAndKnowledge()

    // 获取主题选项（从数据库读取）
    try {
      const themesResponse = await themeCategoriesApi.getList()
      // 响应可能被多次包装
      let themesData = themesResponse?.data?.data || themesResponse?.data || themesResponse
      // 确保是数组
      if (!Array.isArray(themesData)) {
        console.error('❗ [PromptAssistant] 主题数据不是数组')
        throw new Error('主题数据格式错误')
      }
      
      // 只使用启用的二级分类
      themeOptions.value = themesData
        .filter(item => item.is_active && item.parent_id !== null)
        .map(item => ({
          label: item.name,
          value: item.id,  // 使用ID作为值
        }))
    } catch (error) {
      console.error('❗ [PromptAssistant] 获取思政主题失败:', error)
      // 使用默认主题数据作为fallback
      themeOptions.value = [
        { label: '工匠精神', value: 5 },
        { label: '创新精神', value: 6 },
        { label: '团队协作', value: 11 },
        { label: '责任担当', value: 9 },
        { label: '诚信品质', value: 8 },
        { label: '法治意识', value: 10 },
        { label: '科学精神', value: 7 },
        { label: '人文素养', value: 13 },
        { label: '家国情怀', value: 12 },
        { label: '国际视野', value: 14 }
      ]
    }
  } catch (error) {
    message.error('获取选项数据失败')
  }
}

// 监听章节选择，动态调整知识点选项
watch(
  () => presetForm.software_engineering_chapter,
  async (chapterId) => {
    await fetchKnowledgePoints(chapterId)
    const names = knowledgePointOptions.value.map(item => item.value)
    if (!names.includes(presetForm.knowledge_point)) {
      presetForm.knowledge_point = null
    }
  }
)

watch(
  () => presetForm.course_id,
  async (courseId, prev) => {
    if (courseId !== prev) {
      await handleCourseChange(courseId)
    }
  }
)

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
  }

  // 从localStorage恢复对话
  const savedMessages = localStorage.getItem('prompt-assistant-messages')
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

  // 检查是否是从模板页面跳转过来的
  fromTemplatePage.value = localStorage.getItem('from_template_page') === 'true'

  fetchTemplateOptions()
})

// 监听消息变化，自动保存
watch(
  messages,
  (newMessages) => {
    if (newMessages.length > 0) {
      localStorage.setItem('prompt-assistant-messages', JSON.stringify(newMessages))
    }
  },
  { deep: true }
)
</script>

<style scoped>
.prompt-assistant-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 10px;
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
  background: rgba(250, 250, 252, 0.5);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
}

.chat-container :deep(.n-card__content) {
  padding: 0;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.8);
}

.assistant-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.assistant-details {
  flex: 1;
  min-width: 0;
}

.assistant-details h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.status-text {
  margin: 0;
  font-size: 12px;
  opacity: 0.7;
  color: var(--n-text-color-depth-3);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.assistant-avatar {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
  color: #667eea;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 12px;
  min-height: 0;
  scroll-behavior: smooth;
  background: rgba(250, 250, 252, 0.3);
  width: 100%;
  box-sizing: border-box;
}

.messages-container::-webkit-scrollbar {
  width: 4px;
}

.messages-container::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.15);
  border-radius: 2px;
}

.welcome-message {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
}

.welcome-content {
  max-width: 480px;
  padding: 20px;
}

.welcome-content h3 {
  margin: 12px 0 6px 0;
  color: var(--n-text-color);
  font-size: 18px;
}

.welcome-content p {
  margin: 0 0 16px 0;
  color: var(--n-text-color-depth-3);
  font-size: 14px;
}

.preset-panel {
  margin-top: 12px;
  padding: 12px;
  border: 1px dashed var(--n-border-color);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.6);
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
}

.message-item {
  display: flex;
  gap: 8px;
  max-width: 85%;
  width: fit-content;
}

.user-message {
  align-self: flex-end;
  flex-direction: row-reverse;
  margin-left: auto;
}

.assistant-message {
  align-self: flex-start;
  margin-right: auto;
}

.message-content {
  flex: 1;
  min-width: 0;
  max-width: 100%;
  overflow: hidden;
}

.message-text {
  background: rgba(255, 255, 255, 0.9);
  padding: 10px 14px;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  line-height: 1.6;
  word-wrap: break-word;
  word-break: break-word;
  overflow-wrap: break-word;
  width: 100%;
  box-sizing: border-box;
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.user-message .message-text {
  background: rgba(24, 160, 88, 0.08);
  border-color: rgba(24, 160, 88, 0.15);
  color: var(--n-text-color);
}

.message-time {
  font-size: 11px;
  color: var(--n-text-color-depth-3);
  margin-top: 3px;
  text-align: right;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.prompt-suggestion-card {
  margin-top: 8px;
}

.final-prompt-card {
  margin-top: 8px;
}

/* 提示词代码显示框样式 */
.prompt-code-display {
  margin: 0;
  padding: 12px;
  background: rgba(250, 250, 252, 0.8);
  border: 1px solid rgba(24, 160, 88, 0.15);
  border-radius: 6px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #333;
  white-space: pre-wrap;
  word-wrap: break-word;
  word-break: break-word;
  overflow-wrap: break-word;
  max-height: 500px;
  overflow-y: auto;
}

.prompt-code-display::-webkit-scrollbar {
  width: 4px;
}

.prompt-code-display::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.15);
  border-radius: 2px;
}

html[data-theme="dark"] .prompt-code-display {
  background: #1e1e1e;
  border-color: #3a3a3a;
  color: #d4d4d4;
}

.save-hint {
  margin-top: 8px;
}

.input-container {
  padding: 12px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  background: rgba(255, 255, 255, 0.95);
  flex-shrink: 0;
  z-index: 10;
  backdrop-filter: blur(8px);
  width: 100%;
  box-sizing: border-box;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.04);
}


.templates-grid {
  max-height: 450px;
  overflow-y: auto;
}

.templates-grid::-webkit-scrollbar {
  width: 4px;
}

.templates-grid::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.15);
  border-radius: 2px;
}

.template-card {
  cursor: pointer;
  transition: all 0.2s ease;
  background: rgba(250, 250, 252, 0.5);
}

.template-card:hover {
  background: rgba(24, 160, 88, 0.05);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
}

.template-meta {
  margin-top: 6px;
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

/* Markdown渲染样式 */
.message-text :deep(h1) {
  font-size: 1.3em;
  font-weight: 600;
  padding-bottom: 0.2em;
  margin-top: 0.6em;
  margin-bottom: 0.4em;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}

.message-text :deep(h2) {
  font-size: 1.2em;
  font-weight: 600;
  padding-bottom: 0.2em;
  margin-top: 0.5em;
  margin-bottom: 0.3em;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.message-text :deep(h3) {
  font-size: 1.1em;
  font-weight: 600;
  margin-top: 0.5em;
  margin-bottom: 0.3em;
}

.message-text :deep(h4),
.message-text :deep(h5),
.message-text :deep(h6) {
  font-size: 1.05em;
  font-weight: 600;
  margin-top: 0.4em;
  margin-bottom: 0.2em;
}

.message-text :deep(h1:first-child),
.message-text :deep(h2:first-child),
.message-text :deep(h3:first-child),
.message-text :deep(h4:first-child),
.message-text :deep(h5:first-child),
.message-text :deep(h6:first-child) {
  margin-top: 0;
}

.message-text :deep(p) {
  margin-top: 0.2em;
  margin-bottom: 0.2em;
  line-height: 1.6;
}

.message-text :deep(p:first-child) {
  margin-top: 0;
}

.message-text :deep(p:last-child) {
  margin-bottom: 0;
}

.message-text :deep(ul),
.message-text :deep(ol) {
  padding-left: 1.8em;
  margin-top: 0.4em;
  margin-bottom: 0.6em;
}

.message-text :deep(ul) {
  list-style-type: disc;
}

.message-text :deep(ol) {
  list-style-type: decimal;
}

.message-text :deep(li) {
  margin-top: 0.5em;
  margin-bottom: 0.5em;
}

.message-text :deep(ul) {
  list-style-type: disc;
}

.message-text :deep(ol) {
  list-style-type: decimal;
}

.message-text :deep(li) {
  margin-bottom: 0.5em;
}

.message-text :deep(code) {
  background-color: rgba(0, 0, 0, 0.08);
  padding: 3px 6px;
  border-radius: 5px;
  font-family: Consolas, Monaco, 'Andale Mono', 'Ubuntu Mono', monospace;
  font-size: 0.9em;
}

.message-text :deep(pre) {
  background-color: rgba(0, 0, 0, 0.1);
  padding: 1em;
  border-radius: 8px;
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow-x: auto;
  margin: 0.5em 0;
}

.message-text :deep(pre code) {
  background-color: transparent;
  padding: 0;
}

.message-text :deep(blockquote) {
  border-left: 3px solid var(--n-primary-color);
  padding-left: 12px;
  margin: 0.5em 0;
  color: var(--n-text-color-depth-2);
}

.message-text :deep(a) {
  color: var(--n-primary-color);
  text-decoration: none;
}

.message-text :deep(a:hover) {
  text-decoration: underline;
}

.message-text :deep(table) {
  display: block;
  overflow-x: auto;
  white-space: nowrap;
  margin-top: 1em;
  margin-bottom: 1em;
  width: 100%;
  border-collapse: collapse;
  border-spacing: 0;
  font-size: 0.9em;
}

.message-text :deep(th),
.message-text :deep(td) {
  border: 1px solid var(--n-border-color, #e0e0e6);
  padding: 10px 14px;
  text-align: left;
}

.message-text :deep(th) {
  font-weight: 600;
  background-color: var(--n-color-hover, #f6f6f7);
}

.message-text :deep(tbody tr:nth-child(even)) {
  background-color: #fcfcfc;
}

.message-text :deep(hr) {
  margin-top: 25px;
  margin-bottom: 25px;
  border: none;
  height: 3px;
  background-color: var(--n-border-color, #e0e0e6);
}
</style>
