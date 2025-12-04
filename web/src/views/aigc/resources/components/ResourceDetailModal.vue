<template>
  <n-modal
    v-model:show="visible"
    preset="card"
    style="width: 800px; max-height: 80vh"
    :title="resource?.title"
    :bordered="false"
    :segmented="{ content: 'soft' }"
  >
    <n-scrollbar style="max-height: 60vh" v-if="resource">
      <n-space vertical size="large">
        <!-- 资源预览区 -->
        <div class="resource-preview-section">
          <!-- 图片预览 -->
          <div v-if="resource.resource_type === 'image' && resource.file_url" class="preview-container">
            <img :src="getFileUrl(resource.file_url)" :alt="resource.title" style="max-width: 100%; border-radius: 8px;" />
          </div>

          <!-- 视频预览 -->
          <div v-else-if="resource.resource_type === 'video' && resource.file_url" class="preview-container">
            <video
              controls
              style="width: 100%; max-height: 400px; border-radius: 8px;"
              :src="getFileUrl(resource.file_url)"
            >
              您的浏览器不支持视频播放
            </video>
          </div>

          <!-- 其他类型显示图标 -->
          <div v-else class="preview-placeholder">
            <n-icon size="64" :color="getResourceColor(resource.resource_type)">
              <Icon :icon="getResourceIcon(resource.resource_type)" />
            </n-icon>
            <n-text style="margin-top: 12px;">
              {{ getResourceTypeLabel(resource.resource_type) }}
            </n-text>
          </div>
        </div>

        <!-- 基本信息 -->
        <n-descriptions :column="2" bordered size="small">
          <n-descriptions-item label="资源类型">
            <n-tag size="small" :type="getResourceTypeTagType(resource.resource_type)">
              {{ getResourceTypeLabel(resource.resource_type) }}
            </n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="文件大小" v-if="resource.file_size">
            {{ formatFileSize(resource.file_size) }}
          </n-descriptions-item>
          <n-descriptions-item label="文件格式" v-if="resource.file_format">
            {{ resource.file_format.toUpperCase() }}
          </n-descriptions-item>
          <n-descriptions-item label="上传者" v-if="resource.uploader_name">
            {{ resource.uploader_name }}
          </n-descriptions-item>
          <n-descriptions-item label="上传时间" :span="resource.uploader_name ? 1 : 2">
            {{ formatDate(resource.created_at) }}
          </n-descriptions-item>
        </n-descriptions>

        <!-- 教学信息 -->
        <n-card title="教学信息" size="small" v-if="resource.software_engineering_chapter || resource.ideological_theme">
          <n-descriptions :column="2" size="small">
            <n-descriptions-item label="软件工程章节" v-if="resource.software_engineering_chapter">
              <n-tag type="info" size="small">{{ resource.software_engineering_chapter }}</n-tag>
            </n-descriptions-item>
            <n-descriptions-item label="思政主题" v-if="resource.ideological_theme">
              <n-tag type="success" size="small">{{ resource.ideological_theme }}</n-tag>
            </n-descriptions-item>
          </n-descriptions>
        </n-card>

        <!-- 资源描述 -->
        <n-card title="资源描述" size="small" v-if="resource.description">
          <n-text>{{ resource.description }}</n-text>
        </n-card>

        <!-- 标签 -->
        <n-card title="标签" size="small" v-if="resource.tags && resource.tags.length > 0">
          <n-space :size="8">
            <n-tag v-for="tag in resource.tags" :key="tag" size="small">
              {{ tag }}
            </n-tag>
          </n-space>
        </n-card>

        <!-- 外部链接 -->
        <n-card title="外部链接" size="small" v-if="resource.external_url">
          <n-space vertical :size="8">
            <n-text depth="3">{{ resource.external_url }}</n-text>
            <n-button size="small" type="primary" @click="openLink">
              <template #icon>
                <n-icon><Icon icon="ant-design:export-outlined" /></n-icon>
              </template>
              访问链接
            </n-button>
          </n-space>
        </n-card>
      </n-space>
    </n-scrollbar>

    <template #footer>
      <n-space justify="space-between">
        <n-space>
          <n-button v-if="resource?.file_url" @click="$emit('download', resource)">
            <template #icon>
              <n-icon><Icon icon="ant-design:download-outlined" /></n-icon>
            </template>
            下载
          </n-button>
        </n-space>
        <n-space>
          <n-button v-if="canEdit" @click="$emit('edit', resource)">
            编辑
          </n-button>
          <n-button v-if="canEdit" type="error" @click="$emit('delete', resource)">
            删除
          </n-button>
          <n-button @click="visible = false">关闭</n-button>
        </n-space>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup>
import { computed } from 'vue'
import { Icon } from '@iconify/vue'
import {
  NModal,
  NScrollbar,
  NSpace,
  NCard,
  NDescriptions,
  NDescriptionsItem,
  NTag,
  NText,
  NButton,
  NIcon,
} from 'naive-ui'

const props = defineProps({
  visible: Boolean,
  resource: Object,
  canEdit: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:visible', 'edit', 'delete', 'download'])

const visible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val),
})

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

const openLink = () => {
  if (props.resource?.external_url) {
    window.open(props.resource.external_url, '_blank')
  }
}

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

const getResourceColor = (type) => {
  const colors = {
    video: '#667eea',
    audio: '#f093fb',
    image: '#4facfe',
    document: '#43e97b',
    presentation: '#fa709a',
    simulation: '#30cfd0',
    link: '#a8edea',
    other: '#d299c2',
  }
  return colors[type] || '#999'
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

const getResourceTypeTagType = (type) => {
  const types = {
    video: 'info',
    audio: 'warning',
    image: 'success',
    document: 'default',
    presentation: 'error',
    simulation: 'info',
    link: 'success',
    other: 'default',
  }
  return types[type] || 'default'
}

const formatFileSize = (bytes) => {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  return (bytes / (1024 * 1024 * 1024)).toFixed(1) + ' GB'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}
</script>

<style scoped>
.resource-preview-section {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
  background: #f5f5f5;
  border-radius: 8px;
  padding: 16px;
}

.preview-container {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.preview-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
}
</style>
