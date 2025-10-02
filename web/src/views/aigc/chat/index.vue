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
              <n-button size="small" text @click="showAllHistory">
                查看全部
              </n-button>
            </template>
          </n-card>
          
          <n-card title="快捷操作" size="small" style="margin-top: 16px">
            <n-space vertical>
              <n-button size="small" block @click="showCaseLibrary">
                <template #icon><n-icon><Icon icon="ant-design:library-outlined" /></n-icon></template>
                案例库
              </n-button>
              
              <n-button size="small" block @click="showPromptTemplates">
                <template #icon><n-icon><Icon icon="ant-design:book-outlined" /></n-icon></template>
                提示词模板
              </n-button>
              
              <n-button size="small" block @click="exportCurrentChat">
                <template #icon><n-icon><Icon icon="ant-design:export-outlined" /></n-icon></template>
                导出对话
              </n-button>
            </n-space>
          </n-card>
        </div>
      </div>
    </div>
  </AppPage>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, watch } from 'vue'
import { NSpace, NStatistic, NCard, NEmpty, NButton, NIcon, useMessage, useLoadingBar } from 'naive-ui'
import { Icon } from '@iconify/vue'
import AppPage from '@/components/page/AppPage.vue'
import ChatContainer from '@/components/chat/ChatContainer.vue'
import ChatInput from '@/components/chat/ChatInput.vue'

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

// 处理发送消息
async function handleSendMessage(data) {
  console.log('handleSendMessage called with:', data)
  
  const userMessage = {
    id: Date.now(),
    role: 'user',
    content: data.content,
    attachments: data.attachments,
    timestamp: new Date().toISOString()
  }
  
  messages.value.push(userMessage)
  isGenerating.value = true
  loadingBar.start()
  
  console.log('User message added, messages array:', messages.value)
  
  try {
    // 模拟API调用
    await simulateAIResponse(data.content)
    
    console.log('AI response completed successfully')
    loadingBar.finish()
    todayGenerated.value++
    totalCases.value++
    
    // 保存到历史记录
    saveToHistory()
    
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
    console.log('Message sending completed, isGenerating:', isGenerating.value)
  }
}

// 模拟AI响应
async function simulateAIResponse(userInput) {
  const assistantMessage = {
    id: Date.now() + 1,
    role: 'assistant',
    content: '',
    timestamp: new Date().toISOString(),
    isStreaming: true
  }
  
  messages.value.push(assistantMessage)
  
  // 模拟流式响应
  const response = generateMockResponse(userInput)
  const words = response.split('')
  
  for (let i = 0; i < words.length; i++) {
    await new Promise(resolve => setTimeout(resolve, 20))
    assistantMessage.content += words[i]
    
    if (i % 50 === 0 || i === words.length - 1) {
      const messageIndex = messages.value.findIndex(msg => msg.id === assistantMessage.id)
      if (messageIndex !== -1) {
        messages.value[messageIndex] = { ...assistantMessage }
      }
    }
  }
  
  assistantMessage.isStreaming = false
  const messageIndex = messages.value.findIndex(msg => msg.id === assistantMessage.id)
  if (messageIndex !== -1) {
    messages.value[messageIndex] = { ...assistantMessage }
  }
}

// 生成模拟响应
function generateMockResponse(input) {
  return `基于您的需求"${input.substring(0, 50)}..."，我为您生成以下思政案例：

**案例标题：** 软件质量与工匠精神

**背景介绍：**
在某互联网公司的软件开发项目中，开发团队面临着紧急上线的压力。项目经理要求团队加快开发进度，但测试工程师小李坚持认为需要进行充分的测试，确保软件质量。

**核心问题：**
在时间压力和质量要求之间，团队应该如何平衡？作为软件工程师，我们的职业操守是什么？

**思政启示：**
1. **精益求精的工匠精神**：软件开发不仅是技术活动，更是品质的体现
2. **职业道德与责任**：程序员应该对用户负责，对社会负责
3. **团队协作与沟通**：在分歧中寻求最佳解决方案

**讨论问题：**
1. 如何在项目压力下坚持质量标准？
2. 软件工程师的社会责任体现在哪些方面？
3. 如何培养和传承工匠精神？

**实践应用：**
结合实际项目经验，讨论质量管理体系的重要性。`
}

// 使用示例
function handleUseExample(content) {
  chatInput.value?.focus()
  // 这里可以直接触发发送，或者填充到输入框
  handleSendMessage({ content, attachments: [] })
}

// 重新生成
function handleRegenerate(messageId) {
  const messageIndex = messages.value.findIndex(msg => msg.id === messageId)
  if (messageIndex > 0) {
    const userMessage = messages.value[messageIndex - 1]
    // 移除原有的AI回复
    messages.value.splice(messageIndex)
    // 重新生成
    handleSendMessage({ content: userMessage.content, attachments: userMessage.attachments || [] })
  }
}

// 保存案例
function handleSaveCase(messageContent) {
  // 这里应该调用API保存案例到案例库
  message.success('案例已保存到案例库')
}

// 清空历史
function handleClearHistory() {
  messages.value = []
  currentSessionId.value = null
}

// 保存到历史记录
function saveToHistory() {
  if (messages.value.length >= 2) {
    const session = {
      id: currentSessionId.value || Date.now(),
      title: messages.value[0].content.substring(0, 30) + '...',
      messages: [...messages.value],
      createdAt: new Date().toISOString()
    }
    
    const existingIndex = chatHistory.value.findIndex(s => s.id === session.id)
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
  const session = chatHistory.value.find(s => s.id === sessionId)
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
  message.info('提示词模板功能开发中')
}

// 导出当前对话
function exportCurrentChat() {
  chatContainer.value?.exportChat()
}

// 显示全部历史
function showAllHistory() {
  message.info('查看全部历史功能开发中')
}

// 组件挂载时初始化
onMounted(() => {
  // 模拟加载统计数据
  todayGenerated.value = 3
  totalCases.value = 156
  usageTime.value = 45
  
  // 从localStorage加载历史记录
  const savedHistory = localStorage.getItem('aigc-chat-history')
  if (savedHistory) {
    try {
      chatHistory.value = JSON.parse(savedHistory)
    } catch (e) {
      console.warn('Failed to load chat history:', e)
    }
  }
})

// 监听历史记录变化，自动保存
watch(chatHistory, (newHistory) => {
  localStorage.setItem('aigc-chat-history', JSON.stringify(newHistory))
}, { deep: true })
</script>

<style scoped>
.aigc-chat-page {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.page-header {
  background: linear-gradient(135deg, #FF8A65 0%, #FF7043 100%);
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
  background: linear-gradient(135deg, #D84315 0%, #BF360C 100%);
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