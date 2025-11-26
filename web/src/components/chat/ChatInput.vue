<template>
  <div class="chat-input-container">
    <div class="input-toolbar">
      <n-space>
        <n-tooltip trigger="hover">
          <template #trigger>
            <n-button size="small" quaternary circle @click="showPromptTemplates = true">
              <template #icon
                ><n-icon><Icon icon="ant-design:book-outlined" /></n-icon
              ></template>
            </n-button>
          </template>
          提示词模板
        </n-tooltip>

        <n-tooltip trigger="hover">
          <template #trigger>
            <n-button size="small" quaternary circle @click="$refs.fileInput.click()">
              <template #icon
                ><n-icon><Icon icon="mdi:attachment" /></n-icon
              ></template>
            </n-button>
          </template>
          上传文件
        </n-tooltip>

        <n-tooltip trigger="hover">
          <template #trigger>
            <n-button size="small" quaternary circle @click="clearInput">
              <template #icon
                ><n-icon><Icon icon="ant-design:delete-outlined" /></n-icon
              ></template>
            </n-button>
          </template>
          清空输入
        </n-tooltip>
      </n-space>
    </div>

    <div class="input-area">
      <n-input
        ref="inputRef"
        v-model:value="inputText"
        type="textarea"
        :placeholder="placeholder"
        :autosize="{ minRows: 5, maxRows: 12 }"
        :disabled="loading"
        @keydown="handleKeydown"
        @focus="$emit('focus')"
        @blur="$emit('blur')"
      />

      <div class="input-actions">
        <div class="input-info">
          <span class="char-count">{{ inputText.length }}/2000</span>
        </div>

        <n-space>
          <n-button size="small" quaternary :disabled="loading" @click="$emit('clear-history')">
            清空对话
          </n-button>

          <n-button
            type="primary"
            size="small"
            :loading="loading"
            :disabled="!canSend"
            @click="handleSend"
          >
            <template v-if="!loading" #icon>
              <n-icon><Icon icon="ant-design:send-outlined" /></n-icon>
            </template>
            {{ loading ? '生成中...' : '发送' }}
          </n-button>
        </n-space>
      </div>
    </div>

    <!-- 文件上传 -->
    <input
      ref="fileInput"
      type="file"
      multiple
      accept=".txt,.doc,.docx,.pdf"
      style="display: none"
      @change="handleFileUpload"
    />

    <!-- 附件预览 -->
    <div v-if="attachments.length" class="attachments-preview">
      <n-space>
        <n-tag
          v-for="(file, index) in attachments"
          :key="index"
          closable
          size="small"
          @close="removeAttachment(index)"
        >
          <template #icon>
            <n-icon><Icon icon="ant-design:file-outlined" /></n-icon>
          </template>
          {{ file.name }}
        </n-tag>
      </n-space>
    </div>

    <!-- 提示词模板弹窗 -->
    <n-modal
      v-model:show="showPromptTemplates"
      preset="card"
      title="选择提示词模板"
      style="width: 600px"
    >
      <n-list>
        <n-list-item v-for="template in promptTemplates" :key="template.id">
          <n-thing :title="template.title" :description="template.description">
            <template #action>
              <n-button size="small" @click="useTemplate(template)"> 使用模板 </n-button>
            </template>
          </n-thing>
        </n-list-item>
      </n-list>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import {
  NInput,
  NButton,
  NIcon,
  NSpace,
  NTooltip,
  NTag,
  NModal,
  NList,
  NListItem,
  NThing,
  useMessage,
} from 'naive-ui'
import { Icon } from '@iconify/vue'

const props = defineProps({
  loading: {
    type: Boolean,
    default: false,
  },
  placeholder: {
    type: String,
    default:
      '请描述您的教学内容和思政要求，例如：\n\n- 课程章节：软件测试\n- 知识点：单元测试、测试驱动开发\n- 思政主题：质量意识、精益求精\n- 案例要求：结合实际项目经验',
  },
})

const emit = defineEmits(['send', 'clear-history', 'focus', 'blur'])

const message = useMessage()
const inputRef = ref()
const fileInput = ref()
const inputText = ref('')
const attachments = ref([])
const showPromptTemplates = ref(false)

const canSend = computed(() => {
  return inputText.value.trim().length > 0 && inputText.value.length <= 2000 && !props.loading
})

// 预设提示词模板
const promptTemplates = ref([
  {
    id: 1,
    title: '软件工程基础案例',
    description: '生成软件工程基础知识相关的思政案例',
    content:
      '请为《软件工程》课程生成一个思政案例：\n\n课程章节：[请填写章节名称]\n知识点：[请填写具体知识点]\n思政主题：职业道德、团队协作\n案例要求：结合实际软件开发项目，体现工程师的社会责任',
  },
  {
    id: 2,
    title: '团队协作案例',
    description: '强调团队合作和沟通的重要性',
    content:
      '请生成一个关于团队协作的思政案例：\n\n背景：敏捷开发团队项目\n重点：有效沟通、相互信任、共同目标\n思政要素：集体主义精神、协作共赢\n期望效果：培养学生团队意识和协作能力',
  },
  {
    id: 3,
    title: '质量与责任案例',
    description: '突出软件质量与社会责任的关系',
    content:
      '请创建一个关于软件质量的思政案例：\n\n主题：软件质量与社会影响\n场景：关键系统软件开发\n思政角度：精益求精、社会责任感\n教学目标：培养学生对软件质量的敬畏之心',
  },
])

function handleKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey && !e.ctrlKey) {
    e.preventDefault()
    if (canSend.value) {
      handleSend()
    }
  }
}

function handleSend() {
  console.log('handleSend called, canSend:', canSend.value)
  if (!canSend.value) return

  const content = inputText.value.trim()
  const files = [...attachments.value]

  console.log('Emitting send event with:', { content, attachments: files })

  emit('send', {
    content,
    attachments: files,
  })

  // 清空输入
  inputText.value = ''
  attachments.value = []
}

function clearInput() {
  inputText.value = ''
  attachments.value = []
  nextTick(() => {
    inputRef.value?.focus()
  })
}

function handleFileUpload(e) {
  const files = Array.from(e.target.files)
  const maxSize = 10 * 1024 * 1024 // 10MB

  for (const file of files) {
    if (file.size > maxSize) {
      message.warning(`文件 ${file.name} 超过10MB限制`)
      continue
    }

    if (attachments.value.find((f) => f.name === file.name && f.size === file.size)) {
      message.warning(`文件 ${file.name} 已存在`)
      continue
    }

    attachments.value.push(file)
  }

  // 清空input
  e.target.value = ''
}

function removeAttachment(index) {
  attachments.value.splice(index, 1)
}

function useTemplate(template) {
  inputText.value = template.content
  showPromptTemplates.value = false
  nextTick(() => {
    inputRef.value?.focus()
  })
}

// 设置输入内容
function setContent(content) {
  inputText.value = content
  nextTick(() => {
    inputRef.value?.focus()
  })
}

// 暴露方法供父组件调用
defineExpose({
  focus: () => inputRef.value?.focus(),
  clear: clearInput,
  setContent,
})
</script>

<style scoped>
.chat-input-container {
  background: var(--n-color);
  border: 1px solid var(--n-border-color);
  border-radius: 12px;
  padding: 16px;
  min-height: 160px;
  transition: all 0.3s ease;
}

.chat-input-container:focus-within {
  border-color: var(--n-primary-color);
  box-shadow: 0 0 0 2px var(--n-primary-color-suppl);
}

.input-toolbar {
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--n-divider-color);
}

.input-area {
  position: relative;
  min-height: 100px;
}

.input-area .n-input {
  min-height: 100px;
}

.input-area .n-input .n-input__textarea {
  min-height: 100px !important;
  line-height: 1.8;
  padding: 16px;
  font-size: 14px;
  resize: none;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 8px;
  border-top: 1px solid var(--n-divider-color);
}

.input-info {
  font-size: 12px;
  color: var(--n-text-color-depth-3);
}

.char-count {
  font-variant-numeric: tabular-nums;
}

.attachments-preview {
  margin-top: 12px;
  padding-top: 8px;
  border-top: 1px solid var(--n-divider-color);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-input-container {
    padding: 12px;
  }

  .input-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .input-info {
    text-align: center;
  }
}

/* 确保图标和按钮在所有主题下可见 */
.input-toolbar .n-button .n-icon,
.input-actions .n-button .n-icon {
  color: var(--n-text-color) !important;
}

.input-toolbar .n-tooltip .n-button,
.input-actions .n-button {
  color: var(--n-text-color) !important;
}

/* 附件标签样式 */
.attachments-preview .n-tag {
  background: var(--n-color-hover);
  border: 1px solid var(--n-border-color);
}

.attachments-preview .n-tag .n-icon {
  color: var(--n-text-color) !important;
}

/* 夜间模式适配 */
[data-theme='dark'] .chat-input-container {
  background: var(--n-card-color);
  border-color: var(--n-border-color);
}

[data-theme='dark'] .input-toolbar .n-button,
[data-theme='dark'] .input-actions .n-button {
  color: var(--n-text-color) !important;
}

[data-theme='dark'] .input-toolbar .n-button .n-icon,
[data-theme='dark'] .input-actions .n-button .n-icon {
  color: var(--n-text-color) !important;
}
</style>
