<template>
  <div class="chat-message" :class="messageClass">
    <div class="message-avatar">
      <n-avatar
        :size="32"
        :src="message.role === 'user' ? undefined : '/robot-avatar.png'"
        :fallback-src="message.role === 'user' ? undefined : 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjMyIiBoZWlnaHQ9IjMyIiByeD0iMTYiIGZpbGw9IiM0Yzc5ZmYiLz4KPHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4PSI4IiB5PSI4Ij4KPHBhdGggZD0iTTggMkMxMC4yMDkxIDIgMTIgMy43OTA4NiAxMiA2VjEwQzEyIDEyLjIwOTEgMTAuMjA5MSAxNCA4IDE0QzUuNzkwODYgMTQgNCAxMi4yMDkxIDQgMTBWNkM0IDMuNzkwODYgNS43OTA4NiAyIDggMloiIGZpbGw9IndoaXRlIi8+CjxjaXJjbGUgY3g9IjYiIGN5PSI3IiByPSIxIiBmaWxsPSIjNGM3OWZmIi8+CjxjaXJjbGUgY3g9IjEwIiBjeT0iNyIgcj0iMSIgZmlsbD0iIzRjNzlmZiIvPgo8L3N2Zz4KPC9zdmc+'"
      >
        <template v-if="message.role === 'user'">
          <n-icon size="18" color="#4c79ff">
            <svg viewBox="0 0 24 24">
              <path fill="currentColor" d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM21 9V7L15 1.5V3.5L9 3.5V1.5L3 7V9H21ZM12 8C15.86 8 19 11.14 19 15V17C19 18.1 18.1 19 17 19H7C5.9 19 5 18.1 5 17V15C5 11.14 8.14 8 12 8Z"/>
            </svg>
          </n-icon>
        </template>
      </n-avatar>
    </div>
    
    <div class="message-content">
      <div class="message-header">
        <span class="message-role">{{ message.role === 'user' ? '教师' : 'AIGC助手' }}</span>
        <span class="message-time">{{ formatTime(message.timestamp) }}</span>
      </div>
      
      <div class="message-body">
        <div v-if="message.role === 'assistant' && message.isStreaming" class="streaming-content">
          <span>{{ message.content }}</span>
          <span class="cursor">|</span>
        </div>
        <div v-else class="message-text" v-html="formatContent(message.content)"></div>
        
        <div v-if="message.attachments?.length" class="message-attachments">
          <n-space>
            <n-tag v-for="file in message.attachments" :key="file.name" size="small">
              <template #icon>
                <n-icon><Icon icon="ant-design:file-outlined" /></n-icon>
              </template>
              {{ file.name }}
            </n-tag>
          </n-space>
        </div>
      </div>
      
      <div v-if="message.role === 'assistant'" class="message-actions">
        <n-space>
          <n-button size="tiny" quaternary @click="$emit('copy-message', message.content)">
            <template #icon><n-icon><Icon icon="ant-design:copy-outlined" /></n-icon></template>
            复制
          </n-button>
          <n-button size="tiny" quaternary @click="$emit('regenerate', message.id)">
            <template #icon><n-icon><Icon icon="ant-design:reload-outlined" /></n-icon></template>
            重新生成
          </n-button>
          <n-button size="tiny" quaternary @click="$emit('save-case', message)">
            <template #icon><n-icon><Icon icon="ant-design:save-outlined" /></n-icon></template>
            保存案例
          </n-button>
        </n-space>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { NAvatar, NIcon, NSpace, NTag, NButton } from 'naive-ui'
import { Icon } from '@iconify/vue'

const props = defineProps({
  message: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['copy-message', 'regenerate', 'save-case'])

const messageClass = computed(() => ({
  'user-message': props.message.role === 'user',
  'assistant-message': props.message.role === 'assistant'
}))

function formatTime(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function formatContent(content) {
  if (!content) return ''
  // 简单的markdown渲染，处理换行和加粗
  return content
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
}
</script>

<style scoped>
.chat-message {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  padding: 16px;
  border-radius: 8px;
  transition: background-color 0.3s ease;
}

.chat-message:hover {
  background-color: var(--n-color-hover);
}

.user-message {
  flex-direction: row-reverse;
  background: linear-gradient(135deg, #f6f8ff 0%, #e8f0ff 100%);
}

.assistant-message {
  background: linear-gradient(135deg, #fff 0%, #f8fffe 100%);
  border: 1px solid var(--n-border-color);
}

.message-avatar {
  flex-shrink: 0;
}

.message-avatar .n-avatar {
  border-radius: 18px !important;
}

.message-avatar .n-avatar .n-avatar__img {
  border-radius: 18px !important;
}

.message-content {
  flex: 1;
  min-width: 0;
}

.user-message .message-content {
  text-align: right;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 12px;
  color: var(--n-text-color-depth-3);
}

.user-message .message-header {
  flex-direction: row-reverse;
}

.message-role {
  font-weight: 500;
  color: var(--n-text-color-depth-2);
}

.message-body {
  margin-bottom: 8px;
}

.message-text {
  line-height: 1.6;
  color: var(--n-text-color);
  word-wrap: break-word;
}

.streaming-content {
  line-height: 1.6;
  color: var(--n-text-color);
}

.cursor {
  animation: blink 1s infinite;
  color: var(--n-primary-color);
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

.message-attachments {
  margin-top: 8px;
}

.message-actions {
  opacity: 0;
  transition: opacity 0.3s ease;
}

.chat-message:hover .message-actions {
  opacity: 1;
}

.user-message .message-actions {
  text-align: right;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-message {
    padding: 12px;
    gap: 8px;
  }
  
  .message-header {
    font-size: 11px;
  }
  
  .message-actions {
    opacity: 1; /* 移动端始终显示操作按钮 */
  }
}
</style>