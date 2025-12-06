<template>
  <n-modal
    v-model:show="visible"
    preset="card"
    :style="{ width: modalWidth }"
    :title="resource?.title"
    :bordered="false"
    :segmented="{ content: 'soft' }"
  >
    <n-spin :show="loading">
      <div class="resource-preview-container">
        <!-- 图片预览 -->
        <div v-if="resource?.resource_type === 'image' && resource?.file_url" class="image-preview">
          <img :src="getFileUrl(resource.file_url)" :alt="resource.title" style="max-width: 100%; height: auto;" />
        </div>

        <!-- 视频预览 -->
        <div v-else-if="resource?.resource_type === 'video' && resource?.file_url" class="video-preview">
          <video
            controls
            style="width: 100%; max-height: 500px;"
            :src="getFileUrl(resource.file_url)"
          >
            您的浏览器不支持视频播放
          </video>
        </div>

        <!-- PDF预览 -->
        <div v-else-if="resource?.file_format === 'pdf' && resource?.file_url" class="pdf-preview">
          <iframe
            :src="getFileUrl(resource.file_url)"
            style="width: 100%; height: 600px; border: none;"
          ></iframe>
        </div>

        <!-- 文档预览提示 -->
        <div v-else-if="['document', 'presentation'].includes(resource?.resource_type)" class="document-preview">
          <n-result
            status="info"
            title="文档预览"
            description="此类型文件需要下载后查看"
          >
            <template #icon>
              <n-icon size="64" color="#2080f0">
                <Icon :icon="getResourceIcon(resource.resource_type)" />
              </n-icon>
            </template>
            <template #footer>
              <n-space>
                <n-button type="primary" @click="$emit('download', resource)">
                  <template #icon>
                    <n-icon><Icon icon="ant-design:download-outlined" /></n-icon>
                  </template>
                  下载文件
                </n-button>
              </n-space>
            </template>
          </n-result>
        </div>

        <!-- 外部链接 -->
        <div v-else-if="resource?.external_url" class="link-preview">
          <n-result
            status="info"
            title="外部资源"
            :description="resource.external_url"
          >
            <template #icon>
              <n-icon size="64" color="#18a058">
                <Icon icon="ant-design:link-outlined" />
              </n-icon>
            </template>
            <template #footer>
              <n-button type="primary" @click="openLink">
                <template #icon>
                  <n-icon><Icon icon="ant-design:export-outlined" /></n-icon>
                </template>
                访问链接
              </n-button>
            </template>
          </n-result>
        </div>

        <!-- 其他类型 -->
        <div v-else class="default-preview">
          <n-result
            status="info"
            title="无法预览"
            description="此类型文件不支持在线预览，请下载后查看"
          >
            <template #icon>
              <n-icon size="64" color="#999">
                <Icon icon="ant-design:file-outlined" />
              </n-icon>
            </template>
            <template #footer>
              <n-button v-if="resource?.file_url" type="primary" @click="$emit('download', resource)">
                <template #icon>
                  <n-icon><Icon icon="ant-design:download-outlined" /></n-icon>
                </template>
                下载文件
              </n-button>
            </template>
          </n-result>
        </div>

        <!-- 资源信息 -->
        <n-divider />
        <n-descriptions :column="2" size="small" bordered>
          <n-descriptions-item label="资源类型">
            <n-tag size="small">{{ getResourceTypeLabel(resource?.resource_type) }}</n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="文件大小" v-if="resource?.file_size">
            {{ formatFileSize(resource.file_size) }}
          </n-descriptions-item>
          <n-descriptions-item label="软件工程章节" v-if="resource?.software_engineering_chapter">
            {{ resource.software_engineering_chapter }}
          </n-descriptions-item>
          <n-descriptions-item label="思政主题" v-if="resource?.theme_name">
            {{ resource.theme_name }}
          </n-descriptions-item>
          <n-descriptions-item label="上传时间" :span="2">
            {{ formatDate(resource?.created_at) }}
          </n-descriptions-item>
        </n-descriptions>

        <div v-if="resource?.description" style="margin-top: 16px;">
          <n-text strong>资源描述：</n-text>
          <n-text depth="3" style="display: block; margin-top: 8px;">
            {{ resource.description }}
          </n-text>
        </div>

        <div v-if="resource?.tags && resource.tags.length > 0" style="margin-top: 16px;">
          <n-text strong>标签：</n-text>
          <n-space style="margin-top: 8px;" :size="8">
            <n-tag v-for="tag in resource.tags" :key="tag" size="small">
              {{ tag }}
            </n-tag>
          </n-space>
        </div>
      </div>
    </n-spin>

    <template #footer>
      <n-space justify="end">
        <n-button @click="visible = false">关闭</n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Icon } from '@iconify/vue'
import {
  NModal,
  NSpin,
  NResult,
  NButton,
  NIcon,
  NSpace,
  NDivider,
  NDescriptions,
  NDescriptionsItem,
  NTag,
  NText,
} from 'naive-ui'

const props = defineProps({
  modelValue: Boolean,
  resource: Object,
})

const emit = defineEmits(['update:modelValue', 'download'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const loading = ref(false)

// 获取完整的文件 URL
const getFileUrl = (url) => {
  if (!url) return ''
  
  // 如果已经是完整 URL，直接返回
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }
  
  // 如果是相对路径，拼接当前域名
  const origin = window.location.origin
  return `${origin}${url}`
}

const modalWidth = computed(() => {
  if (!props.resource) return '800px'
  const type = props.resource.resource_type
  if (type === 'video' || type === 'image') return '900px'
  return '800px'
})

const getResourceIcon = (type) => {
  const icons = {
    video: 'ant-design:video-camera-outlined',
    audio: 'ant-design:audio-outlined',
    image: 'ant-design:picture-outlined',
    document: 'ant-design:file-text-outlined',
    presentation: 'ant-design:file-ppt-outlined',
    simulation: 'ant-design:experiment-outlined',
    link: 'ant-design:link-outlined',
    other: 'ant-design:file-outlined',
  }
  return icons[type] || icons.other
}

const getResourceTypeLabel = (type) => {
  const labels = {
    video: '微课视频',
    audio: '音频',
    image: '图片',
    document: '文档',
    presentation: '演示文稿',
    simulation: '虚拟仿真',
    link: '外部链接',
    other: '其他',
  }
  return labels[type] || '未知'
}

const formatFileSize = (bytes) => {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
  return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const openLink = () => {
  if (props.resource?.external_url) {
    window.open(props.resource.external_url, '_blank')
  }
}
</script>

<style scoped>
.resource-preview-container {
  min-height: 200px;
}

.image-preview,
.video-preview,
.pdf-preview {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 16px;
}

.image-preview img {
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>
