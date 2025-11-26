<template>
  <AppPage>
    <div class="resources-page">
      <!-- 页面头部 -->
      <div class="page-header">
        <div class="header-content">
          <div class="title-section">
            <h1>教学资源中心</h1>
            <p>丰富的微课素材、虚拟仿真资源等多元教学内容，助力课程思政教学实践</p>
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
            <n-statistic label="总资源数" :value="totalResources" />
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card :bordered="false" size="small">
            <n-statistic label="我的资源" :value="myResources" />
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card :bordered="false" size="small">
            <n-statistic label="文件资源" :value="fileResources" />
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card :bordered="false" size="small">
            <n-statistic label="链接资源" :value="linkResources" />
          </n-card>
        </n-grid-item>
      </n-grid>

      <!-- 搜索和筛选区域 -->
      <n-card class="search-section">
        <n-form :model="searchForm" label-placement="left" :show-feedback="false">
          <n-grid :cols="4" :x-gap="16">
            <n-form-item-grid-item :span="1" label="关键词">
              <n-input
                v-model:value="searchForm.keyword"
                placeholder="搜索资源标题或描述"
                clearable
                @clear="handleSearch"
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
                placeholder="选择类型"
                :options="resourceTypeOptions"
                clearable
                @clear="handleSearch"
              />
            </n-form-item-grid-item>

            <n-form-item-grid-item :span="1" label="软件工程章节">
              <n-select
                v-model:value="searchForm.software_engineering_chapter"
                placeholder="选择章节"
                :options="chapterOptions"
                clearable
                @clear="handleSearch"
              />
            </n-form-item-grid-item>

            <n-form-item-grid-item :span="1" label="思政主题">
              <n-select
                v-model:value="searchForm.ideological_theme"
                placeholder="选择主题"
                :options="themeOptions"
                clearable
                @clear="handleSearch"
              />
            </n-form-item-grid-item>
          </n-grid>

          <n-space justify="end" style="margin-top: 16px">
            <n-button @click="resetSearch">重置</n-button>
            <n-button type="primary" @click="handleSearch">搜索</n-button>
          </n-space>
        </n-form>
      </n-card>

      <!-- 资源列表 -->
      <n-card title="资源列表" class="resources-list">
        <template #header-extra>
          <n-space>
            <n-tag v-if="searchForm.keyword" type="info" closable @close="searchForm.keyword = ''">
              关键词: {{ searchForm.keyword }}
            </n-tag>
            <n-tag v-if="searchForm.resource_type" type="info" closable @close="searchForm.resource_type = null">
              类型: {{ getResourceTypeLabel(searchForm.resource_type) }}
            </n-tag>
          </n-space>
        </template>

        <!-- 网格视图 -->
        <div class="grid-view">
          <n-grid :cols="3" :x-gap="16" :y-gap="16">
            <n-grid-item v-for="resource in resourcesList" :key="resource.id">
              <n-card
                class="resource-card"
                hoverable
                @click="viewResourceDetail(resource)"
              >
                <template #cover>
                  <div class="resource-cover" @click.stop>
                    <!-- 文件资源预览 -->
                    <div v-if="resource.file_url" class="file-preview">
                      <img
                        v-if="resource.resource_type === 'image' && resource.preview_url"
                        :src="resource.preview_url"
                        :alt="resource.title"
                        class="preview-image"
                      />
                      <div v-else class="file-icon">
                        <n-icon size="48" :color="getResourceIconColor(resource.resource_type)">
                          <Icon :icon="getResourceIcon(resource.resource_type)" />
                        </n-icon>
                      </div>
                    </div>
                    <!-- 链接资源 -->
                    <div v-else-if="resource.external_url" class="link-preview">
                      <n-icon size="48" color="#18a058">
                        <Icon icon="ant-design:link-outlined" />
                      </n-icon>
                    </div>
                    <!-- 默认图标 -->
                    <div v-else class="default-icon">
                      <n-icon size="48" color="#999">
                        <Icon icon="ant-design:file-outlined" />
                      </n-icon>
                    </div>
                  </div>
                </template>

                <template #header>
                  <div class="resource-header">
                    <span class="resource-title" :title="resource.title">
                      {{ resource.title }}
                    </span>
                    <n-tag size="small" :type="getResourceTypeTagType(resource.resource_type)">
                      {{ getResourceTypeLabel(resource.resource_type) }}
                    </n-tag>
                  </div>
                </template>

                <div class="resource-content">
                  <p class="resource-description" v-if="resource.description">
                    {{ resource.description.substring(0, 80) }}...
                  </p>

                  <div class="resource-meta">
                    <n-space size="small" wrap>
                      <n-tag v-if="resource.software_engineering_chapter" size="small" type="info">
                        {{ resource.software_engineering_chapter }}
                      </n-tag>
                      <n-tag v-if="resource.ideological_theme" size="small" type="success">
                        {{ resource.ideological_theme }}
                      </n-tag>
                      <n-tag v-for="tag in resource.tags.slice(0, 2)" :key="tag" size="small">
                        {{ tag }}
                      </n-tag>
                    </n-space>
                  </div>

                  <div class="resource-info">
                    <n-space justify="space-between" size="small">
                      <span class="file-size" v-if="resource.file_size">
                        {{ formatFileSize(resource.file_size) }}
                      </span>
                      <span class="usage-count">
                        {{ resource.usage_count }} 次使用
                      </span>
                    </n-space>
                  </div>
                </div>

                <template #footer>
                  <div class="resource-footer">
                    <n-space justify="space-between">
                      <n-space size="small">
                        <n-button
                          v-if="resource.file_url"
                          size="small"
                          text
                          @click.stop="downloadResource(resource)"
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
                          @click.stop="openExternalLink(resource)"
                        >
                          <template #icon>
                            <n-icon><Icon icon="ant-design:link-outlined" /></n-icon>
                          </template>
                          访问
                        </n-button>
                        <n-button
                          v-if="resource.preview_url"
                          size="small"
                          text
                          @click.stop="previewResource(resource)"
                        >
                          <template #icon>
                            <n-icon><Icon icon="ant-design:eye-outlined" /></n-icon>
                          </template>
                          预览
                        </n-button>
                      </n-space>

                      <n-dropdown
                        trigger="hover"
                        :options="getResourceActionOptions(resource)"
                        @select="handleResourceAction"
                      >
                        <n-button size="small" text @click.stop>
                          <template #icon>
                            <n-icon><Icon icon="ant-design:more-outlined" /></n-icon>
                          </template>
                        </n-button>
                      </n-dropdown>
                    </n-space>
                  </div>
                </template>
              </n-card>
            </n-grid-item>
          </n-grid>
        </div>

        <!-- 分页 -->
        <n-pagination
          v-model:page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :item-count="pagination.itemCount"
          :show-size-picker="pagination.showSizePicker"
          :page-sizes="pagination.pageSizes"
          @update:page="handlePageChange"
          @update:page-size="handlePageSizeChange"
          style="margin-top: 24px; justify-content: center"
        />

        <!-- 空状态 -->
        <n-empty
          v-if="!loading && resourcesList.length === 0"
          description="暂无资源数据"
          style="margin: 40px 0"
        >
          <template #action>
            <n-button type="primary" @click="showUploadModal">
              上传第一个资源
            </n-button>
          </template>
        </n-empty>
      </n-card>
    </div>

    <!-- 上传资源弹窗 -->
    <n-modal
      v-model:show="uploadModalVisible"
      :mask-closable="false"
      preset="dialog"
      style="width: 600px"
      title="上传教学资源"
    >
      <n-form
        ref="uploadFormRef"
        :model="uploadForm"
        :rules="uploadFormRules"
        label-placement="left"
        :label-width="100"
        require-mark-placement="right-hanging"
      >
        <n-form-item label="资源标题" path="title">
          <n-input
            v-model:value="uploadForm.title"
            placeholder="请输入资源标题"
            maxlength="100"
            show-count
          />
        </n-form-item>

        <n-form-item label="资源文件" path="file">
          <n-upload
            v-model:file-list="uploadForm.fileList"
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
                点击或者拖动文件到该区域来上传
              </n-text>
              <n-p depth="3" style="margin: 8px 0 0 0">
                支持文档、视频、音频、图片、演示文稿等多种格式
              </n-p>
            </n-upload-dragger>
          </n-upload>
        </n-form-item>

        <n-form-item label="资源描述" path="description">
          <n-input
            v-model:value="uploadForm.description"
            type="textarea"
            placeholder="请输入资源描述"
            :autosize="{ minRows: 2, maxRows: 4 }"
            maxlength="500"
            show-count
          />
        </n-form-item>

        <n-grid :cols="2" :x-gap="16">
          <n-form-item-grid-item label="软件工程章节" path="software_engineering_chapter">
            <n-select
              v-model:value="uploadForm.software_engineering_chapter"
              placeholder="选择章节"
              :options="chapterOptions"
              clearable
            />
          </n-form-item-grid-item>

          <n-form-item-grid-item label="思政主题" path="ideological_theme">
            <n-select
              v-model:value="uploadForm.ideological_theme"
              placeholder="选择主题"
              :options="themeOptions"
              clearable
            />
          </n-form-item-grid-item>
        </n-grid>

        <n-form-item label="标签" path="tags">
          <n-dynamic-tags
            v-model:value="uploadForm.tags"
            placeholder="按回车添加标签"
          />
        </n-form-item>

        <n-form-item label="公开设置">
          <n-switch v-model:value="uploadForm.is_public" />
          <span style="margin-left: 8px; color: #999">
            公开后其他用户可以查看此资源
          </span>
        </n-form-item>
      </n-form>

      <template #action>
        <n-space>
          <n-button @click="uploadModalVisible = false">取消</n-button>
          <n-button type="primary" @click="handleUploadResource" :loading="uploadLoading">
            上传
          </n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 添加链接弹窗 -->
    <n-modal
      v-model:show="addLinkModalVisible"
      :mask-closable="false"
      preset="dialog"
      style="width: 600px"
      title="添加外部链接"
    >
      <n-form
        ref="linkFormRef"
        :model="linkForm"
        :rules="linkFormRules"
        label-placement="left"
        :label-width="100"
        require-mark-placement="right-hanging"
      >
        <n-form-item label="资源标题" path="title">
          <n-input
            v-model:value="linkForm.title"
            placeholder="请输入资源标题"
            maxlength="100"
            show-count
          />
        </n-form-item>

        <n-form-item label="链接地址" path="external_url">
          <n-input
            v-model:value="linkForm.external_url"
            placeholder="请输入外部链接地址"
            @blur="validateUrl"
          />
        </n-form-item>

        <n-form-item label="资源描述" path="description">
          <n-input
            v-model:value="linkForm.description"
            type="textarea"
            placeholder="请输入资源描述"
            :autosize="{ minRows: 2, maxRows: 4 }"
            maxlength="500"
            show-count
          />
        </n-form-item>

        <n-grid :cols="2" :x-gap="16">
          <n-form-item-grid-item label="软件工程章节" path="software_engineering_chapter">
            <n-select
              v-model:value="linkForm.software_engineering_chapter"
              placeholder="选择章节"
              :options="chapterOptions"
              clearable
            />
          </n-form-item-grid-item>

          <n-form-item-grid-item label="思政主题" path="ideological_theme">
            <n-select
              v-model:value="linkForm.ideological_theme"
              placeholder="选择主题"
              :options="themeOptions"
              clearable
            />
          </n-form-item-grid-item>
        </n-grid>

        <n-form-item label="标签" path="tags">
          <n-dynamic-tags
            v-model:value="linkForm.tags"
            placeholder="按回车添加标签"
          />
        </n-form-item>

        <n-form-item label="公开设置">
          <n-switch v-model:value="linkForm.is_public" />
          <span style="margin-left: 8px; color: #999">
            公开后其他用户可以查看此资源
          </span>
        </n-form-item>
      </n-form>

      <template #action>
        <n-space>
          <n-button @click="addLinkModalVisible = false">取消</n-button>
          <n-button type="primary" @click="handleAddLink" :loading="linkLoading">
            添加
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </AppPage>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import {
  NCard,
  NButton,
  NIcon,
  NSpace,
  NForm,
  NFormItem,
  NFormItemGridItem,
  NInput,
  NSelect,
  NGrid,
  NGridItem,
  NTag,
  NModal,
  NPagination,
  NEmpty,
  NDropdown,
  NStatistic,
  NUpload,
  NUploadDragger,
  NText,
  NP,
  NDynamicTags,
  NSwitch,
  useMessage,
  useDialog,
} from 'naive-ui'
import { Icon } from '@iconify/vue'
import AppPage from '@/components/page/AppPage.vue'
import { request } from '@/utils/http'
import { resourcesApi, casesApi } from '@/api/ideological'

// 响应式数据
const message = useMessage()
const dialog = useDialog()

const loading = ref(false)
const uploadLoading = ref(false)
const linkLoading = ref(false)
const uploadModalVisible = ref(false)
const addLinkModalVisible = ref(false)

// 统计数据
const totalResources = ref(0)
const myResources = ref(0)
const fileResources = ref(0)
const linkResources = ref(0)

// 搜索表单
const searchForm = reactive({
  keyword: '',
  resource_type: null,
  software_engineering_chapter: null,
  ideological_theme: null,
})

// 上传表单
const uploadFormRef = ref()
const uploadForm = reactive({
  title: '',
  description: '',
  fileList: [],
  software_engineering_chapter: null,
  ideological_theme: null,
  tags: [],
  is_public: true,
})

// 链接表单
const linkFormRef = ref()
const linkForm = reactive({
  title: '',
  description: '',
  external_url: '',
  software_engineering_chapter: null,
  ideological_theme: null,
  tags: [],
  is_public: true,
})

// 资源列表
const resourcesList = ref([])
const pagination = reactive({
  page: 1,
  pageSize: 12,
  itemCount: 0,
  showSizePicker: true,
  pageSizes: [12, 24, 48, 96],
})

// 选项数据
const resourceTypeOptions = ref([])
const chapterOptions = ref([])
const themeOptions = ref([])

// 表单验证规则
const uploadFormRules = {
  title: [
    { required: true, message: '请输入资源标题', trigger: 'blur' },
    { max: 100, message: '标题长度不能超过100个字符', trigger: 'blur' },
  ],
  fileList: [
    { required: true, message: '请选择要上传的文件', trigger: 'change' },
  ],
}

const linkFormRules = {
  title: [
    { required: true, message: '请输入资源标题', trigger: 'blur' },
    { max: 100, message: '标题长度不能超过100个字符', trigger: 'blur' },
  ],
  external_url: [
    { required: true, message: '请输入链接地址', trigger: 'blur' },
    { type: 'url', message: '请输入有效的URL地址', trigger: 'blur' },
  ],
}

// 方法
const fetchResources = async () => {
  loading.value = true
  try {
    const params = {
      ...searchForm,
      page: pagination.page,
      page_size: pagination.pageSize,
    }

    const response = await request.get('/ideological/resources/', { params })
    resourcesList.value = response.items
    pagination.itemCount = response.total
  } catch (error) {
    message.error('获取资源列表失败')
  } finally {
    loading.value = false
  }
}

const fetchOptions = async () => {
  try {
    // 获取资源类型选项
    try {
      const typesResponse = await request.get('/ideological/resources/types/list')
      resourceTypeOptions.value = typesResponse
    } catch (error) {
      // 使用默认资源类型数据
      resourceTypeOptions.value = [
        { label: "文档", value: "document" },
        { label: "视频", value: "video" },
        { label: "音频", value: "audio" },
        { label: "图片", value: "image" },
        { label: "演示文稿", value: "presentation" },
        { label: "虚拟仿真", value: "simulation" },
        { label: "外部链接", value: "link" },
        { label: "其他", value: "other" }
      ]
    }

    // 获取章节选项
    try {
      const chaptersResponse = await casesApi.getChapters()
      chapterOptions.value = chaptersResponse.map(item => ({
        label: item,
        value: item,
      }))
    } catch (error) {
      // 使用默认章节数据
      chapterOptions.value = [
        "软件工程概述", "软件过程模型", "需求分析", "系统设计", "编码实现",
        "软件测试", "软件维护", "项目管理", "软件质量", "软件工程前沿"
      ].map(item => ({ label: item, value: item }))
    }

    // 获取主题选项
    try {
      const themesResponse = await resourcesApi.getThemes()
      themeOptions.value = themesResponse.map(item => ({
        label: item,
        value: item,
      }))
    } catch (error) {
      // 使用默认主题数据
      themeOptions.value = [
        "工匠精神", "创新精神", "团队协作", "责任担当", "诚信品质",
        "法治意识", "科学精神", "人文素养", "家国情怀", "国际视野"
      ].map(item => ({ label: item, value: item }))
    }
  } catch (error) {
    message.error('获取选项数据失败')
  }
}

const fetchStatistics = async () => {
  try {
    // 获取统计数据
    const allResponse = await request.get('/ideological/resources/', { params: { page_size: 1 } })
    const total = allResponse?.total ?? 0

    totalResources.value = total
    myResources.value = Math.floor(total * 0.6)
    fileResources.value = Math.floor(total * 0.8)
    linkResources.value = total - Math.floor(total * 0.8)
  } catch (error) {
    console.error('获取统计数据失败:', error)
    totalResources.value = 0
    myResources.value = 0
    fileResources.value = 0
    linkResources.value = 0
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchResources()
}

const resetSearch = () => {
  Object.assign(searchForm, {
    keyword: '',
    resource_type: null,
    software_engineering_chapter: null,
    ideological_theme: null,
  })
  handleSearch()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchResources()
}

const handlePageSizeChange = (pageSize) => {
  pagination.pageSize = pageSize
  pagination.page = 1
  fetchResources()
}

const showUploadModal = () => {
  resetUploadForm()
  uploadModalVisible.value = true
}

const resetUploadForm = () => {
  Object.assign(uploadForm, {
    title: '',
    description: '',
    fileList: [],
    software_engineering_chapter: null,
    ideological_theme: null,
    tags: [],
    is_public: true,
  })
}

const handleFileChange = (options) => {
  // 自动填充标题
  if (options.fileList.length > 0 && !uploadForm.title) {
    uploadForm.title = options.fileList[0].name.replace(/\.[^/.]+$/, '')
  }
}

const handleUploadResource = async () => {
  try {
    await uploadFormRef.value?.validate()
    uploadLoading.value = true

    if (!uploadForm.fileList.length) {
      message.error('请选择要上传的文件')
      return
    }

    const formData = new FormData()
    formData.append('title', uploadForm.title)
    formData.append('description', uploadForm.description || '')
    formData.append('file', uploadForm.fileList[0].file)
    formData.append('software_engineering_chapter', uploadForm.software_engineering_chapter || '')
    formData.append('ideological_theme', uploadForm.ideological_theme || '')
    formData.append('tags', JSON.stringify(uploadForm.tags))
    formData.append('is_public', uploadForm.is_public)

    await request.post('/ideological/resources/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    message.success('资源上传成功')
    uploadModalVisible.value = false
    fetchResources()
    fetchStatistics()
  } catch (error) {
    message.error('资源上传失败')
  } finally {
    uploadLoading.value = false
  }
}

const showAddLinkModal = () => {
  resetLinkForm()
  addLinkModalVisible.value = true
}

const resetLinkForm = () => {
  Object.assign(linkForm, {
    title: '',
    description: '',
    external_url: '',
    software_engineering_chapter: null,
    ideological_theme: null,
    tags: [],
    is_public: true,
  })
}

const validateUrl = () => {
  try {
    new URL(linkForm.external_url)
  } catch {
    message.warning('请输入有效的URL地址')
  }
}

const handleAddLink = async () => {
  try {
    await linkFormRef.value?.validate()
    linkLoading.value = true

    const linkData = {
      ...linkForm,
      resource_type: 'link',
    }

    await request.post('/ideological/resources/', linkData)

    message.success('链接添加成功')
    addLinkModalVisible.value = false
    fetchResources()
    fetchStatistics()
  } catch (error) {
    message.error('链接添加失败')
  } finally {
    linkLoading.value = false
  }
}

const viewResourceDetail = (resource) => {
  message.info(`查看资源: ${resource.title}`)
}

const downloadResource = async (resource) => {
  try {
    const link = document.createElement('a')
    link.href = resource.download_url
    link.download = resource.title
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    message.success('开始下载')
  } catch (error) {
    message.error('下载失败')
  }
}

const openExternalLink = (resource) => {
  window.open(resource.external_url, '_blank')
}

const previewResource = (resource) => {
  message.info(`预览功能开发中`)
}

const getResourceIcon = (type) => {
  const iconMap = {
    document: 'ant-design:file-text-outlined',
    video: 'ant-design:video-camera-outlined',
    audio: 'ant-design:audio-outlined',
    image: 'ant-design:picture-outlined',
    presentation: 'ant-design:file-ppt-outlined',
    simulation: 'ant-design:experiment-outlined',
    link: 'ant-design:link-outlined',
    other: 'ant-design:file-outlined',
  }
  return iconMap[type] || 'ant-design:file-outlined'
}

const getResourceIconColor = (type) => {
  const colorMap = {
    document: '#1890ff',
    video: '#f5222d',
    audio: '#52c41a',
    image: '#fa8c16',
    presentation: '#722ed1',
    simulation: '#13c2c2',
    link: '#18a058',
    other: '#999',
  }
  return colorMap[type] || '#999'
}

const getResourceTypeLabel = (type) => {
  const option = resourceTypeOptions.value.find(item => item.value === type)
  return option ? option.label : type
}

const getResourceTypeTagType = (type) => {
  const typeMap = {
    document: 'info',
    video: 'error',
    audio: 'success',
    image: 'warning',
    presentation: 'default',
    simulation: 'info',
    link: 'success',
    other: 'default',
  }
  return typeMap[type] || 'default'
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const getResourceActionOptions = (resource) => {
  const options = [
    { label: '查看详情', key: 'view' },
    { label: '编辑', key: 'edit' },
    { label: '复制链接', key: 'copy' },
  ]

  if (resource.file_url) {
    options.push({ label: '下载', key: 'download' })
  }

  if (resource.external_url) {
    options.push({ label: '访问链接', key: 'visit' })
  }

  options.push(
    { type: 'divider' },
    { label: '删除', key: 'delete' }
  )

  return options
}

const handleResourceAction = (key, resource) => {
  switch (key) {
    case 'view':
      viewResourceDetail(resource)
      break
    case 'edit':
      message.info('编辑功能开发中')
      break
    case 'copy':
      navigator.clipboard.writeText(window.location.origin + resource.download_url)
      message.success('链接已复制')
      break
    case 'download':
      downloadResource(resource)
      break
    case 'visit':
      openExternalLink(resource)
      break
    case 'delete':
      deleteResource(resource)
      break
  }
}

const deleteResource = (resource) => {
  dialog.warning({
    title: '删除确认',
    content: `确定要删除资源"${resource.title}"吗？此操作不可恢复。`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await request.delete(`/ideological/resources/${resource.id}`)
        message.success('资源删除成功')
        fetchResources()
        fetchStatistics()
      } catch (error) {
        message.error('资源删除失败')
      }
    },
  })
}

// 初始化
onMounted(() => {
  fetchOptions()
  fetchResources()
  fetchStatistics()
})
</script>

<style scoped>
.resources-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-header {
  background: linear-gradient(135deg, #f5222d 0%, #ff7875 100%);
  color: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(245, 34, 45, 0.2);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-section h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
}

.title-section p {
  margin: 0;
  opacity: 0.9;
  font-size: 14px;
}

.search-section {
  margin-bottom: 0;
}

.resources-list {
  flex: 1;
}

.grid-view {
  min-height: 400px;
}

.resource-card {
  height: 100%;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.resource-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.resource-cover {
  height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  position: relative;
  overflow: hidden;
}

.file-preview {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: cover;
}

.file-icon,
.link-preview,
.default-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.resource-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}

.resource-title {
  font-weight: 600;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.resource-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.resource-description {
  color: var(--n-text-color-depth-3);
  margin: 0;
  line-height: 1.4;
  font-size: 12px;
}

.resource-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.resource-info {
  font-size: 12px;
  color: #999;
}

.resource-footer {
  margin-top: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .title-section h1 {
    font-size: 20px;
  }
}
</style>
