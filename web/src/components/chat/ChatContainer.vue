<template>
  <div class="chat-container">
    <div class="chat-header">
      <div class="header-title">
        <n-icon size="20" color="white">
          <Icon icon="mdi:robot" />
        </n-icon>
        <span>AIGC思政案例生成助手</span>
      </div>

      <div class="header-actions">
        <n-space>
          <n-tooltip trigger="hover">
            <template #trigger>
              <n-button size="small" quaternary circle @click="toggleSettings">
                <template #icon
                  ><n-icon color="white"><Icon icon="ant-design:setting-outlined" /></n-icon
                ></template>
              </n-button>
            </template>
            生成设置
          </n-tooltip>

          <n-tooltip trigger="hover">
            <template #trigger>
              <n-button size="small" quaternary circle @click="exportChat">
                <template #icon
                  ><n-icon color="white"><Icon icon="ant-design:export-outlined" /></n-icon
                ></template>
              </n-button>
            </template>
            导出对话
          </n-tooltip>
        </n-space>
      </div>
    </div>

    <div ref="messagesContainer" class="messages-container">
      <div v-if="messages.length === 0" class="empty-state">
        <div class="empty-icon">
          <n-icon size="48" color="var(--n-text-color-depth-3)">
            <Icon icon="ant-design:message-outlined" />
          </n-icon>
        </div>
        <h3>开始您的思政案例生成之旅</h3>
        <p>描述您的课程内容和思政需求，AI将为您生成高质量的教学案例</p>

        <!-- <div class="quick-start">
          <n-space vertical>
            <h4>快速开始示例：</h4>
            <n-button
              v-for="example in quickExamples"
              :key="example.id"
              size="small"
              quaternary
              @click="$emit('use-example', example.content)"
            >
              {{ example.title }}
            </n-button>
          </n-space>
        </div> -->
      </div>

      <div v-else class="messages-list">
        <ChatMessage
          v-for="message in messages"
          :key="message.id"
          :message="message"
          @copy-message="handleCopyMessage"
          @regenerate="handleRegenerate"
          @save-case="handleSaveCase"
        />

        <!-- 加载状态 -->
        <div v-if="isGenerating" class="generating-indicator">
          <div class="loading-avatar">
            <n-avatar size="32">
              <n-icon><Icon icon="mdi:robot" /></n-icon>
            </n-avatar>
          </div>
          <div class="loading-content">
            <n-space vertical size="small">
              <n-skeleton text :repeat="3" />
              <div class="loading-text">
                <n-icon class="loading-icon"><Icon icon="ant-design:loading-outlined" /></n-icon>
                正在生成思政案例...
              </div>
            </n-space>
          </div>
        </div>
      </div>
    </div>

    <!-- 生成设置抽屉 -->
    <n-drawer v-model:show="showSettings" width="400" placement="right">
      <n-drawer-content title="生成设置">
        <n-space vertical size="large">
          <div>
            <n-text strong>生成参数</n-text>
            <n-space vertical size="medium" style="margin-top: 12px">
              <div>
                <n-text depth="2">创造性 (Temperature)</n-text>
                <n-slider
                  v-model:value="settings.temperature"
                  :min="0"
                  :max="1"
                  :step="0.1"
                  :marks="{ 0: '保守', 0.5: '平衡', 1: '创新' }"
                />
              </div>

              <div>
                <n-text depth="2">最大长度</n-text>
                <n-input-number
                  v-model:value="settings.maxTokens"
                  :min="100"
                  :max="2000"
                  :step="100"
                  style="width: 100%"
                />
              </div>
            </n-space>
          </div>

          <div>
            <n-text strong>案例偏好</n-text>
            <n-space vertical size="medium" style="margin-top: 12px">
              <n-checkbox-group v-model:value="settings.preferences">
                <n-space vertical>
                  <n-checkbox value="practical">注重实用性</n-checkbox>
                  <n-checkbox value="innovative">突出创新性</n-checkbox>
                  <n-checkbox value="ethical">强调伦理道德</n-checkbox>
                  <n-checkbox value="teamwork">体现团队协作</n-checkbox>
                </n-space>
              </n-checkbox-group>
            </n-space>
          </div>
        </n-space>

        <template #footer>
          <n-space>
            <n-button @click="resetSettings">重置</n-button>
            <n-button type="primary" @click="saveSettings">保存设置</n-button>
          </n-space>
        </template>
      </n-drawer-content>
    </n-drawer>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, onUnmounted } from 'vue'
import {
  NIcon,
  NButton,
  NSpace,
  NTooltip,
  NAvatar,
  NSkeleton,
  NDrawer,
  NDrawerContent,
  NText,
  NSlider,
  NInputNumber,
  NCheckboxGroup,
  NCheckbox,
  useMessage,
} from 'naive-ui'
import { Icon } from '@iconify/vue'
import ChatMessage from './ChatMessage.vue'

const props = defineProps({
  messages: {
    type: Array,
    default: () => [],
  },
  isGenerating: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['use-example', 'regenerate', 'save-case'])

const message = useMessage()
const messagesContainer = ref()
const showSettings = ref(false)

// 生成设置
const settings = ref({
  temperature: 0.7,
  maxTokens: 1000,
  preferences: ['practical', 'ethical'],
})

// 快速开始示例
const quickExamples = ref([
  {
    id: 1,
    title: '软件测试中的质量意识',
    content:
      '请为软件测试章节生成一个思政案例，强调质量意识和精益求精的工匠精神，结合实际测试项目经验。',
  },
  {
    id: 2,
    title: '敏捷开发中的团队协作',
    content: '生成一个关于敏捷开发的思政案例，重点体现团队协作、有效沟通和集体责任感。',
  },
  {
    id: 3,
    title: '软件安全与社会责任',
    content: '创建一个软件安全相关的思政案例，突出程序员的社会责任和职业道德。',
  },
])

// 滚动到底部
function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 复制消息
function handleCopyMessage(content) {
  navigator.clipboard
    .writeText(content)
    .then(() => {
      message.success('已复制到剪贴板')
    })
    .catch(() => {
      message.error('复制失败')
    })
}

// 重新生成
function handleRegenerate(messageId) {
  emit('regenerate', messageId)
}

// 保存案例
function handleSaveCase(messageContent) {
  emit('save-case', messageContent)
}

// 切换设置
function toggleSettings() {
  showSettings.value = !showSettings.value
}

// 导出对话
function exportChat() {
  if (props.messages.length === 0) {
    message.warning('没有对话内容可导出')
    return
  }

  // 生成 Markdown 格式内容
  const now = new Date()
  const dateStr = now.toLocaleString('zh-CN')
  
  let chatContent = `# AIGC 对话记录\n\n`
  chatContent += `**导出时间**: ${dateStr}\n\n`
  chatContent += `**消息数量**: ${props.messages.length}\n\n`
  chatContent += `---\n\n`
  
  chatContent += props.messages
    .map((msg, index) => {
      const role = msg.role === 'user' ? '👤 教师' : '🤖 AIGC助手'
      const timestamp = msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString('zh-CN') : ''
      const timeInfo = timestamp ? ` <small>(${timestamp})</small>` : ''
      
      return `### ${role}${timeInfo}\n\n${msg.content}\n`
    })
    .join('\n---\n\n')

  const blob = new Blob([chatContent], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `AIGC对话_${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}_${String(now.getHours()).padStart(2, '0')}${String(now.getMinutes()).padStart(2, '0')}.md`
  a.click()
  URL.revokeObjectURL(url)

  message.success('对话已导出为 Markdown 格式')
}

// 重置设置
function resetSettings() {
  settings.value = {
    temperature: 0.7,
    maxTokens: 1000,
    preferences: ['practical', 'ethical'],
  }
  message.info('设置已重置')
}

// 保存设置
function saveSettings() {
  // 这里可以将设置保存到本地存储或发送到服务器
  localStorage.setItem('aigc-settings', JSON.stringify(settings.value))
  showSettings.value = false
  message.success('设置已保存')
}

// 监听消息变化，自动滚动
let observer

onMounted(() => {
  // 加载保存的设置
  const savedSettings = localStorage.getItem('aigc-settings')
  if (savedSettings) {
    settings.value = { ...settings.value, ...JSON.parse(savedSettings) }
  }

  // 设置滚动观察器
  if (messagesContainer.value) {
    observer = new MutationObserver(() => {
      scrollToBottom()
    })
    observer.observe(messagesContainer.value, { childList: true, subtree: true })
  }
})

onUnmounted(() => {
  if (observer) {
    observer.disconnect()
  }
})

// 暴露方法
defineExpose({
  scrollToBottom,
  getSettings: () => settings.value,
  exportChat,
})
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  background: var(--n-color);
  border-radius: 8px;
  overflow: hidden;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, rgba(255, 138, 101, 0.9) 0%, rgba(255, 112, 67, 0.9) 100%);
  color: #ffffff !important;
  box-shadow: 0 2px 8px rgba(255, 138, 101, 0.15);
  flex-shrink: 0;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  font-weight: 500;
  color: #ffffff !important;
  flex: 1;
  min-width: 0;
}

.header-title span {
  color: #ffffff !important;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 0;
  min-height: 0;
  scroll-behavior: smooth;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 40px 20px;
  text-align: center;
  color: var(--n-text-color-depth-2);
}

.empty-icon {
  margin-bottom: 16px;
}

.empty-state h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 500;
  color: var(--n-text-color);
}

.empty-state p {
  margin: 0 0 24px 0;
  max-width: 400px;
  line-height: 1.6;
}

.quick-start {
  background: var(--n-color-hover);
  padding: 20px;
  border-radius: 8px;
  max-width: 500px;
}

.quick-start h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 500;
  color: var(--n-text-color);
}

.messages-list {
  padding: 20px;
}

.generating-indicator {
  display: flex;
  gap: 12px;
  padding: 16px;
  margin-bottom: 16px;
  border-radius: 8px;
  background: linear-gradient(135deg, #fff 0%, #f8fffe 100%);
  border: 1px solid var(--n-border-color);
}

.loading-avatar {
  flex-shrink: 0;
}

.loading-avatar .n-avatar {
  border-radius: 8px !important;
}

.loading-content {
  flex: 1;
}

.loading-text {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--n-text-color-depth-2);
}

.loading-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 滚动条样式 */
.messages-container::-webkit-scrollbar {
  width: 6px;
}

.messages-container::-webkit-scrollbar-track {
  background: var(--n-scrollbar-color);
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb {
  background: var(--n-scrollbar-color-hover);
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: var(--n-primary-color);
}

/* 主题适配 */
[data-theme='dark'] .chat-header {
  background: linear-gradient(135deg, rgba(216, 67, 21, 0.85) 0%, rgba(191, 54, 12, 0.85) 100%);
  box-shadow: 0 2px 8px rgba(216, 67, 21, 0.2);
}

[data-theme='dark'] .header-title,
[data-theme='dark'] .header-title span {
  color: #ffffff !important;
}

/* 确保图标在不同主题下都可见 */
.header-title .n-icon,
.header-actions .n-icon {
  color: #ffffff !important;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-header {
    padding: 12px 16px;
  }

  .header-title {
    font-size: 14px;
  }

  .messages-list {
    padding: 16px;
  }

  .empty-state {
    padding: 20px 16px;
  }

  .quick-start {
    padding: 16px;
  }
}
</style>
