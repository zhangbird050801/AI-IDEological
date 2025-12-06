<template>
  <AppPage>
    <div class="resources-page">
      <!-- 页面头部 -->
      <div class="page-header">
        <div class="header-content">
          <div class="title-section">
            <h1>教学资源中心</h1>
            <p>整合微课素材、虚拟仿真资源等多元教学内容，助力课程思政教学实践</p>
          </div>

          <div class="actions-section">
            <n-space>
              <n-button type="primary" @click="showUploadModal">
                <template #icon>
                  <n-icon><Icon icon="ant-design:upload-outlined" /></n-icon>
                </template>
                上传资源
              </n-button>
              <n-button @click="showAddLinkModal">
                <template #icon>
                  <n-icon><Icon icon="ant-design:link-outlined" /></n-icon>
                </template>
                添加链接
              </n-button>
            </n-space>
          </div>
        </div>
      </div>

      <!-- 统计信息 -->
      <n-grid :cols="4" :x-gap="16" style="margin-bottom: 16px">
        <n-grid-item>
          <n-card :bordered="false" size="small">
            <n-statistic label="总资源数" :value="statistics.total" />
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card :bordered="false" size="small">
            <n-statistic label="微课视频" :value="statistics.video" />
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card :bordered="false" size="small">
            <n-statistic label="虚拟仿真" :value="statistics.simulation" />
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card :bordered="false" size="small">
            <n-statistic label="我的资源" :value="statistics.mine" />
          </n-card>
        </n-grid-item>
      </n-grid>

      <!-- 搜索和筛选区域 -->
      <n-card class="search-section" size="small">
        <n-form :model="searchForm" label-placement="left" :show-feedback="false">
          <n-grid :cols="4" :x-gap="16">
            <n-form-item-grid-item :span="1" label="关键词">
              <n-input
                v-model:value="searchForm.keyword"
                placeholder="搜索资源标题或描述"
                clearable
                @keyup.enter="handleSearch"
              >
                <template #prefix>
                  <n-icon><Icon icon="ant-design:search-outlined" /></n-icon>
                </template>
              </n-input>
            </n-form-item-grid-item>

            <n-form-item-grid-item :span="1" label="资源类型">
              <n-select
                v-model:value="searchForm.resource_type"
                placeholder="全部类型"
                :options="resourceTypeOptions"
                clearable
              />
            </n-form-item-grid-item>

            <n-form-item-grid-item :span="1" label="软件工程章节">
              <n-select
                v-model:value="searchForm.software_engineering_chapter"
                placeholder="全部章节"
                :options="chapterOptions"
                clearable
              />
            </n-form-item-grid-item>

            <n-form-item-grid-item :span="1" label="思政主题">
              <n-select
                v-model:value="searchForm.theme_category_id"
                placeholder="全部主题"
                :options="themeOptions"
                clearable
              />
            </n-form-item-grid-item>
          </n-grid>

          <n-space justify="end" style="margin-top: 12px">
            <n-button @click="resetSearch">重置</n-button>
            <n-button type="primary" @click="handleSearch">搜索</n-button>
          </n-space>
        </n-form>
      </n-card>

      <!-- 资源列表 -->
      <n-card title="资源列表" class="resources-list">
        <template #header-extra>
          <n-space>
            <n-button-group>
              <n-button :type="viewMode === 'grid' ? 'primary' : 'default'" @click="viewMode = 'grid'">
                <template #icon>
                  <n-icon><Icon icon="ant-design:appstore-outlined" /></n-icon>
                </template>
              </n-button>
              <n-button :type="viewMode === 'list' ? 'primary' : 'default'" @click="viewMode = 'list'">
                <template #icon>
                  <n-icon><Icon icon="ant-design:bars-outlined" /></n-icon>
                </template>
              </n-button>
            </n-button-group>
          </n-space>
        </template>

        <n-spin :show="loading">
          <!-- 网格视图 -->
          <div v-if="viewMode === 'grid'" class="grid-view">
            <n-grid :cols="3" :x-gap="16" :y-gap="16">
              <n-grid-item v-for="resource in resourcesList" :key="resource.id">
                <ResourceCard
                  :resource="resource"
                  :can-edit="canEditResource(resource)"
                  @click="viewResourceDetail(resource)"
                  @preview="previewResource(resource)"
                  @download="downloadResource(resource)"
                  @open-link="openExternalLink(resource)"
                  @action="handleResourceAction"
                />
              </n-grid-item>
            </n-grid>
          </div>

          <!-- 列表视图 -->
          <div v-else class="list-view">
            <n-list hoverable clickable>
              <n-list-item
                v-for="resource in resourcesList"
                :key="resource.id"
                @click="viewResourceDetail(resource)"
              >
                <template #prefix>
                  <n-avatar :style="{ background: getResourceBgColor(resource.resource_type) }">
                    <n-icon size="24" color="white">
                      <Icon :icon="getResourceIcon(resource.resource_type)" />
                    </n-icon>
                  </n-avatar>
                </template>

                <n-thing>
                  <template #header>
                    <n-space align="center">
                      <span>{{ resource.title }}</span>
                      <n-tag size="small" :type="getResourceTypeTagType(resource.resource_type)">
                        {{ getResourceTypeLabel(resource.resource_type) }}
                      </n-tag>
                    </n-space>
                  </template>
                  <template #description>
                    <n-space vertical :size="4">
                      <n-text depth="3">{{ resource.description || '暂无描述' }}</n-text>
                      <n-space :size="8">
                        <n-tag v-if="resource.software_engineering_chapter" size="small" type="info" :bordered="false">
                          {{ resource.software_engineering_chapter }}
                        </n-tag>
                        <n-tag v-if="resource.theme_name" size="small" type="success" :bordered="false">
                          {{ resource.theme_name }}
                        </n-tag>
                        <n-text v-if="resource.file_size" depth="3" style="font-size: 12px;">
                          {{ formatFileSize(resource.file_size) }}
                        </n-text>
                      </n-space>
                    </n-space>
                  </template>
                </n-thing>

                <template #suffix>
                  <n-space>
                    <n-button v-if="resource.file_url" size="small" @click.stop="previewResource(resource)">
                      预览
                    </n-button>
                    <n-button v-if="resource.file_url" size="small" @click.stop="downloadResource(resource)">
                      下载
                    </n-button>
                    <n-button v-if="resource.external_url" size="small" @click.stop="openExternalLink(resource)">
                      访问
                    </n-button>
                  </n-space>
                </template>
              </n-list-item>
            </n-list>
          </div>

          <!-- 空状态 -->
          <div v-if="!loading && resourcesList.length === 0" class="empty-state">
            <n-empty description="暂无资源数据" size="large">
              <template #icon>
                <n-icon size="80" color="#d0d0d0">
                  <Icon icon="ant-design:folder-open-outlined" />
                </n-icon>
              </template>
              <template #extra>
                <n-space vertical align="center" :size="16">
                  <p style="color: #999; margin: 16px 0;">
                    还没有上传任何教学资源，快来上传第一个资源吧！
                  </p>
                  <n-space>
                    <n-button type="primary" size="large" @click="showUploadModal">
                      <template #icon>
                        <n-icon><Icon icon="ant-design:upload-outlined" /></n-icon>
                      </template>
                      上传资源
                    </n-button>
                    <n-button size="large" @click="showAddLinkModal">
                      <template #icon>
                        <n-icon><Icon icon="ant-design:link-outlined" /></n-icon>
                      </template>
                      添加链接
                    </n-button>
                  </n-space>
                </n-space>
              </template>
            </n-empty>
          </div>
        </n-spin>

        <!-- 分页 -->
        <n-pagination
          v-if="resourcesList.length > 0"
          v-model:page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :item-count="pagination.itemCount"
          :show-size-picker="true"
          :page-sizes="[12, 24, 48]"
          @update:page="handlePageChange"
          @update:page-size="handlePageSizeChange"
          style="margin-top: 24px; justify-content: center"
        />
      </n-card>
    </div>

    <!-- 上传资源弹窗 -->
    <UploadResourceModal
      v-model:visible="uploadModalVisible"
      :chapter-options="chapterOptions"
      :theme-options="themeOptions"
      @success="handleUploadSuccess"
    />

    <!-- 添加链接弹窗 -->
    <AddLinkModal
      v-model:visible="addLinkModalVisible"
      :chapter-options="chapterOptions"
      :theme-options="themeOptions"
      @success="handleAddLinkSuccess"
    />

    <!-- 资源预览弹窗 -->
    <ResourcePreview
      v-model="previewModalVisible"
      :resource="currentResource"
      @download="downloadResource"
    />

    <!-- 资源详情弹窗 -->
    <ResourceDetailModal
      v-model:visible="detailModalVisible"
      :resource="currentResource"
      @edit="handleEdit"
      @delete="handleDelete"
      @download="downloadResource"
    />
  </AppPage>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useMessage, useDialog } from 'naive-ui'
import { Icon } from '@iconify/vue'
import {
  NGrid,
  NGridItem,
  NCard,
  NStatistic,
  NForm,
  NFormItemGridItem,
  NInput,
  NSelect,
  NButton,
  NButtonGroup,
  NSpace,
  NIcon,
  NSpin,
  NList,
  NListItem,
  NThing,
  NTag,
  NText,
  NEmpty,
  NPagination,
  NAvatar,
} from 'naive-ui'

import AppPage from '@/components/page/AppPage.vue'
import ResourceCard from '@/components/resource/ResourceCard.vue'
import ResourcePreview from '@/components/resource/ResourcePreview.vue'
import UploadResourceModal from './components/UploadResourceModal.vue'
import AddLinkModal from './components/AddLinkModal.vue'
import ResourceDetailModal from './components/ResourceDetailModal.vue'

import { request } from '@/utils'
import { themeCategoriesApi } from '@/api/ideological'

const message = useMessage()
const dialog = useDialog()

// 状态
const loading = ref(false)
const viewMode = ref('grid')
const resourcesList = ref([])
const currentResource = ref(null)

// 弹窗状态
const uploadModalVisible = ref(false)
const addLinkModalVisible = ref(false)
const previewModalVisible = ref(false)
const detailModalVisible = ref(false)

// 搜索表单
const searchForm = reactive({
  keyword: '',
  resource_type: null,
  software_engineering_chapter: null,
  theme_category_id: null,
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 12,
  itemCount: 0,
})

// 统计数据
const statistics = reactive({
  total: 0,
  video: 0,
  simulation: 0,
  mine: 0,
})

// 选项数据
const resourceTypeOptions = ref([
  { label: '微课视频', value: 'video' },
  { label: '文档资料', value: 'document' },
  { label: '演示文稿', value: 'presentation' },
  { label: '虚拟仿真', value: 'simulation' },
  { label: '图片素材', value: 'image' },
  { label: '音频资料', value: 'audio' },
  { label: '外部链接', value: 'link' },
  { label: '其他', value: 'other' },
])

const chapterOptions = ref([])
const themeOptions = ref([])

// 加载资源列表
const fetchResources = async () => {
  loading.value = true
  try {
    const params = {
      ...searchForm,
      page: pagination.page,
      page_size: pagination.pageSize,
    }

    const response = await request.get('/ideological/resources/', { params })
    const data = response?.data || response

    resourcesList.value = data?.items || []
    pagination.itemCount = data?.total || 0

    // 更新统计数据
    updateStatistics()
  } catch (error) {
    console.error('获取资源列表失败:', error)
    message.error('获取资源列表失败')
  } finally {
    loading.value = false
  }
}

// 更新统计数据
const updateStatistics = () => {
  statistics.total = pagination.itemCount
  statistics.video = resourcesList.value.filter(r => r.resource_type === 'video').length
  statistics.simulation = resourcesList.value.filter(r => r.resource_type === 'simulation').length
  // TODO: 从后端获取我的资源数量
  statistics.mine = 0
}

// 加载选项数据
const fetchOptions = async () => {
  try {
    // 加载章节选项
    const chaptersRes = await request.get('/ideological/cases/chapters/list')
    chapterOptions.value = (chaptersRes?.data || chaptersRes || []).map(item => ({
      label: item,
      value: item,
    }))

    // 加载主题选项
    const themesResponse = await themeCategoriesApi.getList()
    console.log('📥 [ResourcesNew] 主题分类API响应:', themesResponse)
    
    let themesData = themesResponse?.data?.data || themesResponse?.data || themesResponse
    console.log('📦 [ResourcesNew] 解包后的数据:', themesData)
    
    if (!Array.isArray(themesData)) {
      console.error('❗ [ResourcesNew] 主题数据不是数组')
      throw new Error('主题数据格式错误')
    }
    
    themeOptions.value = themesData
      .filter(item => item.is_active && item.parent_id !== null)
      .map(item => ({
        label: item.name,
        value: item.id,  // 使用ID作为值
      }))
    
    console.log('✅ [ResourcesNew] 处理后的主题选项:', themeOptions.value)
  } catch (error) {
    console.error('❗ [ResourcesNew] 加载选项失败:', error)
    // fallback数据
    themeOptions.value = [
      { label: '工匠精神', value: 5 },
      { label: '创新精神', value: 6 },
      { label: '团队协作', value: 11 }
    ]
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchResources()
}

// 重置搜索
const resetSearch = () => {
  Object.assign(searchForm, {
    keyword: '',
    resource_type: null,
    software_engineering_chapter: null,
    theme_category_id: null,
  })
  handleSearch()
}

// 分页
const handlePageChange = (page) => {
  pagination.page = page
  fetchResources()
}

const handlePageSizeChange = (pageSize) => {
  pagination.pageSize = pageSize
  pagination.page = 1
  fetchResources()
}

// 显示上传弹窗
const showUploadModal = () => {
  uploadModalVisible.value = true
}

// 显示添加链接弹窗
const showAddLinkModal = () => {
  addLinkModalVisible.value = true
}

// 上传成功
const handleUploadSuccess = () => {
  message.success('资源上传成功')
  fetchResources()
}

// 添加链接成功
const handleAddLinkSuccess = () => {
  message.success('链接添加成功')
  fetchResources()
}

// 查看资源详情
const viewResourceDetail = (resource) => {
  currentResource.value = resource
  detailModalVisible.value = true
}

// 预览资源
const previewResource = (resource) => {
  currentResource.value = resource
  previewModalVisible.value = true
}

// 下载资源
const downloadResource = async (resource) => {
  if (!resource.file_url) {
    message.warning('该资源没有可下载的文件')
    return
  }

  try {
    // 获取完整的文件 URL
    let fileUrl = resource.file_url
    if (!fileUrl.startsWith('http://') && !fileUrl.startsWith('https://')) {
      const origin = window.location.origin
      fileUrl = `${origin}${fileUrl}`
    }

    // 创建一个隐藏的a标签来触发下载
    const link = document.createElement('a')
    link.href = fileUrl
    link.download = resource.title
    link.target = '_blank'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    message.success('开始下载')

    // 更新使用次数
    await request.get(`/ideological/resources/${resource.id}`)
  } catch (error) {
    console.error('下载失败:', error)
    message.error('下载失败')
  }
}

// 打开外部链接
const openExternalLink = (resource) => {
  if (resource.external_url) {
    window.open(resource.external_url, '_blank')
    // 更新使用次数
    request.get(`/ideological/resources/${resource.id}`).catch(() => {})
  }
}

// 资源操作
const handleResourceAction = (action, resource) => {
  currentResource.value = resource

  switch (action) {
    case 'view':
      viewResourceDetail(resource)
      break
    case 'edit':
      handleEdit(resource)
      break
    case 'delete':
      handleDelete(resource)
      break
  }
}

// 编辑资源
const handleEdit = (resource) => {
  // TODO: 实现编辑功能
  message.info('编辑功能开发中')
}

// 删除资源
const handleDelete = (resource) => {
  dialog.warning({
    title: '确认删除',
    content: `确定要删除资源"${resource.title}"吗？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await request.delete(`/ideological/resources/${resource.id}`)
        message.success('删除成功')
        fetchResources()
      } catch (error) {
        console.error('删除失败:', error)
        message.error('删除失败')
      }
    },
  })
}

// 判断是否可以编辑资源
const canEditResource = (resource) => {
  // TODO: 根据用户权限判断
  return true
}

// 工具函数
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

// 初始化
onMounted(() => {
  fetchOptions()
  fetchResources()
})
</script>

<style scoped>
.resources-page {
  padding: 0;
}

.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 32px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-section h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
}

.title-section p {
  margin: 0;
  opacity: 0.9;
  font-size: 14px;
}

.search-section {
  margin-bottom: 16px;
}

.grid-view {
  min-height: 400px;
}

.list-view {
  min-height: 400px;
}

.empty-state {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
}

/* 资源卡片悬停效果 */
.grid-view :deep(.n-card) {
  transition: all 0.3s ease;
  cursor: pointer;
}

.grid-view :deep(.n-card:hover) {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

/* 列表项悬停效果 */
.list-view :deep(.n-list-item) {
  transition: all 0.3s ease;
  border-radius: 8px;
  margin-bottom: 8px;
}

.list-view :deep(.n-list-item:hover) {
  background-color: rgba(102, 126, 234, 0.05);
  transform: translateX(4px);
}

/* 统计卡片样式 */
:deep(.n-statistic) {
  text-align: center;
}

:deep(.n-statistic .n-statistic-value) {
  font-size: 28px;
  font-weight: 600;
  color: var(--n-primary-color);
}

/* 搜索区域样式优化 */
.search-section {
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .title-section h1 {
    font-size: 22px;
  }

  .grid-view {
    grid-template-columns: 1fr !important;
  }
}
</style>
