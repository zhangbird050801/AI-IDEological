<template>
  <AppPage>
    <div class="prompts-page">
      <!-- 页面头部 -->
      <div class="page-header">
        <div class="header-content">
          <div class="title-section">
            <h1>提示词模板库</h1>
            <p>高效的提示词模板，助力快速生成优质思政内容</p>
          </div>

          <div class="actions-section">
            <n-space>
              <n-button type="primary" @click="generateWithAssistant">
                <template #icon>
                  <n-icon><Icon icon="mdi:robot" /></n-icon>
                </template>
                AI助手生成
              </n-button>
              <n-button @click="showImportModal">
                <template #icon>
                  <n-icon><Icon icon="mdi:import" /></n-icon>
                </template>
                导入模板
              </n-button>
              <n-button @click="showSystemTemplates">
                <template #icon>
                  <n-icon><Icon icon="mdi:star" /></n-icon>
                </template>
                系统模板
              </n-button>
            </n-space>
          </div>
        </div>
      </div>

      <!-- 统计信息 -->
      <n-grid :cols="4" :x-gap="16" style="margin-bottom: 16px">
        <n-grid-item>
          <n-card :bordered="false" size="small">
            <n-statistic label="总模板数" :value="totalTemplates" />
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card :bordered="false" size="small">
            <n-statistic label="我的模板" :value="myTemplates" />
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card :bordered="false" size="small">
            <n-statistic label="系统模板" :value="systemTemplates" />
          </n-card>
        </n-grid-item>
        <n-grid-item>
          <n-card :bordered="false" size="small">
            <n-statistic label="今日使用" :value="todayUsage" />
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
                placeholder="搜索模板名称或描述"
                clearable
                @clear="handleSearch"
                @keyup.enter="handleSearch"
              >
                <template #prefix>
                  <n-icon><Icon icon="mdi:magnify" /></n-icon>
                </template>
              </n-input>
            </n-form-item-grid-item>

            <n-form-item-grid-item :span="1" label="模板类型">
              <n-select
                v-model:value="searchForm.template_type"
                placeholder="选择类型"
                :options="templateTypeOptions"
                clearable
                @clear="handleSearch"
              />
            </n-form-item-grid-item>

            <n-form-item-grid-item :span="1" label="分类">
              <n-select
                v-model:value="searchForm.category"
                placeholder="选择分类"
                :options="categoryOptions"
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
          </n-grid>

          <n-space justify="end" style="margin-top: 16px">
            <n-button @click="resetSearch">重置</n-button>
            <n-button type="primary" @click="handleSearch">搜索</n-button>
          </n-space>
        </n-form>
      </n-card>

      <!-- 模板列表 -->
      <n-card title="模板列表" class="templates-list">
        <template #header-extra>
          <n-space>
            <n-tag v-if="searchForm.keyword" type="info" closable @close="searchForm.keyword = ''">
              关键词: {{ searchForm.keyword }}
            </n-tag>
            <n-tag v-if="searchForm.template_type" type="info" closable @close="searchForm.template_type = null">
              类型: {{ getTemplateTypeLabel(searchForm.template_type) }}
            </n-tag>
            <n-tag v-if="searchForm.category" type="info" closable @close="searchForm.category = null">
              分类: {{ searchForm.category }}
            </n-tag>
          </n-space>
        </template>

        <!-- 网格视图 -->
        <div class="grid-view">
          <n-grid :cols="2" :x-gap="16" :y-gap="16">
            <n-grid-item v-for="template in templatesList" :key="template.id">
              <n-card
                class="template-card"
                hoverable
                @click="viewTemplateDetail(template)"
              >
                <template #header>
                  <div class="template-header">
                    <div class="template-title-section">
                      <span class="template-title">{{ template.name }}</span>
                      <div class="template-meta">
                        <n-tag v-if="template.is_system" type="warning" size="small">系统</n-tag>
                        <n-tag v-else type="info" size="small">个人</n-tag>
                        <n-tag size="small" type="default">
                          {{ getTemplateTypeLabel(template.template_type) }}
                        </n-tag>
                      </div>
                    </div>
                    <div class="template-rating">
                      <n-rate :value="template.rating" readonly size="small" />
                      <span class="rating-text">({{ template.rating_count }})</span>
                    </div>
                  </div>
                </template>

                <div class="template-content">
                  <p class="template-description">
                    {{ template.description || '' }}
                  </p>

                  <div class="template-preview">
                  <div class="code-content">
                    {{ (template.template_content || '').substring(0, 200) + '...' }}
                  </div>
                </div>

                  <div class="template-variables" v-if="template.variables && template.variables.length > 0">
                    <n-space size="small" wrap>
                      <n-tag v-for="variable in template.variables" :key="variable" size="small">
                        {{ '{' + '{' + variable + '}' + '}' }}
                      </n-tag>
                    </n-space>
                  </div>

                  <div class="template-stats">
                    <n-space size="small">
                      <n-button size="small" text>
                        <template #icon>
                          <n-icon><Icon icon="mdi:fire" /></n-icon>
                        </template>
                        {{ template.usage_count }}
                      </n-button>
                      <n-button size="small" text @click.stop="previewTemplate(template)">
                        <template #icon>
                          <n-icon><Icon icon="mdi:eye" /></n-icon>
                        </template>
                        预览
                      </n-button>
                      <n-button size="small" text @click.stop="useTemplate(template)">
                        <template #icon>
                          <n-icon><Icon icon="mdi:play" /></n-icon>
                        </template>
                        使用
                      </n-button>
                    </n-space>
                  </div>
                </div>

                <template #footer>
                  <div class="template-footer">
                    <n-space justify="space-between">
                      <n-space size="small">
                        <span style="color: #999; font-size: 12px">
                          {{ formatDate(template.updated_at) }}
                        </span>
                      </n-space>

                      <n-dropdown
                        trigger="hover"
                        :options="getTemplateActionOptions(template)"
                        @select="handleTemplateAction"
                      >
                        <n-button size="small" text>
                          <template #icon>
                            <n-icon><Icon icon="mdi:dots-vertical" /></n-icon>
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
          v-if="!loading && templatesList.length === 0"
          description="暂无模板数据"
          style="margin: 40px 0"
        >
          <template #action>
            <n-button type="primary" @click="generateWithAssistant">
              使用AI助手生成
            </n-button>
          </template>
        </n-empty>
      </n-card>
    </div>

  
    <!-- 模板预览弹窗 -->
    <n-modal
      v-model:show="previewModalVisible"
      preset="dialog"
      style="width: 800px"
      title="模板预览"
    >
      <div v-if="previewTemplateData">
        <n-descriptions :column="1" bordered>
          <n-descriptions-item label="模板名称">
            {{ previewTemplateData.name }}
          </n-descriptions-item>
          <n-descriptions-item label="模板类型">
            <n-tag type="info">
              {{ getTemplateTypeLabel(previewTemplateData.template_type) }}
            </n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="分类">
            {{ previewTemplateData.category }}
          </n-descriptions-item>
          <n-descriptions-item label="描述">
            {{ previewTemplateData.description || '' }}
          </n-descriptions-item>
          <n-descriptions-item label="变量" v-if="previewTemplateData.variables && previewTemplateData.variables.length > 0">
            <n-space wrap>
              <n-tag v-for="variable in previewTemplateData.variables" :key="variable" size="small">
                {{ '{' + '{' + variable + '}' + '}' }}
              </n-tag>
            </n-space>
          </n-descriptions-item>
        </n-descriptions>

        <div style="margin-top: 16px">
          <h4>模板内容：</h4>
          <div class="preview-code-content">
            {{ previewTemplateData.template_content || '' }}
          </div>
        </div>
      </div>

      <template #action>
        <n-space>
          <n-button @click="previewModalVisible = false">关闭</n-button>
          <n-button type="primary" @click="useTemplate(previewTemplateData)">
            使用此模板
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </AppPage>
</template>

<script>
export default {
  name: 'AIGCPrompts'
}
</script>

<script setup>
import { ref, reactive, onMounted, computed, watch, h } from 'vue'
import { useRouter } from 'vue-router'
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
  NRate,
  NCode,
  NDescriptions,
  NDescriptionsItem,
  NText,
  NPagination,
  NEmpty,
  NDropdown,
  NStatistic,
  useMessage,
  useDialog,
} from 'naive-ui'
import { Icon } from '@iconify/vue'
import AppPage from '@/components/page/AppPage.vue'
import { request } from '@/utils/http'
import { templatesApi, casesApi } from '@/api/ideological'

// 响应式数据
const message = useMessage()
const dialog = useDialog()

const loading = ref(false)
const previewModalVisible = ref(false)
const previewTemplateData = ref(null)

// 调试信息
console.log('AIGCPrompts 组件已加载')

// 统计数据
const totalTemplates = ref(0)
const myTemplates = ref(0)
const systemTemplates = ref(0)
const todayUsage = ref(0)

// 搜索表单
const searchForm = reactive({
  keyword: '',
  template_type: null,
  category: null,
  software_engineering_chapter: null,
  ideological_theme: null,
})


// 模板列表
const templatesList = ref([])
const pagination = reactive({
  page: 1,
  pageSize: 12,
  itemCount: 0,
  showSizePicker: true,
  pageSizes: [12, 24, 48, 96],
})

// 选项数据
const templateTypeOptions = ref([])
const categoryOptions = ref([])
const chapterOptions = ref([])
const themeOptions = ref([])

// 方法
const fetchTemplates = async () => {
  loading.value = true
  try {
    const params = {
      ...searchForm,
      page: pagination.page,
      page_size: pagination.pageSize,
    }

    const response = await request.get('/ideological/templates/', { params })
    templatesList.value = response.data?.items || []
    pagination.itemCount = response.data?.total || 0
  } catch (error) {
    console.error('获取模板列表失败:', error)
    message.error('获取模板列表失败')
  } finally {
    loading.value = false
  }
}

const fetchOptions = async () => {
  try {
    // 获取模板类型选项
    try {
      const typesResponse = await request.get('/ideological/templates/types/list')
      templateTypeOptions.value = Array.isArray(typesResponse.data) ? typesResponse.data : (typesResponse?.data || typesResponse || [])
    } catch (error) {
      // 使用默认模板类型数据
      templateTypeOptions.value = [
        { label: "案例生成", value: "case_generation" },
        { label: "讨论题生成", value: "discussion_generation" },
        { label: "思考题生成", value: "thinking_generation" },
        { label: "内容优化", value: "content_optimization" },
        { label: "教学设计", value: "teaching_design" },
        { label: "知识点讲解", value: "knowledge_point" }
      ]
    }

    // 获取分类选项
    try {
      const categoriesResponse = await request.get('/ideological/templates/categories/list')
      const categoriesData = Array.isArray(categoriesResponse.data) ? categoriesResponse.data : (categoriesResponse?.data || categoriesResponse || [])
      categoryOptions.value = categoriesData.map(item => ({
        label: item,
        value: item,
      }))
    } catch (error) {
      // 使用默认分类数据
      categoryOptions.value = [
        "思政案例", "教学方法", "知识点讲解", "课程设计", "实践指导", "质量评价", "前沿技术", "职业素养"
      ].map(item => ({ label: item, value: item }))
    }

    // 获取章节选项
    try {
      const chaptersResponse = await casesApi.getChapters()
      const chaptersData = Array.isArray(chaptersResponse.data) ? chaptersResponse.data : (chaptersResponse?.data || chaptersResponse || [])
      chapterOptions.value = chaptersData.map(item => ({
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
      const themesResponse = await templatesApi.getThemes()
      const themesData = Array.isArray(themesResponse.data) ? themesResponse.data : (themesResponse?.data || themesResponse || [])
      themeOptions.value = themesData.map(item => ({
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
    const allResponse = await request.get('/ideological/templates/', { params: { page_size: 1 } })
    const total = allResponse?.data?.total ?? allResponse?.total ?? 0
    
    totalTemplates.value = total

    const systemResponse = await request.get('/ideological/templates/system/list')
    const systemCount = (systemResponse?.data || systemResponse || []).length
    systemTemplates.value = systemCount

    myTemplates.value = total - systemCount

    // 模拟今日使用数据
    todayUsage.value = Math.floor(Math.random() * 50) + 10
  } catch (error) {
    console.error('获取统计数据失败:', error)
    totalTemplates.value = 0
    systemTemplates.value = 0
    myTemplates.value = 0
    todayUsage.value = 0
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchTemplates()
}

const resetSearch = () => {
  Object.assign(searchForm, {
    keyword: '',
    template_type: null,
    category: null,
    software_engineering_chapter: null,
    ideological_theme: null,
  })
  handleSearch()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchTemplates()
}

const handlePageSizeChange = (pageSize) => {
  pagination.pageSize = pageSize
  pagination.page = 1
  fetchTemplates()
}

const previewTemplate = (template) => {
  previewTemplateData.value = template
  previewModalVisible.value = true
}

const viewTemplateDetail = (template) => {
  previewTemplateData.value = template
  previewModalVisible.value = true
}

const useTemplate = (template) => {
  if (!template) return

  // 跳转到聊天页面并使用该模板
  message.info(`使用模板: ${template.name}`)

  // 将模板信息保存到localStorage
  localStorage.setItem('selected_template', JSON.stringify({
    id: template.id,
    name: template.name,
    content: template.template_content,
    variables: template.variables
  }))

  // 跳转到聊天页面
  const router = useRouter()
  router.push('/aigc/chat')
}

const generateWithAssistant = () => {
  console.log('generateWithAssistant 函数被调用')

  // 标记是从模板页面跳转到助手
  localStorage.setItem('from_template_page', 'true')
  localStorage.removeItem('prompt_to_save') // 清除之前的提示词数据

  message.info('即将跳转到提示词助手，生成完成后可以保存为模板')

  // 直接跳转到提示词助手页面
  console.log('准备跳转到提示词助手页面')
  window.location.href = '/aigc/prompt-assistant'
}

const getTemplateTypeLabel = (type) => {
  if (!templateTypeOptions.value || !templateTypeOptions.value.length) return type
  const option = templateTypeOptions.value.find(item => item.value === type)
  return option ? option.label : type
}

const getTemplateActionOptions = (template) => {
  const options = [
    { label: '查看详情', key: 'view' },
    { label: '预览', key: 'preview' },
    { label: '使用模板', key: 'use' },
  ]

  if (!template.is_system) {
    options.push(
      { type: 'divider' },
      { label: '复制', key: 'copy' },
      { label: '删除', key: 'delete' }
    )
  }

  options.push(
    { type: 'divider' },
    { label: '评分', key: 'rate' }
  )

  return options
}

const handleTemplateAction = (key, template) => {
  switch (key) {
    case 'view':
    case 'preview':
      viewTemplateDetail(template)
      break
    case 'use':
      useTemplate(template)
      break
    case 'copy':
      copyTemplate(template)
      break
    case 'delete':
      deleteTemplate(template)
      break
    case 'rate':
      rateTemplate(template)
      break
  }
}

const copyTemplate = (template) => {
  const newTemplate = { ...template }
  delete newTemplate.id
  delete newTemplate.created_at
  delete newTemplate.updated_at
  newTemplate.name = `${template.name} (副本)`
  // 复制模板时直接调用API，不需要表单
  createTemplateCopy(newTemplate)
}

const createTemplateCopy = async (templateData) => {
  try {
    await request.post('/ideological/templates/', templateData)
    message.success('模板复制成功')
    fetchTemplates()
    fetchStatistics()
  } catch (error) {
    message.error('模板复制失败')
  }
}

const deleteTemplate = (template) => {
  dialog.warning({
    title: '删除确认',
    content: `确定要删除模板"${template.name}"吗？此操作不可恢复。`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await request.delete(`/ideological/templates/${template.id}`)
        message.success('模板删除成功')
        fetchTemplates()
        fetchStatistics()
      } catch (error) {
        message.error('模板删除失败')
      }
    },
  })
}

const rateTemplate = (template) => {
  // 创建一个简单的评分弹窗
  dialog.create({
    title: `为"${template.name}"评分`,
    content: () => {
      const rating = ref(3)
      return h('div', { style: 'padding: 20px; text-align: center;' }, [
        h('p', { style: 'margin-bottom: 16px; color: #666;' }, '请为这个提示词模板评分：'),
        h('div', { style: 'margin-bottom: 16px;' }, [
          h(NRate, {
            value: rating.value,
            'onUpdate:value': (val) => { rating.value = val },
            size: 'large'
          })
        ]),
        h('p', { style: 'color: #999; font-size: 12px;' }, `当前评分: ${template.rating} (${template.rating_count}人评价)`)
      ])
    },
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await request.post(`/ideological/templates/${template.id}/rate`, {}, { params: { rating: 4 } })
        message.success('评分成功！')
        fetchTemplates() // 刷新列表
        fetchStatistics() // 刷新统计
      } catch (error) {
        message.error('评分失败')
      }
    }
  })
}

const showSystemTemplates = async () => {
  try {
    const response = await request.get('/ideological/templates/system/list')
    templatesList.value = response.data || []
    pagination.itemCount = (response.data || []).length
    message.success('已切换到系统模板视图')
  } catch (error) {
    message.error('获取系统模板失败')
  }
}

const showImportModal = () => {
  dialog.create({
    title: '导入提示词模板',
    content: () => {
      const importText = ref('')
      return h('div', { style: 'padding: 20px;' }, [
        h('p', { style: 'margin-bottom: 16px; color: #666;' }, '请输入要导入的提示词模板内容：'),
        h('div', { style: 'margin-bottom: 16px;' }, [
          h('textarea', {
            value: importText.value,
            'onInput': (e) => { importText.value = e.target.value },
            placeholder: '请输入提示词模板内容，使用 {{变量名}} 格式定义变量...',
            style: 'width: 100%; height: 120px; padding: 8px; border: 1px solid #ccc; border-radius: 4px; resize: vertical;'
          })
        ]),
        h('p', { style: 'color: #999; font-size: 12px;' }, '支持格式：纯文本提示词，变量用 {{变量名}} 格式')
      ])
    },
    positiveText: '导入',
    negativeText: '取消',
    onPositiveClick: async () => {
      if (!importText.value.trim()) {
        message.warning('请输入模板内容')
        return false
      }
      try {
        // 提取变量
        const variables = [...new Set(importText.value.match(/\{\{(\w+)\}\}/g) || [])]
          .map(match => match.slice(2, -2))

        const templateData = {
          name: `导入模板_${Date.now()}`,
          description: '通过导入创建的提示词模板',
          template_type: 'content_optimization',
          template_content: importText.value,
          variables: variables,
          category: '导入模板'
        }

        await request.post('/ideological/templates/', templateData)
        message.success('模板导入成功！')
        fetchTemplates() // 刷新列表
        fetchStatistics() // 刷新统计
      } catch (error) {
        message.error('模板导入失败')
      }
    }
  })
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`

  return date.toLocaleDateString()
}

// 初始化
onMounted(() => {
  // 确保开发环境有认证token
  if (import.meta.env.DEV) {
    const currentToken = localStorage.getItem('access_token')
    if (!currentToken || currentToken !== 'dev') {
      localStorage.setItem('access_token', 'dev')
      console.log('🔧 提示词模板页面：已设置认证token')
    }
  }

  fetchOptions()
  fetchTemplates()
  fetchStatistics()
})
</script>

<style scoped>
.prompts-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-header {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.2);
  margin-bottom: 16px;
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

.templates-list {
  flex: 1;
}

.grid-view {
  min-height: 400px;
}

.template-card {
  height: 100%;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.template-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.template-title-section {
  flex: 1;
  margin-right: 16px;
}

.template-title {
  font-weight: 600;
  font-size: 16px;
  display: block;
  margin-bottom: 8px;
}

.template-meta {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.template-rating {
  display: flex;
  align-items: center;
  gap: 4px;
}

.rating-text {
  font-size: 12px;
  color: #999;
}

.template-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
  font-size: 14px;
  line-height: 1.6;
  word-wrap: break-word;
  word-break: break-word;
  overflow-wrap: break-word;
}

.template-description {
  color: var(--n-text-color-depth-3);
  margin: 0;
  line-height: 1.5;
  word-wrap: break-word;
  word-break: break-all;
  white-space: normal;
}

.template-preview {
  max-height: 120px;
  overflow: hidden;
  font-size: 12px;
  line-height: 1.4;
}

.code-content {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  padding: 12px;
  font-family: 'Courier New', monospace;
  font-size: 11px;
  line-height: 1.4;
  color: #495057;
  white-space: pre-wrap;
  word-wrap: break-word;
  word-break: break-all;
  overflow: hidden;
}

.preview-code-content {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  padding: 16px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.5;
  color: #495057;
  white-space: pre-wrap;
  word-wrap: break-word;
  word-break: break-word;
  max-height: 400px;
  overflow-y: auto;
}

.template-variables {
  margin-top: 8px;
}

.template-stats {
  margin-top: 8px;
}

.template-footer {
  margin-top: 12px;
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
