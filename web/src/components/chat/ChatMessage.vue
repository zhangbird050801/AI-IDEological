<template>
  <div class="chat-message" :class="messageClass">
    <div class="message-avatar">
      <n-avatar
        :size="32"
        round
        :src="message.role === 'user' ? (message.avatar || userAvatar) : undefined"
        :style="message.role === 'user' ? '' : 'background: linear-gradient(135deg, #4c79ff, #6ed0ff); color: #fff;'"
      >
        <template v-if="message.role === 'user' && !(message.avatar || userAvatar)">
          <n-icon size="18" color="#4c79ff">
            <svg viewBox="0 0 24 24">
              <path
                fill="currentColor"
                d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM21 9V7L15 1.5V3.5L9 3.5V1.5L3 7V9H21ZM12 8C15.86 8 19 11.14 19 15V17C19 18.1 18.1 19 17 19H7C5.9 19 5 18.1 5 17V15C5 11.14 8.14 8 12 8Z"
              />
            </svg>
          </n-icon>
        </template>
        <template v-else-if="message.role !== 'user'">
          <n-icon size="18" color="#fff">
            <svg viewBox="0 0 24 24">
              <path
                fill="currentColor"
                d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM7 8.5L5 11H3V8.5L7 5.5V3.5H9V5.5L12 8.5L15 5.5V3.5H17V5.5L21 8.5V11H19L17 8.5L14 11H10L7 8.5ZM6 13H18C19.1 13 20 13.9 20 15V19C20 20.1 19.1 21 18 21H6C4.9 21 4 20.1 4 19V15C4 13.9 4.9 13 6 13ZM8 15C7.45 15 7 15.45 7 16C7 16.55 7.45 17 8 17C8.55 17 9 16.55 9 16C9 15.45 8.55 15 8 15ZM16 15C15.45 15 15 15.45 15 16C15 16.55 15.45 17 16 17C16.55 17 17 16.55 17 16C17 15.45 16.55 15 16 15Z"
              />
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
        <div v-else class="message-text" v-html="renderMarkdown(message.content)"></div>

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

      <div v-if="message.role === 'assistant' && !message.isStreaming" class="message-actions">
        <n-space>
          <n-button size="tiny" quaternary @click="$emit('copy-message', message.content)">
            <template #icon
              ><n-icon><Icon icon="ant-design:copy-outlined" /></n-icon
            ></template>
            复制
          </n-button>
          <n-button size="tiny" quaternary @click="$emit('regenerate', message.id)">
            <template #icon
              ><n-icon><Icon icon="ant-design:reload-outlined" /></n-icon
            ></template>
            重新生成
          </n-button>
          <n-button size="tiny" quaternary @click="$emit('save-case', message)">
            <template #icon
              ><n-icon><Icon icon="ant-design:save-outlined" /></n-icon
            ></template>
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
import MarkdownIt from 'markdown-it'
import markdownItKatex from 'markdown-it-katex'
import { useUserStore } from '@/store'

const props = defineProps({
  message: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['copy-message', 'regenerate', 'save-case'])
const userStore = useUserStore()
const userAvatar = computed(() => userStore.avatar || '')

const messageClass = computed(() => ({
  'user-message': props.message.role === 'user',
  'assistant-message': props.message.role === 'assistant',
}))

function formatTime(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

//  使用 markdown-it 渲染
const md = new MarkdownIt({
  html: true, // 允许 HTML 标签
  linkify: true, // 自动转换链接
  breaks: true, // 转换换行符为 <br>
  // typographer: true, // 启用 typographer
})
md.use(markdownItKatex, { throwOnError: false })

function renderMarkdown(content) {
  if (!content) return ''
  let normalized = content
    .replace(/\\\[((?:.|\n)*?)\\\]/g, (_, math) => `$$${math}$$`)
    .replace(/\\\((.*?)\\\)/g, (_, math) => `$${math}$`)
  const displayBlocks = []
  normalized = normalized.replace(/\$\$([\s\S]*?)\$\$/g, (_, math) => {
    const cleaned = math.replace(/\n+/g, ' ').trim()
    const index = displayBlocks.length
    displayBlocks.push(`$$${cleaned}$$`)
    return `@@MATH_DISPLAY_${index}@@`
  })
  normalized = normalized.replace(/\$([^\$]+?)\$/g, (_, math) => {
    const cleaned = math.replace(/\n+/g, ' ').trim()
    return `$${cleaned}$`
  })
  normalized = normalized.replace(/@@MATH_DISPLAY_(\d+)@@/g, (_, index) => displayBlocks[index])
  return md.render(normalized)
}

// function formatContent(content) {
//   if (!content) return ''
//   // 简单的markdown渲染，处理换行和加粗
//   return content
//     .replace(/\n/g, '<br>')
//     .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
//     .replace(/\*(.*?)\*/g, '<em>$1</em>')
// }
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
  margin-left: auto;
  max-width: 65%;
  width: fit-content;
}

.assistant-message {
  background: linear-gradient(135deg, #fff 0%, #f8fffe 100%);
  border: 1px solid var(--n-border-color);
  margin-right: auto;
  max-width: 85%;
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
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 12px;
  color: var(--n-text-color-depth-3);
  width: 100%;
}

.user-message .message-header {
  flex-direction: row-reverse;
  justify-content: flex-start;
  gap: 8px;
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
  font-size: 14px;
}

.message-text :deep(p) {
  margin-top: 0.5em;
  margin-bottom: 0.5em;
}

.user-message .message-text {
  text-align: left;
  max-width: 100%;
}

/* 为两种列表设置通用的内外边距 */
.message-text :deep(ul),
.message-text :deep(ol) {
  /* 使用 padding-left 可以更好地控制项目符号的位置 */
  padding-left: 2em; 
  margin-top: 0.5em;
  margin-bottom: 1em;
}

/* 专门为无序列表 <ul> 设置项目符号 */
.message-text :deep(ul) {
  list-style-type: disc; /* 实心圆点 */
}

/* 专门为有序列表 <ol> 设置项目符号 */
.message-text :deep(ol) {
  list-style-type: decimal; /* 数字 */
}

/* 为所有列表项 <li> 设置通用的样式（比如行间距），但不涉及符号类型 */
.message-text :deep(li) {
  margin-bottom: 0.5em;
}

/* 为行内代码 <code> 设置样式 */
  .message-text :deep(code) {
  /* 使用一个半透明的深色作为背景。
     在浅色渐变背景上，这会呈现为半透明的灰色。
     它既能醒目地标识出代码，又不会完全遮挡背景的美感。*/
  background-color: rgba(0, 0, 0, 0.08);
  
  /* 添加一些内边距和圆角，让它看起来更像一个标签 */
  padding: 3px 6px;
  border-radius: 5px;
  
  /* 确保代码使用等宽字体 */
  font-family: Consolas, Monaco, 'Andale Mono', 'Ubuntu Mono', monospace;
  font-size: 0.9em; /* 可以让字体稍微小一点 */
}

/* 为代码块 <pre> 设置样式 (通常是多行代码) */
.message-text :deep(pre) {
  background-color: rgba(0, 0, 0, 0.1); /* 背景可以比行内代码稍深一点 */
  padding: 1em;
  border-radius: 8px;
  white-space: pre-wrap;   /* 允许代码自动换行 */
  word-wrap: break-word; /* 在单词内部换行 */
}

/* 如果 pre 标签内也包含 code 标签，我们不希望它有双重背景 */
.message-text :deep(pre code) {
  background-color: transparent; /* 重置背景 */
  padding: 0; /* 重置内边距 */
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
  0%,
  50% {
    opacity: 1;
  }
  51%,
  100% {
    opacity: 0;
  }
}

.message-attachments {
  margin-top: 8px;
}

.message-actions {
  opacity: 0;
  transition: opacity 0.3s ease;
  width: 100%;
}

.chat-message:hover .message-actions {
  opacity: 1;
}

.user-message .message-actions {
  display: flex;
  justify-content: flex-end;
}

/* ---- 表格响应式支持 ---- */
/* 在父元素上创建一个块格式化上下文，并让表格可以横向滚动 */
.message-text :deep(table) {
  display: block;
  overflow-x: auto;
  white-space: nowrap; /* 防止表格内容在滚动时换行 */
  margin-top: 1em;
  margin-bottom: 1em;
}

/* ---- 表格整体样式 ---- */
.message-text :deep(table) {
  width: 100%;
  border-collapse: collapse; /* 合并边框 */
  border-spacing: 0;
  font-size: 0.9em; /* 表格字体可以稍小一些 */
}

/* ---- 表头和单元格样式 ---- */
.message-text :deep(th),
.message-text :deep(td) {
  border: 1px solid var(--n-border-color, #e0e0e6); /* 使用Naive UI的边框颜色变量，或一个备用色 */
  padding: 10px 14px; /* 单元格内边距 */
  text-align: left; /* 文本左对齐 */
}

/* ---- 表头特殊样式 ---- */
.message-text :deep(th) {
  font-weight: 600;
  background-color: var(--n-color-hover, #f6f6f7); /* 使用Naive UI的悬浮颜色变量 */
}

/* ---- 斑马条纹 ---- */
/* 使表格更易读 */
.message-text :deep(tbody tr:nth-child(even)) {
  background-color: #fcfcfc;
}

.message-text :deep(hr) {
  /* 核心：调整分割线与上下文的垂直间距 */
  margin-top: 25px;    /* 增加上边距，例如 20px */
  margin-bottom: 25px; /* 增加下边距，例如 20px */

  /* 可选：美化分割线本身 */
  border: none; /* 移除浏览器默认的边框和效果 */
  height: 3px;  /* 设置线条的高度（即粗细） */
  background-color: var(--n-border-color, #e0e0e6); /* 设置线条的颜色 */
}

/* ---- 各级标题的字体大小 ---- */

/* 一级标题 H1 (#) */
.message-text :deep(h1) {
  font-size: 1.4em; /* 减小字体大小 */
  font-weight: 600;
  padding-bottom: 0.3em;
  margin-top: 0.8em;
  margin-bottom: 0.5em;
  border-bottom: 1px solid var(--n-border-color, #e0e0e6);
}

/* 二级标题 H2 (##) */
.message-text :deep(h2) {
  font-size: 1.25em; /* 减小字体大小 */
  font-weight: 600;
  padding-bottom: 0.3em;
  margin-top: 0.7em;
  margin-bottom: 0.4em;
  border-bottom: 1px solid var(--n-border-color, #e0e0e6);
}

/* 三级标题 H3 (###) */
.message-text :deep(h3) {
  font-size: 1.15em; /* 减小字体大小 */
  font-weight: 600;
  margin-top: 0.6em;
  margin-bottom: 0.4em;
}

/* 四级标题 H4 (####) */
.message-text :deep(h4) {
  font-size: 1.1em; /* 减小字体大小 */
  font-weight: 600;
  margin-top: 0.5em;
  margin-bottom: 0.3em;
}

/* 五级标题 H5 (#####) */
.message-text :deep(h5) {
  font-size: 1.05em;
  font-weight: 600;
  margin-top: 0.5em;
  margin-bottom: 0.3em;
}

/* 六级标题 H6 (######) */
.message-text :deep(h6) {
  font-size: 1em;
  font-weight: 600;
  margin-top: 0.5em;
  margin-bottom: 0.3em;
}

/* 如果标题是消息的第一个元素，则移除多余的上边距，让布局更紧凑 */
.message-text :deep(h1:first-child),
.message-text :deep(h2:first-child),
.message-text :deep(h3:first-child),
.message-text :deep(h4:first-child),
.message-text :deep(h5:first-child),
.message-text :deep(h6:first-child) {
    margin-top: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-message {
    padding: 12px;
    gap: 8px;
  }

  .user-message,
  .assistant-message {
    max-width: 90%;
  }

  .message-header {
    font-size: 11px;
  }

  .message-actions {
    opacity: 1; /* 移动端始终显示操作按钮 */
  }
}
</style>
