<template>
  <AppPage class="aigc-chat-wrapper">
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
            <div v-if="selectedResources.length" class="resource-attachments">
              <n-space align="center" :size="8" wrap>
                <span class="resource-attachments__label">已附加教学资源:</span>
                <n-tag
                  v-for="item in selectedResources"
                  :key="item.id"
                  size="small"
                  closable
                  @close="removeSelectedResource(item.id)"
                >
                  <template #icon>
                    <n-icon><Icon icon="ant-design:file-outlined" /></n-icon>
                  </template>
                  {{ item.title }}
                </n-tag>
                <n-button size="tiny" text type="primary" @click="clearSelectedResources">
                  清空
                </n-button>
              </n-space>
            </div>
          </div>
        </div>

        <div class="sidebar">
          <n-card title="📜 生成历史" size="small">
            <div v-if="chatHistory.length === 0" class="empty-history">
              <n-empty size="small" description="暂无历史记录">
                <template #icon>
                  <n-icon size="48">
                    <Icon icon="ant-design:file-text-outlined" />
                  </n-icon>
                </template>
              </n-empty>
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
              <n-button size="small" text type="primary" @click="showAllHistory">
                查看全部 →
              </n-button>
            </template>
          </n-card>

          <n-card title="⚙️ 上下文配置" size="small">
            <n-space vertical :size="8">
              <n-select
                v-model:value="selectedCourseId"
                :options="courseOptions"
                placeholder="选择课程"
                clearable
                filterable
                size="small"
                @update:value="handleCourseChange"
              />
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
                placeholder="选择章节"
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
              <n-switch v-model:value="enableWebSearch" size="small">
                <template #checked>启用联网搜索</template>
                <template #unchecked>启用联网搜索</template>
              </n-switch>
            </n-space>
          </n-card>

          <n-card title="⚡ 快捷操作" size="small">
            <n-space vertical :size="6">
              <n-button size="small" block secondary @click="openResourceSelector">
                <template #icon><n-icon><Icon icon="ant-design:folder-open-outlined" /></n-icon></template>
                教学资源
              </n-button>
              <n-button size="small" block secondary @click="showCaseLibrary">
                <template #icon><n-icon><Icon icon="ant-design:library-outlined" /></n-icon></template>
                案例库
              </n-button>
              <n-button size="small" block secondary @click="showPromptTemplates">
                <template #icon><n-icon><Icon icon="ant-design:book-outlined" /></n-icon></template>
                随机加载模板
              </n-button>
              <n-button size="small" block secondary @click="exportCurrentChat">
                <template #icon><n-icon><Icon icon="ant-design:export-outlined" /></n-icon></template>
                导出对话
              </n-button>
            </n-space>
          </n-card>
        </div>
      </div>
    </div>
    
    <!-- 教学资源选择 -->
    <n-modal
      v-model:show="resourceSelectorVisible"
      preset="card"
      title="选择教学资源"
      style="width: 980px; max-width: 94vw"
    >
      <n-space vertical :size="12">
        <n-card size="small">
          <n-space class="resource-search-bar" :size="12" align="center" wrap>
            <n-input
              v-model:value="resourceSearchForm.keyword"
              placeholder="关键词"
              size="small"
              @keyup.enter="fetchResourceList"
            />
            <n-select
              v-model:value="resourceSearchForm.resource_type"
              :options="resourceTypeOptions"
              placeholder="资源类型"
              size="small"
            />
            <n-select
              v-model:value="resourceSearchForm.chapter_id"
              :options="chapterOptions"
              placeholder="章节"
              size="small"
            />
            <n-select
              v-model:value="resourceSearchForm.theme_category_id"
              :options="themeOptions"
              placeholder="思政主题"
              size="small"
            />
            <n-button size="small" type="primary" @click="fetchResourceList">
              搜索
            </n-button>
            <n-button size="small" @click="resetResourceSearch">
              重置
            </n-button>
          </n-space>
        </n-card>

        <n-data-table
          :loading="resourceLoading"
          :columns="resourceColumns"
          :data="resourceList"
          :row-key="row => row.id"
          :checked-row-keys="selectedResourceIds"
          @update:checked-row-keys="handleResourceSelection"
        />

        <n-space justify="space-between" align="center">
          <n-pagination
            v-model:page="resourcePagination.page"
            v-model:page-size="resourcePagination.pageSize"
            :item-count="resourcePagination.itemCount"
            :page-sizes="resourcePagination.pageSizes"
            show-size-picker
            @update:page="fetchResourceList"
            @update:page-size="handleResourcePageSizeChange"
          />
          <n-space>
            <n-button size="small" @click="clearSelectedResources">
              清空选择
            </n-button>
            <n-button size="small" type="primary" :loading="resourceApplying" @click="applySelectedResources">
              使用选中资源
            </n-button>
          </n-space>
        </n-space>

        <div v-if="selectedResources.length" class="selected-resources">
          <n-space>
            <n-tag v-for="item in selectedResources" :key="item.id" size="small" closable @close="removeSelectedResource(item.id)">
              {{ item.title }}
            </n-tag>
          </n-space>
        </div>
      </n-space>
    </n-modal>

    <!-- 保存案例模态框 -->
    <n-modal
      v-model:show="saveCaseVisible"
      preset="dialog"
      title="💾 保存为案例"
      positive-text="保存"
      negative-text="取消"
      @positive-click="confirmSaveCase"
      :style="{
        width: '900px',
        maxWidth: '92vw'
      }"
      class="save-case-modal"
    >
      <n-spin :show="extractingCaseFields">
        <n-form class="case-form-wrap" :model="caseForm" label-placement="top" label-width="auto">
          <n-form-item label="案例标题" required>
            <n-input v-model:value="caseForm.title" placeholder="请输入案例标题" />
          </n-form-item>
          
          <n-grid :cols="2" :x-gap="16">
            <n-gi>
              <n-form-item label="软件工程章节" required>
                <n-select
                  v-model:value="caseForm.chapter_id"
                  :options="chapterOptions"
                  placeholder="请选择章节"
                  filterable
                />
              </n-form-item>
            </n-gi>
            
            <n-gi>
              <n-form-item label="思政主题" required>
                <n-select
                  v-model:value="caseForm.theme_category_id"
                  :options="themeOptions"
                  placeholder="请选择思政主题"
                  filterable
                />
              </n-form-item>
            </n-gi>
          </n-grid>
          
          <n-grid :cols="2" :x-gap="16">
            <n-gi>
              <n-form-item label="案例类型" required>
                <n-select
                  v-model:value="caseForm.case_type"
                  :options="caseTypeOptions"
                  placeholder="请选择案例类型"
                />
              </n-form-item>
            </n-gi>
            
            <n-gi>
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
            </n-gi>
          </n-grid>
          
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
              :autosize="{ minRows: 4, maxRows: 10 }"
            />
          </n-form-item>
        </n-form>
      </n-spin>
    </n-modal>

    <!-- 生成历史弹窗 -->
    <n-modal v-model:show="historyModalVisible" preset="card" title="生成历史" style="width: 720px; max-width: 92vw">
      <div v-if="chatHistory.length === 0" class="history-modal-empty">
        <n-empty size="small" description="暂无历史记录" />
      </div>
      <div v-else class="history-modal-list">
        <div
          v-for="session in chatHistory"
          :key="session.id"
          class="history-modal-item"
          @click="handleHistorySelect(session.id)"
        >
          <div class="history-modal-title">{{ session.title }}</div>
          <div class="history-modal-preview">{{ getHistoryPreview(session) }}</div>
          <div class="history-modal-time">{{ formatTime(session.createdAt) }}</div>
        </div>
      </div>
    </n-modal>
  </AppPage>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
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
  NGrid,
  NGi,
  NDataTable,
  NPagination,
  NTag,
  useMessage,
  useLoadingBar,
} from 'naive-ui'
import { Icon } from '@iconify/vue'
import AppPage from '@/components/page/AppPage.vue'
import ChatContainer from '@/components/chat/ChatContainer.vue'
import ChatInput from '@/components/chat/ChatInput.vue'
import { chatAPI, chatStream } from '@/api/aigc'
import { createGenerationHistory } from '@/api/aigc-history'
import { request } from '@/utils/http'
import api from '@/api'
import { templatesApi, themeCategoriesApi, resourcesApi } from '@/api/ideological'
import { useUserStore } from '@/store'

// 响应式数据
const message = useMessage()
const loadingBar = useLoadingBar()
const router = useRouter()
const chatContainer = ref()
const chatInput = ref()
const userStore = useUserStore()

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
const courseOptions = ref([])
const selectedCourseId = ref(null)
const selectedTemplateId = ref(null)
const chapterOptionsRich = ref([])
const selectedChapterId = ref(null)
const chapterMap = ref({})
const selectedTheme = ref(null)
const selectedCaseType = ref(null)
const extractingCaseFields = ref(false)
const autoAttachResources = ref(true)
const enableWebSearch = ref(false)

// 教学资源选择
const resourceSelectorVisible = ref(false)
const resourceLoading = ref(false)
const resourceApplying = ref(false)
const resourceList = ref([])
const resourceTypeOptions = ref([])
const selectedResourceIds = ref([])
const selectedResourceMap = reactive(new Map())
const resourceContextText = ref('')
const resourcePagination = reactive({
  page: 1,
  pageSize: 8,
  itemCount: 0,
  pageSizes: [8, 12, 20],
})
const resourceSearchForm = reactive({
  keyword: '',
  resource_type: null,
  software_engineering_chapter: null,
  course_id: null,
  chapter_id: null,
  theme_category_id: null,
})

// 保存案例相关
const saveCaseVisible = ref(false)
const currentSaveMessage = ref(null)
const historyModalVisible = ref(false)
const caseForm = reactive({
  title: '',
  software_engineering_chapter: '',
  course_id: null,
  chapter_id: null,
  theme_category_id: null,
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

// 有效的case_type枚举值集合
const validCaseTypeValues = new Set(caseTypeOptions.map(opt => opt.value))

const resourceColumns = [
  {
    type: 'selection',
  },
  {
    title: '标题',
    key: 'title',
    ellipsis: { tooltip: true },
  },
  {
    title: '类型',
    key: 'resource_type',
    width: 120,
    render: (row) => getResourceTypeLabel(row.resource_type),
  },
  {
    title: '章节',
    key: 'software_engineering_chapter',
    width: 160,
    ellipsis: { tooltip: true },
  },
  {
    title: '思政主题',
    key: 'theme_category_id',
    width: 140,
    render: (row) => resolveThemeLabel(row.theme_category_id),
  },
]

// 验证并映射case_type，如果无效则返回null
function validateCaseType(type) {
  if (!type) return null
  // 如果已经是有效的枚举值，直接返回
  if (validCaseTypeValues.has(type)) return type
  // 尝试根据label匹配
  const matched = caseTypeOptions.find(opt => opt.label === type)
  if (matched) return matched.value
  // 尝试模糊匹配
  const lowerType = type.toLowerCase()
  if (lowerType.includes('案例') || lowerType.includes('case')) return 'case_study'
  if (lowerType.includes('讨论')) return 'discussion'
  if (lowerType.includes('思考')) return 'thinking'
  if (lowerType.includes('示例')) return 'example'
  if (lowerType.includes('实践') || lowerType.includes('项目') || lowerType.includes('practice')) return 'practice'
  return null
}

const selectedResources = computed(() => Array.from(selectedResourceMap.values()))

// 处理发送消息
async function handleSendMessage(data) {
  // 防止竞态条件：如果正在生成中，忽略新的请求
  if (isGenerating.value) {
    message.warning('正在生成中，请稍候...')
    return
  }

  const userMessage = {
    id: Date.now(),
    role: 'user',
    content: data.content,
    attachments: data.attachments,
    timestamp: new Date().toISOString(),
    avatar: userStore.avatar || '',
  }

  messages.value.push(userMessage)
  isGenerating.value = true
  loadingBar.start()

  try {
    // 已禁用自动引用资源功能
    // await maybeAutoAttachResources()
    
    // 如果有附加的教学资源，在用户消息内容中添加资源信息提示
    let userContentWithResources = data.content
    if (selectedResources.value.length > 0) {
      const resourceTitles = selectedResources.value.map(r => r.title).join('、')
      userContentWithResources = `${data.content}\n\n[已附加教学资源: ${resourceTitles}]`
      // 更新用户消息的显示内容
      userMessage.content = userContentWithResources
    }
    const hasExternalResource = selectedResources.value.some((r) => r?.external_url)
    const effectiveEnableWebSearch = enableWebSearch.value || hasExternalResource
    
    const formatGuide = '请使用标准 Markdown 输出（段落 + 有序/无序列表），段落之间空一行；允许少量小标题，用“**小标题：**”行内加粗即可，不要用多级 # 标题；禁止使用表格；避免整段加粗。'
    const msgArr = [
      { role: 'system', content: 'You are a helpful assistant.' },
      { role: 'system', content: formatGuide },
      ...(resourceContextText.value ? [{ role: 'system', content: resourceContextText.value }] : []),
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
    const iterator = chatStream(msgArr, { enableWebSearch: effectiveEnableWebSearch })
    try {
      for await (const item of iterator) {
        // item is { type: 'chunk'|'text', payload: ... }
        if (item && item.type === 'chunk' && item.payload) {
          const obj = item.payload
          if (obj && obj.type === 'content') {
            const chunkText = obj.content ?? ''
            // Preserve whitespace/newlines: do NOT trim.
            if (typeof chunkText === 'string' && chunkText.length > 0) {
              assistantMessage.content += chunkText
              messages.value = [...messages.value]
              await nextTick()
              chatContainer.value?.scrollToBottom()
            }
          } else if (obj && obj.type === 'done') {
            break
          } else if (obj && (obj.type === 'error' || obj.error)) {
            throw new Error(obj.error || 'Stream error')
          }
        } else if (item && item.type === 'text') {
          // Fallback: append raw text as-is
          const rawText = String(item.payload || '')
          if (rawText.length > 0) {
            assistantMessage.content += rawText
            messages.value = [...messages.value]
            await nextTick()
            chatContainer.value?.scrollToBottom()
          }
        }
      }
      // stream finished
      assistantMessage.isStreaming = false
      loadingBar.finish()
      todayGenerated.value++
      totalCases.value++
      
      await saveGenerationHistory(userMessage.content, assistantMessage.content, assistantMessage)
      
      saveToHistory()
    } catch (streamErr) {
      console.error('Stream error, falling back to non-streaming:', streamErr)
      // remove streaming placeholder
      const idx = messages.value.findIndex((m) => m.id === assistantMessage.id)
      if (idx >= 0) messages.value.splice(idx, 1)
      // fallback to non-streaming API
      const res = await chatAPI(msgArr, { enableWebSearch: effectiveEnableWebSearch })
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
      
      await saveGenerationHistory(userMessage.content, finalReply, fallbackMessage)
      
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
    const chapter = chapterMap.value[selectedChapterId.value]
    const historyData = {
      user_input: userInput,
      generated_content: generatedContent,
      generation_type: 'aigc_chat',
      software_engineering_chapter: chapter?.name || null,
      course_id: selectedCourseId.value,
      chapter_id: selectedChapterId.value,
      theme_category_id: selectedTheme.value,
    }
    const response = await createGenerationHistory(historyData)
    const data = response?.data || response || {}
    if (data && data.id) {
      messageObj.historyId = data.id
      return
    }
    messageObj.historyId = Date.now()
  } catch (error) {
    console.error('保存生成历史失败:', error)
    // 即使失败也分配一个临时ID，确保功能可用
    messageObj.historyId = Date.now()
  }
}

// 保存案例
async function handleSaveCase(messageObj) {
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
    course_id: selectedCourseId.value,
    chapter_id: selectedChapterId.value,
    theme_category_id: null,
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

  // 先展示弹窗，再异步填充字段（AI优先，正则兜底）
  saveCaseVisible.value = true
  extractingCaseFields.value = true
  autoFillCaseForm(messageObj.content || '')
    .catch((err) => console.error('自动填充案例字段失败:', err))
    .finally(() => {
      extractingCaseFields.value = false
    })
}

async function autoFillCaseForm(content) {
  const normalized = content.replace(/\r\n/g, '\n')

  const matchField = (labels) => {
    for (const label of labels) {
      const reg = new RegExp(`${label}\\s*[:：]\\s*([^\\n]+)`, 'i')
      const m = normalized.match(reg)
      if (m && m[1]) return m[1].trim()
    }
    return ''
  }

  // 先用本地解析兜底
  const extracted = autoExtractCaseMetadata(content || '')

  const explicitTitle = matchField(['案例标题', '标题', '案例名称'])
  if (explicitTitle) caseForm.title = explicitTitle

  const chapter = matchField(['软件工程章节', '章节'])
  if (chapter) applyCaseChapter(chapter)

  const theme = matchField(['思政主题', '主题'])
  if (theme) {
    // 查找匹配的主题ID
    const matchedTheme = themeOptions.value.find(opt => opt.label === theme)
    if (matchedTheme) caseForm.theme_category_id = matchedTheme.value
  }

  const type = matchField(['案例类型'])
  if (type) {
    const validType = validateCaseType(type)
    if (validType) caseForm.case_type = validType
  }

  const level = matchField(['难度等级', '难度'])
  if (level) {
    const levelNum = parseInt(level, 10)
    if (!isNaN(levelNum)) caseForm.difficulty_level = levelNum
  }

  if (extracted.tags.length) caseForm.tags = extracted.tags
  if (extracted.keyPoints.length) caseForm.key_points = extracted.keyPoints
  if (extracted.discussionQuestions.length) caseForm.discussion_questions = extracted.discussionQuestions

  const teachingMatch = normalized.match(/教学建议\s*[:：]?\s*([\s\S]*?)(\n\s*\n|$)/i)
  if (teachingMatch && teachingMatch[1].trim()) {
    caseForm.teaching_suggestions = teachingMatch[1].trim()
  }

  // 再尝试 AI 结构化提取，成功则覆盖（用户可修改）
  const aiData = await aiExtractCaseMetadata(content)
  if (aiData) {
    caseForm.title = aiData.title || caseForm.title
    const incomingChapter =
      aiData.software_engineering_chapter || aiData.chapter || caseForm.software_engineering_chapter
    if (incomingChapter) applyCaseChapter(incomingChapter)
    // 如果AI返回了主题名称，查找对应的ID
    const themeName = aiData.ideological_theme || aiData.theme
    if (themeName) {
      const matchedTheme = themeOptions.value.find(opt => opt.label === themeName)
      if (matchedTheme) caseForm.theme_category_id = matchedTheme.value
    }
    const validAiCaseType = validateCaseType(aiData.case_type)
    if (validAiCaseType) caseForm.case_type = validAiCaseType
    if (aiData.difficulty_level) caseForm.difficulty_level = aiData.difficulty_level
    if (Array.isArray(aiData.tags) && aiData.tags.length) caseForm.tags = aiData.tags
    if (Array.isArray(aiData.key_points) && aiData.key_points.length) caseForm.key_points = aiData.key_points
    if (Array.isArray(aiData.discussion_questions) && aiData.discussion_questions.length) {
      caseForm.discussion_questions = aiData.discussion_questions
    }
    if (aiData.teaching_suggestions) caseForm.teaching_suggestions = aiData.teaching_suggestions
  }
}

function autoExtractCaseMetadata(content) {
  // 预清洗，统一分隔符
  const normalized = content
    .replace(/\r\n/g, '\n')
    .replace(/：/g, ':')
    .replace(/。/g, '。\n') // 句号后换行，方便分块

  const cleanListItems = (block) =>
    block
      .split('\n')
      .map((line) => line.replace(/^[\s>*\-•·\d\)\.]+\s*/, '').trim())
      .filter(Boolean)
      .slice(0, 8)

  const extractListByHeading = (headings) => {
    for (const heading of headings) {
      const reg = new RegExp(`${heading}\\s*[:：]?\\s*([\\s\\S]*?)(\\n\\s*\\n|$)`, 'i')
      const match = normalized.match(reg)
      if (match && match[1]) {
        const items = cleanListItems(match[1])
        if (items.length) return items
      }
    }

    const lines = normalized.split('\n')
    for (let i = 0; i < lines.length; i++) {
      if (headings.some((h) => lines[i].includes(h))) {
        const block = lines.slice(i + 1, i + 6).join('\n')
        const items = cleanListItems(block)
        if (items.length) return items
      }
    }

    // 回退：尝试从 markdown 子标题中提取
    for (let i = 0; i < lines.length; i++) {
      if (/^#+\s*/.test(lines[i]) && headings.some((h) => lines[i].includes(h))) {
        const block = lines.slice(i + 1, i + 6).join('\n')
        const items = cleanListItems(block)
        if (items.length) return items
      }
    }
    return []
  }

  const extractTags = () => {
    const tagMatch =
      normalized.match(/标签[:：]\s*([^\n]+)/i) ||
      normalized.match(/关键词[:：]\s*([^\n]+)/i) ||
      normalized.match(/关键标签[:：]\s*([^\n]+)/i)
    if (tagMatch) {
      return [...new Set(tagMatch[1].split(/[、，,;；\s]+/).map((t) => t.trim()).filter(Boolean))].slice(0, 8)
    }

    // 回退：基于常见关键词快速抓取
    const candidates = []
    ;['主题', '价值', '知识点', '技术'].forEach((key) => {
      const m = normalized.match(new RegExp(`${key}[:：]\\s*([^\\n]+)`, 'i'))
      if (m && m[1]) {
        candidates.push(...m[1].split(/[、，,;；\s]+/))
      }
    })
    return [...new Set(candidates.map((t) => t.trim()).filter(Boolean))].slice(0, 8)
  }

  return {
    discussionQuestions: extractListByHeading([
      '讨论思考',
      '讨论问题',
      '讨论题',
      '思考题',
      '讨论',
      '课堂讨论',
    ]),
    keyPoints: extractListByHeading(['关键知识点', '知识点', '要点', '学习要点', '核心技术内容']),
    tags: extractTags(),
  }
}

async function aiExtractCaseMetadata(content) {
  if (!content || content.trim().length === 0) return null
  try {
    const systemPrompt =
      '你是一名教学案例助理。请严格输出 JSON，不要包含说明文字。字段：title, software_engineering_chapter, ideological_theme, case_type, difficulty_level (整数), tags(array), key_points(array), discussion_questions(array), teaching_suggestions(string)。确保 JSON 可被直接解析。'
    const userPrompt = `请从下面的思政教学案例文本中提取结构化字段，按字段输出 JSON。文本如下：\n${content}`
    const res = await chatAPI([
      { role: 'system', content: systemPrompt },
      { role: 'user', content: userPrompt },
    ])
    const reply =
      res?.reply ||
      res?.data?.reply ||
      res?.data?.choices?.[0]?.message?.content ||
      res?.choices?.[0]?.message?.content ||
      ''
    if (!reply) return null
    const jsonText = extractJson(reply)
    return JSON.parse(jsonText)
  } catch (err) {
    console.warn('AI 提取案例字段失败，使用兜底解析', err)
    return null
  }
}

function extractJson(text) {
  // 如果本身就是 JSON
  const trimmed = text.trim()
  if (trimmed.startsWith('{') && trimmed.endsWith('}')) return trimmed
  // 尝试从代码块中提取
  const codeBlockMatch = text.match(/```json\s*([\s\S]*?)```/i) || text.match(/```([\s\S]*?)```/)
  if (codeBlockMatch) return codeBlockMatch[1]
  // 兜底返回原文
  return text
}

// 确认保存案例
async function confirmSaveCase() {
  return new Promise(async (resolve, reject) => {
    try {
      // 验证必填字段
      if (!caseForm.title || !(caseForm.chapter_id || caseForm.software_engineering_chapter) || !caseForm.theme_category_id) {
        message.error('请填写所有必填项')
        reject(new Error('缺少必填项'))
        return
      }
      const chapter = chapterMap.value[caseForm.chapter_id]
      const chapterName = chapter?.name || caseForm.software_engineering_chapter
      const courseId = caseForm.course_id || chapter?.course_id || selectedCourseId.value
      
      const caseData = {
        title: caseForm.title.trim(),
        content: currentSaveMessage.value.content, // 直接使用消息内容
        software_engineering_chapter: chapterName,
        course_id: courseId,
        chapter_id: caseForm.chapter_id,
        theme_category_id: caseForm.theme_category_id,
        case_type: caseForm.case_type || 'case_study',
        tags: caseForm.tags || [],
        key_points: caseForm.key_points || [],
        discussion_questions: caseForm.discussion_questions || [],
        teaching_suggestions: caseForm.teaching_suggestions || '',
        difficulty_level: caseForm.difficulty_level || 3,
        is_public: true, // 默认公开
        status: 'published', // 直接发布，不需要审核
      }
      
      // 直接调用创建案例的API
      const response = await request.post('/ideological/cases/', caseData)
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

// 清空当前对话
function handleClearHistory() {
  messages.value = []
  currentSessionId.value = null
  const userId = userStore.id || userStore.userInfo?.id
  const messagesKey = `aigc-chat-current-messages-${userId}`
  localStorage.removeItem(messagesKey)
}

// 清空所有历史记录
function clearAllHistory() {
  dialog.warning({
    title: '确认清空',
    content: '确定要清空所有生成历史吗？此操作不可恢复。',
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: () => {
      chatHistory.value = []
      localStorage.removeItem('aigc-chat-history')
      message.success('已清空所有历史记录')
    }
  })
}

// 保存到历史记录
function saveToHistory() {
  if (messages.value.length >= 2) {
    // 每次生成都创建新的会话ID，避免覆盖旧的历史记录
    const sessionId = Date.now()
    
    // 找到最后一条用户消息作为标题
    const lastUserMessage = [...messages.value].reverse().find(m => m.role === 'user')
    const title = lastUserMessage 
      ? lastUserMessage.content.substring(0, 30) + (lastUserMessage.content.length > 30 ? '...' : '')
      : '新对话'
    
    const session = {
      id: sessionId,
      title: title,
      // store plain objects (avoid reactive proxies)
      messages: messages.value.map((m) => ({ ...m })),
      createdAt: new Date().toISOString(),
    }

    // 总是添加为新的历史记录
    chatHistory.value.unshift(session)

    currentSessionId.value = sessionId

    // 限制历史记录数量
    if (chatHistory.value.length > 20) {
      chatHistory.value = chatHistory.value.slice(0, 20)
    }
    
    // 生成完成后重置sessionId，下次发送会创建新会话
    currentSessionId.value = null
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
  router.push({ path: '/aigc/cases' })
}

// 随机加载提示词模板
function showPromptTemplates() {
  if (templateOptions.value.length === 0) {
    message.warning('暂无可用的提示词模板')
    return
  }
  // 随机选择一个模板
  const randomIndex = Math.floor(Math.random() * templateOptions.value.length)
  const randomTemplate = templateOptions.value[randomIndex]
  selectedTemplateId.value = randomTemplate.value
  applyPromptPreset()
  message.success(`已随机加载模板: ${randomTemplate.label}`)
}

// 导出当前对话
function exportCurrentChat() {
  chatContainer.value?.exportChat()
}

// 显示全部历史
function showAllHistory() {
  historyModalVisible.value = true
}

function handleHistorySelect(sessionId) {
  loadSession(sessionId)
  historyModalVisible.value = false
}

function getHistoryPreview(session) {
  const list = Array.isArray(session?.messages) ? session.messages : []
  if (list.length === 0) return '暂无内容'
  const last = list[list.length - 1]
  const text = String(last?.content || '').replace(/\s+/g, ' ').trim()
  return text || '暂无内容'
}

async function fetchCourseOptions() {
  try {
    const res = await api.getAllCourses(true)
    const courses = res?.data || res || []
    courseOptions.value = courses.map((item) => ({
      label: item.name,
      value: item.id,
    }))
    if (!selectedCourseId.value && courseOptions.value.length > 0) {
      selectedCourseId.value = courseOptions.value[0].value
    }
  } catch (error) {
    courseOptions.value = []
  }
}

async function fetchChapterOptions(courseId) {
  if (!courseId) {
    chapterOptionsRich.value = []
    chapterOptions.value = []
    chapterMap.value = {}
    return
  }
  try {
    const res = await api.getChaptersByCourse(courseId)
    const chapters = res?.data || res || []
    chapterOptionsRich.value = chapters.map((c) => ({
      label: c.name,
      value: c.id,
      desc: c.description,
    }))
    chapterOptions.value = chapters.map((c) => ({
      label: c.name,
      value: c.id,
    }))
    chapterMap.value = Object.fromEntries(chapters.map((c) => [c.id, c]))
  } catch (error) {
    chapterOptionsRich.value = []
    chapterOptions.value = []
    chapterMap.value = {}
  }
}

function handleCourseChange(value) {
  selectedCourseId.value = value
  selectedChapterId.value = null
  resourceSearchForm.course_id = value
  resourceSearchForm.chapter_id = null
  resourceSearchForm.software_engineering_chapter = null
  fetchChapterOptions(value)
}

// 获取选项数据
async function fetchOptions() {
  await fetchCourseOptions()
  await fetchChapterOptions(selectedCourseId.value)
  resourceSearchForm.course_id = selectedCourseId.value
  resourceSearchForm.software_engineering_chapter = null

  try {
    const response = await themeCategoriesApi.getList()
  // 响应可能被多次包装
  let themesResponse = response?.data?.data || response?.data || response
  // 确保是数组
  if (!Array.isArray(themesResponse)) {
    console.error('❗ [Chat] 主题数据不是数组')
      throw new Error('主题数据格式错误')
    }
    
    // 只使用启用的二级分类
    themeOptions.value = themesResponse
      .filter(item => item.is_active && item.parent_id !== null)
      .map(item => ({
        label: item.name,
        value: item.id,  // 使用ID作为值
      }))
    
  } catch (error) {
    console.error('❗ [Chat] 获取主题选项失败:', error)
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
    const themeLabel = resolveThemeLabel(selectedTheme.value)
    parts.push(`思政主题：${themeLabel || selectedTheme.value}`)
  }
  if (selectedCaseType.value) {
    const caseLabel = caseTypeOptions.find((c) => c.value === selectedCaseType.value)?.label || selectedCaseType.value
    parts.push(`案例类型：${caseLabel}`)
  }

  chatInput.value?.setContent(parts.filter(Boolean).join('\n'))
}

function applyCaseChapter(chapterName) {
  if (!chapterName) return
  caseForm.software_engineering_chapter = chapterName
  const matched = chapterOptionsRich.value.find((item) => item.label === chapterName)
  if (matched) {
    caseForm.chapter_id = matched.value
    if (!caseForm.course_id && chapterMap.value[matched.value]) {
      caseForm.course_id = chapterMap.value[matched.value].course_id
    }
  }
}

function openResourceSelector() {
  resourceSelectorVisible.value = true
  const chapter = chapterMap.value[selectedChapterId.value]
  resourceSearchForm.software_engineering_chapter = chapter?.name || null
  resourceSearchForm.course_id = selectedCourseId.value
  resourceSearchForm.chapter_id = selectedChapterId.value
  if (resourceTypeOptions.value.length === 0) {
    fetchResourceTypes()
  }
  fetchResourceList()
}

async function fetchResourceTypes() {
  try {
    const res = await resourcesApi.getTypes()
    resourceTypeOptions.value = normalizeResourceTypeOptions(res?.data || res)
  } catch (error) {
    resourceTypeOptions.value = normalizeResourceTypeOptions()
  }
}

function normalizeResourceTypeOptions(input) {
  const defaults = [
    { label: '文档', value: 'document' },
    { label: '视频', value: 'video' },
    { label: '音频', value: 'audio' },
    { label: '图片', value: 'image' },
    { label: '演示文稿', value: 'presentation' },
    { label: '虚拟仿真', value: 'simulation' },
    { label: '外部链接', value: 'link' },
    { label: '其他', value: 'other' },
  ]

  if (!input) return defaults
  if (Array.isArray(input)) {
    if (input.length === 0) return defaults
    if (typeof input[0] === 'string') {
      return input.map((v) => ({ label: v, value: v }))
    }
    if (typeof input[0] === 'object') {
      return input.map((v) => ({
        label: v.label || v.name || v.value || '未知类型',
        value: v.value || v.name || v.label || 'other',
      }))
    }
  }
  return defaults
}

function getResourceTypeLabel(type) {
  const list = Array.isArray(resourceTypeOptions.value) ? resourceTypeOptions.value : []
  const option = list.find((item) => item?.value === type)
  return option ? option.label : type || '未知类型'
}

function resolveThemeLabel(themeId) {
  if (!themeId) return ''
  const option = themeOptions.value.find((item) => item.value === themeId)
  return option ? option.label : ''
}

async function fetchResourceList() {
  resourceLoading.value = true
  try {
    const params = {
      ...resourceSearchForm,
      page: resourcePagination.page,
      page_size: resourcePagination.pageSize,
    }
    const res = await resourcesApi.getList(params)
    const data = res?.data || res || {}
    const items = data.items || []
    
    resourceList.value = items
    resourcePagination.itemCount = data.total || 0
    selectedResourceIds.value = Array.from(selectedResourceMap.keys())
    
    // 如果没有结果，给用户提示
    if (items.length === 0 && (params.course_id || params.chapter_id)) {
      message.info('当前筛选条件下没有找到资源，请尝试调整筛选条件')
    }
  } catch (error) {
    message.error('获取教学资源失败')
  } finally {
    resourceLoading.value = false
  }
}

function handleResourcePageSizeChange(pageSize) {
  resourcePagination.pageSize = pageSize
  resourcePagination.page = 1
  fetchResourceList()
}

function resetResourceSearch() {
  const chapter = chapterMap.value[selectedChapterId.value]
  Object.assign(resourceSearchForm, {
    keyword: '',
    resource_type: null,
    software_engineering_chapter: chapter?.name || null,
    course_id: selectedCourseId.value,
    chapter_id: selectedChapterId.value,
    theme_category_id: null,
  })
  resourcePagination.page = 1
  fetchResourceList()
}

function handleResourceSelection(keys) {
  selectedResourceIds.value = keys
  const currentIds = new Set(resourceList.value.map((r) => r.id))
  resourceList.value.forEach((r) => {
    if (currentIds.has(r.id) && !keys.includes(r.id)) {
      selectedResourceMap.delete(r.id)
    }
  })
  resourceList.value.forEach((r) => {
    if (keys.includes(r.id)) {
      selectedResourceMap.set(r.id, r)
    }
  })
}

function clearSelectedResources() {
  selectedResourceIds.value = []
  selectedResourceMap.clear()
  resourceContextText.value = ''
}

function removeSelectedResource(id) {
  selectedResourceMap.delete(id)
  selectedResourceIds.value = selectedResourceIds.value.filter((key) => key !== id)
  if (selectedResourceIds.value.length === 0) {
    resourceContextText.value = ''
  }
}

function resolveResourceLink(resource) {
  const url = resource?.external_url || resource?.preview_url || resource?.file_url || resource?.download_url
  if (!url) return ''
  if (url.startsWith('http')) return url
  try {
    return new URL(url, window.location.origin).href
  } catch (e) {
    return ''
  }
}

function buildResourcePrompt(resources) {
  const lines = ['参考教学资源：']
  resources.forEach((item, index) => {
    const linePrefix = `${index + 1}.`
    lines.push(`${linePrefix} 标题：${item.title || '-'}`)
    if (item.description) lines.push(`   描述：${item.description}`)
    if (item.resource_type) lines.push(`   类型：${getResourceTypeLabel(item.resource_type)}`)
    if (item.software_engineering_chapter) {
      lines.push(`   章节：${item.software_engineering_chapter}`)
    }
    const themeLabel = resolveThemeLabel(item.theme_category_id)
    if (themeLabel) lines.push(`   思政主题：${themeLabel}`)
    const link = resolveResourceLink(item)
    if (link) lines.push(`   链接：${link}`)
    if (item.external_url) {
      lines.push('   说明：该资源为外部链接，请联网访问或搜索此链接获取正文内容，再结合摘要回答。')
    }
    if (item.extractedText) {
      lines.push(`   内容摘要：${item.extractedText}`)
    }
  })
  lines.push('请结合以上教学资源内容回答。')
  return lines.join('\n')
}

async function fetchResourceExtract(resource) {
  try {
    // 文件提取可能需要较长时间，设置5分钟超时
    const res = await request.get(`/ideological/resources/${resource.id}/extract-text`, {
      params: { max_chars: 1500 },
      timeout: 300000, // 5分钟
    })
    const data = res?.data || res || {}
    return data.text || ''
  } catch (error) {
    console.error('资源文本提取失败:', error)
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      message.warning(`资源"${resource.title}"处理超时，已跳过`)
    }
    return ''
  }
}

async function applySelectedResources() {
  if (selectedResources.value.length === 0) {
    message.warning('请先选择教学资源')
    return
  }
  resourceApplying.value = true
  try {
    const items = selectedResources.value
    const extractedList = await Promise.all(items.map((item) => fetchResourceExtract(item)))
    const enriched = items.map((item, index) => ({
      ...item,
      extractedText: extractedList[index],
    }))
    const hasExternal = enriched.some((item) => item?.external_url)
    const missingCount = enriched.filter((item) => !item.extractedText).length
    if (missingCount > 0) {
      message.warning(`有 ${missingCount} 个资源未能读取内容，已仅附加基础信息`)
    }
    resourceContextText.value = buildResourcePrompt(enriched)
    if (hasExternal) {
      // 外部链接需要联网搜索，自动开启
      enableWebSearch.value = true
    }
    resourceSelectorVisible.value = false
  } finally {
    resourceApplying.value = false
  }
}

async function maybeAutoAttachResources() {
  if (!autoAttachResources.value) return
  if (selectedResources.value.length > 0 || resourceContextText.value) return
  try {
    let res = await resourcesApi.getRecommended({
      course_id: selectedCourseId.value,
      chapter_id: selectedChapterId.value,
      theme_category_id: selectedTheme.value,
      limit: 3,
    })
    let items = res?.data || res || []
    if (!Array.isArray(items) || items.length === 0) {
      const fallbackRes = await resourcesApi.getList({
        software_engineering_chapter: chapterMap.value[selectedChapterId.value]?.name || null,
        theme_category_id: selectedTheme.value,
        page: 1,
        page_size: 3,
      })
      const fallbackData = fallbackRes?.data || fallbackRes || {}
      items = fallbackData.items || []
    }
    if (!Array.isArray(items) || items.length === 0) return
    items.forEach((item) => {
      if (item && item.id) selectedResourceMap.set(item.id, item)
    })
    selectedResourceIds.value = Array.from(selectedResourceMap.keys())
    await applySelectedResources()
  } catch (error) {
    // ignore auto-attach errors
  }
}

// 组件挂载时初始化
onMounted(async () => {
  // 模拟加载统计数据
  todayGenerated.value = 3
  totalCases.value = 156
  usageTime.value = 45

  if (!userStore.avatar) {
    await userStore.getUserInfo()
  }

  // 获取选项数据
  fetchOptions()
  
  // 从localStorage加载历史记录（按用户ID区分）
  const userId = userStore.id || userStore.userInfo?.id
  const historyKey = `aigc-chat-history-${userId}`
  const savedHistory = localStorage.getItem(historyKey)
  if (savedHistory) {
    try {
      chatHistory.value = JSON.parse(savedHistory)
    } catch (e) {
      console.warn('Failed to load chat history:', e)
    }
  }

  // 从localStorage加载当前对话（按用户ID区分）
  const messagesKey = `aigc-chat-current-messages-${userId}`
  const savedMessages = localStorage.getItem(messagesKey)
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

// 监听历史记录变化，自动保存（按用户ID区分）
watch(
  chatHistory,
  (newHistory) => {
    const userId = userStore.id || userStore.userInfo?.id
    const historyKey = `aigc-chat-history-${userId}`
    localStorage.setItem(historyKey, JSON.stringify(newHistory))
  },
  { deep: true }
)

// 监听当前消息变化，自动保存（按用户ID区分）
watch(
  messages,
  (newMessages) => {
    if (newMessages.length > 0) {
      const userId = userStore.id || userStore.userInfo?.id
      const messagesKey = `aigc-chat-current-messages-${userId}`
      localStorage.setItem(messagesKey, JSON.stringify(newMessages))
    }
  },
  { deep: true }
)

watch(selectedCourseId, (value) => {
  resourceSearchForm.course_id = value
})

watch(selectedChapterId, (value) => {
  resourceSearchForm.chapter_id = value
  const chapter = chapterMap.value[value]
  resourceSearchForm.software_engineering_chapter = chapter?.name || null
})
</script>

<style scoped>
.aigc-chat-page {
  height: 100%;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  min-height: 100%;
}

:deep(.aigc-chat-wrapper) {
  padding-bottom: 0;
  overflow: hidden;
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
  gap: 12px;
  min-height: 0;
  height: 100%;
  min-height: 100%;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  height: 100%;
  max-height: none;
  min-height: 100%;
  justify-content: space-between;
  background: rgba(250, 250, 252, 0.5);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
}

.input-section {
  flex-shrink: 0;
  padding: 12px;
  background: rgba(255, 255, 255, 0.98);
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.04);
  min-height: 92px;
  margin-top: auto;
}

.resource-attachments {
  margin-top: 8px;
  padding: 8px 12px;
  border: 1px dashed var(--n-border-color);
  border-radius: 8px;
  background: var(--n-color-hover);
}

.resource-attachments__label {
  font-size: 12px;
  color: var(--n-text-color-depth-3);
}

.resource-search-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.resource-search-bar :deep(.n-input),
.resource-search-bar :deep(.n-select) {
  min-width: 160px;
  width: 180px;
}

.resource-search-bar :deep(.n-button) {
  flex: 0 0 auto;
}

.sidebar {
  width: 280px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow-y: auto;
  max-height: 100%;
}

.sidebar :deep(.n-card) {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  transition: all 0.2s ease;
}

.sidebar :deep(.n-card:hover) {
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
}

.sidebar :deep(.n-card-header) {
  padding: 12px 14px;
  font-weight: 600;
  font-size: 14px;
}

.sidebar :deep(.n-card__content) {
  padding: 10px;
}

.save-case-modal :deep(.n-dialog__title) {
  font-size: 18px;
  font-weight: 600;
}

.case-form-wrap {
  max-height: 65vh;
  overflow-y: auto;
  padding: 4px 2px;
  margin-top: 4px;
}

.case-form-wrap::-webkit-scrollbar {
  width: 4px;
}

.case-form-wrap::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.15);
  border-radius: 2px;
}

.case-form-wrap :deep(.n-form-item) {
  margin-bottom: 14px;
}

.case-form-wrap :deep(.n-form-item-label) {
  font-weight: 500;
  font-size: 13px;
  margin-bottom: 6px;
  color: var(--n-text-color-base);
}

.case-form-wrap :deep(.n-input),
.case-form-wrap :deep(.n-select),
.case-form-wrap :deep(.n-input-number) {
  border-radius: 4px;
}

.case-form-wrap :deep(.n-dynamic-tags) {
  width: 100%;
  min-height: 70px;
  padding: 10px;
  border: 1px dashed rgba(24, 160, 88, 0.25);
  border-radius: 6px;
  background: rgba(250, 250, 252, 0.5);
  transition: all 0.2s ease;
}

.case-form-wrap :deep(.n-dynamic-tags:hover) {
  border-color: rgba(24, 160, 88, 0.4);
  background: rgba(24, 160, 88, 0.03);
}

.case-form-wrap :deep(.n-dynamic-tags .n-tag) {
  margin: 3px 5px 3px 0;
  padding: 5px 10px;
  font-size: 12px;
  line-height: 1.5;
  max-width: 100%;
  word-break: break-word;
  white-space: normal;
  height: auto;
  min-height: 26px;
  display: inline-flex;
  align-items: center;
  border-radius: 4px;
  background: rgba(24, 160, 88, 0.08);
  border: 1px solid rgba(24, 160, 88, 0.15);
}

.case-form-wrap :deep(.n-dynamic-tags .n-tag .n-tag__content) {
  white-space: normal;
  word-break: break-word;
  line-height: 1.5;
  flex: 1;
}

.case-form-wrap :deep(.n-dynamic-tags .n-dynamic-tags-input) {
  margin: 3px 0;
  min-width: 120px;
  border-radius: 4px;
}

.case-form-wrap :deep(.n-dynamic-tags .n-dynamic-tags-add-button) {
  margin: 3px 0;
  border-radius: 4px;
}

.empty-history {
  text-align: center;
  padding: 20px 12px;
  color: var(--n-text-color-depth-3);
}

.empty-history :deep(.n-empty__icon) {
  font-size: 40px;
  margin-bottom: 8px;
}

.history-list {
  max-height: 300px;
  overflow-y: auto;
  padding: 2px;
}

.history-list::-webkit-scrollbar {
  width: 4px;
}

.history-list::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.15);
  border-radius: 2px;
}

.history-item {
  padding: 8px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
  margin-bottom: 6px;
  background: rgba(250, 250, 252, 0.5);
}

.history-item:hover {
  background-color: rgba(24, 160, 88, 0.05);
  border-color: rgba(24, 160, 88, 0.15);
}

.history-item.active {
  background: rgba(24, 160, 88, 0.08);
  border-color: rgba(24, 160, 88, 0.3);
}

.history-item.active .history-title {
  color: var(--n-primary-color);
  font-weight: 600;
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

.history-modal-empty {
  padding: 16px 0;
}

.history-modal-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 60vh;
  overflow-y: auto;
  padding-right: 4px;
}

.history-modal-item {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 12px;
  padding: 10px 12px;
  border: 1px solid var(--n-border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s ease, border-color 0.2s ease;
}

.history-modal-item:hover {
  background: var(--n-color-hover);
  border-color: rgba(24, 160, 88, 0.2);
}

.history-modal-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--n-text-color);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  width: 100%;
}

.history-modal-preview {
  font-size: 12px;
  color: var(--n-text-color-depth-3);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
  width: 100%;
}

.history-modal-time {
  font-size: 12px;
  color: var(--n-text-color-depth-3);
  width: 100%;
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
    width: 260px;
  }
  
  .chat-main {
    padding: 12px;
  }
}

@media (max-width: 768px) {
  .chat-layout {
    flex-direction: column;
    gap: 16px;
  }

  .sidebar {
    width: 100%;
    order: -1;
  }
  
  .chat-main {
    height: calc(100vh - 200px);
    padding: 12px;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .title-section h1 {
    font-size: 20px;
  }
  
  .case-form-wrap {
    max-height: 60vh;
  }
  
  .save-case-modal :deep(.n-dialog) {
    margin: 16px;
  }
}



/* 滚动条美化 */
* {
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 0, 0, 0.15) transparent;
}

*::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

*::-webkit-scrollbar-track {
  background: transparent;
}

*::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.15);
  border-radius: 3px;
}

*::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.25);
}
</style>
