<template>
  <n-modal
    v-model:show="visible"
    :mask-closable="false"
    preset="dialog"
    style="width: 700px"
    title="添加外部链接"
  >
    <n-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-placement="left"
      :label-width="120"
      require-mark-placement="right-hanging"
    >
      <n-form-item label="资源标题" path="title">
        <n-input
          v-model:value="formData.title"
          placeholder="请输入资源标题"
          maxlength="100"
          show-count
        />
      </n-form-item>

      <n-form-item label="外部链接" path="external_url">
        <n-input
          v-model:value="formData.external_url"
          placeholder="请输入完整的URL地址，如：https://example.com"
          @blur="handleUrlBlur"
        />
      </n-form-item>

      <n-form-item label="资源类型" path="resource_type">
        <n-select
          v-model:value="formData.resource_type"
          placeholder="选择资源类型"
          :options="resourceTypeOptions"
        />
      </n-form-item>

      <n-form-item label="资源描述" path="description">
        <n-input
          v-model:value="formData.description"
          type="textarea"
          placeholder="请输入资源描述"
          :autosize="{ minRows: 3, maxRows: 5 }"
          maxlength="500"
          show-count
        />
      </n-form-item>

      <n-grid :cols="2" :x-gap="16">
        <n-form-item-grid-item label="软件工程章节" path="software_engineering_chapter">
          <n-select
            v-model:value="formData.software_engineering_chapter"
            placeholder="选择章节"
            :options="chapterOptions"
            clearable
          />
        </n-form-item-grid-item>

        <n-form-item-grid-item label="思政主题" path="theme_category_id">
          <n-select
            v-model:value="formData.theme_category_id"
            placeholder="选择主题"
            :options="themeOptions"
            clearable
          />
        </n-form-item-grid-item>
      </n-grid>

      <n-form-item label="标签">
        <n-dynamic-tags
          v-model:value="formData.tags"
          placeholder="按回车添加标签"
        />
      </n-form-item>

      <n-form-item label="公开设置">
        <n-space align="center">
          <n-switch v-model:value="formData.is_public" />
          <n-text depth="3" style="font-size: 12px;">
            公开后其他教师可以查看和使用此资源
          </n-text>
        </n-space>
      </n-form-item>
    </n-form>

    <template #action>
      <n-space>
        <n-button @click="handleCancel">取消</n-button>
        <n-button type="primary" @click="handleSubmit" :loading="submitting">
          添加
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { useMessage } from 'naive-ui'
import {
  NModal,
  NForm,
  NFormItem,
  NFormItemGridItem,
  NGrid,
  NInput,
  NSelect,
  NSwitch,
  NDynamicTags,
  NButton,
  NSpace,
  NText,
} from 'naive-ui'
import { request } from '@/utils'

const props = defineProps({
  visible: Boolean,
  chapterOptions: Array,
  themeOptions: Array,
})

const emit = defineEmits(['update:visible', 'success'])

const message = useMessage()
const formRef = ref(null)
const submitting = ref(false)

const visible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val),
})

const formData = reactive({
  title: '',
  external_url: '',
  resource_type: 'link',
  description: '',
  software_engineering_chapter: null,
  theme_category_id: null,
  tags: [],
  is_public: true,
})

const resourceTypeOptions = [
  { label: '外部链接', value: 'link' },
  { label: '虚拟仿真', value: 'simulation' },
  { label: '在线工具', value: 'other' },
]

const rules = {
  title: [
    { required: true, message: '请输入资源标题', trigger: 'blur' },
  ],
  external_url: [
    { required: true, message: '请输入外部链接', trigger: 'blur' },
    {
      pattern: /^https?:\/\/.+/,
      message: '请输入有效的URL地址',
      trigger: 'blur',
    },
  ],
  resource_type: [
    { required: true, message: '请选择资源类型', trigger: 'change' },
  ],
}

const handleUrlBlur = () => {
  // 如果标题为空，尝试从URL提取标题
  if (!formData.title && formData.external_url) {
    try {
      const url = new URL(formData.external_url)
      formData.title = url.hostname
    } catch (e) {
      // 忽略无效URL
    }
  }
}

const handleCancel = () => {
  visible.value = false
  resetForm()
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()

    submitting.value = true

    const data = {
      ...formData,
      tags: formData.tags,
    }

    await request.post('/ideological/resources/', data)

    message.success('链接添加成功')
    visible.value = false
    resetForm()
    emit('success')
  } catch (error) {
    console.error('添加失败:', error)
    if (error.errors) {
      // 表单验证错误
      return
    }
    message.error(error.response?.data?.detail || '添加失败')
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  Object.assign(formData, {
    title: '',
    external_url: '',
    resource_type: 'link',
    description: '',
    software_engineering_chapter: null,
    theme_category_id: null,
    tags: [],
    is_public: true,
  })
  formRef.value?.restoreValidation()
}

watch(() => props.visible, (val) => {
  if (!val) {
    resetForm()
  }
})
</script>
