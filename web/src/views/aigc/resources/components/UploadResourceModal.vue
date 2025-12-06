<template>
  <n-modal
    v-model:show="visible"
    :mask-closable="false"
    preset="dialog"
    style="width: 700px"
    title="上传教学资源"
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

      <n-form-item label="资源文件" path="file">
        <n-upload
          v-model:file-list="fileList"
          :max="1"
          :default-upload="false"
          @change="handleFileChange"
        >
          <n-upload-dragger>
            <div style="margin-bottom: 12px">
              <n-icon size="48" depth="3">
                <Icon icon="ant-design:cloud-upload-outlined" />
              </n-icon>
            </div>
            <n-text style="font-size: 16px">
              点击或拖拽文件到此区域上传
            </n-text>
            <n-p depth="3" style="margin: 8px 0 0 0; font-size: 12px;">
              支持：视频(mp4,avi)、文档(pdf,doc,docx)、演示文稿(ppt,pptx)、图片(jpg,png)等
            </n-p>
          </n-upload-dragger>
        </n-upload>
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
        <n-button type="primary" @click="handleSubmit" :loading="uploading">
          上传
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { useMessage } from 'naive-ui'
import { Icon } from '@iconify/vue'
import {
  NModal,
  NForm,
  NFormItem,
  NFormItemGridItem,
  NGrid,
  NInput,
  NSelect,
  NSwitch,
  NUpload,
  NUploadDragger,
  NDynamicTags,
  NButton,
  NSpace,
  NIcon,
  NText,
  NP,
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
const uploading = ref(false)
const fileList = ref([])

const visible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val),
})

const formData = reactive({
  title: '',
  description: '',
  software_engineering_chapter: null,
  theme_category_id: null,
  tags: [],
  is_public: true,
})

const rules = {
  title: [
    { required: true, message: '请输入资源标题', trigger: 'blur' },
  ],
  file: [
    { required: true, message: '请上传资源文件', trigger: 'change' },
  ],
}

const handleFileChange = ({ fileList: newFileList }) => {
  fileList.value = newFileList
  // 如果标题为空，使用文件名作为标题
  if (!formData.title && newFileList.length > 0) {
    const fileName = newFileList[0].name
    formData.title = fileName.substring(0, fileName.lastIndexOf('.')) || fileName
  }
}

const handleCancel = () => {
  visible.value = false
  resetForm()
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()

    if (fileList.value.length === 0) {
      message.warning('请选择要上传的文件')
      return
    }

    uploading.value = true

    // 创建FormData
    const formDataToSend = new FormData()
    formDataToSend.append('file', fileList.value[0].file)
    formDataToSend.append('title', formData.title)
    formDataToSend.append('description', formData.description || '')
    formDataToSend.append('resource_type', 'other') // 后端会自动识别
    formDataToSend.append('software_engineering_chapter', formData.software_engineering_chapter || '')
    formDataToSend.append('theme_category_id', formData.theme_category_id || '')
    formDataToSend.append('tags', JSON.stringify(formData.tags))
    formDataToSend.append('is_public', formData.is_public ? '1' : '0')

    await request.post('/ideological/resources/', formDataToSend, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    message.success('资源上传成功')
    visible.value = false
    resetForm()
    emit('success')
  } catch (error) {
    console.error('上传失败:', error)
    if (error.errors) {
      // 表单验证错误
      return
    }
    message.error(error.response?.data?.detail || '上传失败')
  } finally {
    uploading.value = false
  }
}

const resetForm = () => {
  Object.assign(formData, {
    title: '',
    description: '',
    software_engineering_chapter: null,
    theme_category_id: null,
    tags: [],
    is_public: true,
  })
  fileList.value = []
  formRef.value?.restoreValidation()
}

watch(() => props.visible, (val) => {
  if (!val) {
    resetForm()
  }
})
</script>
