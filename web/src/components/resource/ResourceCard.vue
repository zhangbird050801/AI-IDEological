<template>
  <n-card class="resource-card" hoverable @click="$emit('click', resource)">
    <template #cover>
      <div class="resource-cover" @click.stop="handleCoverClick">
        <!-- 图片预览 -->
        <img
          v-if="resource.resource_type === 'image' && resource.file_url"
          :src="getImageUrl"
          :alt="resource.title"
          class="preview-image"
          @error="handleImageError"
        />
        <!-- 文件图标 -->
        <div v-else class="file-icon" :style="{ background: getResourceBgColor(resource.resource_type) }">
          <n-icon size="48" color="white">
            <Icon :icon="getResourceIcon(resource.resource_type)" />
          </n-icon>
          <div class="resource-type-label">
            {{ getResourceTypeLabel(resource.resource_type) }}
          </div>
        </div>
      </div>
    </template>

    <template #header>
      <div class="resource-header">
        <n-ellipsis :line-clamp="2" :tooltip="{ width: 300 }">
          {{ resource.title }}
        </n-ellipsis>
      </div>
    </template>

    <div class="resource-content">
      <n-ellipsis v-if="resource.description" :line-clamp="2" class="resource-description">
        {{ resource.description }}
      </n-ellipsis>
      <n-text v-else depth="3" style="font-size: 12px;">暂无描述</n-text>

      <div class="resource-meta" style="margin-top: 12px;">
        <n-space size="small" wrap>
          <n-tag v-if="resource.software_engineering_chapter" size="small" type="info" :bordered="false">
            {{ resource.software_engineering_chapter }}
          </n-tag>
          <n-tag v-if="resource.ideological_theme" size="small" type="success" :bordered="false">
            {{ resource.ideological_theme }}
          </n-tag>
          <n-tag v-for="tag in resource.tags?.slice(0, 2)" :key="tag" size="small" :bordered="false">
            {{ tag }}
          </n-tag>
        </n-space>
      </div>

      <n-divider style="margin: 12px 0;" />

      <div class="resource-info">
        <n-space justify="end" size="small" align="center">
          <n-text v-if="resource.file_size" depth="3" style="font-size: 12px;">
            {{ formatFileSize(resource.file_size) }}
          </n-text>
        </n-space>
      </div>
    </div>

    <template #footer>
      <n-space justify="space-between" align="center">
        <n-space size="small">
          <n-button
            v-if="resource.file_url"
            size="small"
            text
            @click.stop="$emit('preview', resource)"
          >
            <template #icon>
              <n-icon><Icon icon="ant-design:eye-outlined" /></n-icon>
            </template>
            预览
          </n-button>
          <n-button
            v-if="resource.file_url"
            size="small"
            text
            @click.stop="$emit('download', resource)"
          >
            <template #icon>
              <n-icon><Icon icon="ant-design:download-outlined" /></n-icon>
            </template>
            下载
          </n-button>
          <n-button
            v-if="resource.external_url"
            size="small"
            text
            @click.stop="$emit('open-link', resource)"
          >
            <template #icon>
              <n-icon><Icon icon="ant-design:link-outlined" /></n-icon>
            </template>
            访问
          </n-button>
        </n-space>

        <n-dropdown
          trigger="hover"
          :options="actionOptions"
          @select="(key) => $emit('action', key, resource)"
        >
          <n-button size="small" text @click.stop>
            <template #icon>
              <n-icon><Icon icon="ant-design:more-outlined" /></n-icon>
            </template>
          </n-button>
        </n-dropdown>
      </n-space>
    </template>
  </n-card>
</template>

<script setup>
import { h, computed } from 'vue'
import { Icon } from '@iconify/vue'
import {
  NCard,
  NIcon,
  NSpace,
  NButton,
  NTag,
  NText,
  NEllipsis,
  NDivider,
  NDropdown,
} from 'naive-ui'

const props = defineProps({
  resource: {
    type: Object,
    required: true,
  },
  canEdit: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['click', 'preview', 'download', 'open-link', 'action'])

// 获取完整的图片 URL
const getImageUrl = computed(() => {
  if (!props.resource.file_url) return ''
  
  // 如果已经是完整 URL，直接返回
  if (props.resource.file_url.startsWith('http://') || props.resource.file_url.startsWith('https://')) {
    return props.resource.file_url
  }
  
  // 如果是相对路径，拼接当前域名
  const origin = window.location.origin
  return `${origin}${props.resource.file_url}`
})

const handleCoverClick = () => {
  // 点击封面图片时触发预览
  if (props.resource.resource_type === 'image' && props.resource.file_url) {
    emit('preview', props.resource)
  } else {
    emit('click', props.resource)
  }
}

const handleImageError = (e) => {
  // 图片加载失败时，隐藏图片，显示图标
  e.target.style.display = 'none'
}

const actionOptions = computed(() => {
  const options = [
    {
      label: '查看详情',
      key: 'view',
      icon: () => h(Icon, { icon: 'ant-design:eye-outlined' }),
    },
  ]

  if (props.canEdit) {
    options.push(
      {
        label: '编辑',
        key: 'edit',
        icon: () => h(Icon, { icon: 'ant-design:edit-outlined' }),
      },
      {
        label: '删除',
        key: 'delete',
        icon: () => h(Icon, { icon: 'ant-design:delete-outlined' }),
      }
    )
  }

  return options
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

const getResourceBgColor = (type) => {
  const colors = {
    video: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    audio: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    image: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    document: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    presentation: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    simulation: 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
    link: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
    other: 'linear-gradient(135deg, #d299c2 0%, #fef9d7 100%)',
  }
  return colors[type] || colors.other
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
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  return (bytes / (1024 * 1024 * 1024)).toFixed(1) + ' GB'
}
</script>

<style scoped>
.resource-card {
  height: 100%;
  transition: all 0.3s ease;
  cursor: pointer;
}

.resource-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.resource-cover {
  height: 180px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.file-icon {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.resource-type-label {
  color: white;
  font-size: 14px;
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.resource-header {
  font-weight: 600;
  font-size: 15px;
  line-height: 1.4;
}

.resource-content {
  min-height: 120px;
}

.resource-description {
  font-size: 13px;
  line-height: 1.6;
  color: #666;
}

.resource-meta {
  min-height: 32px;
}
</style>
