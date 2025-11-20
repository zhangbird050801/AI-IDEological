<template>
  <AppPage>
    <div class="prompts-page">
      <!-- 页面头部 -->
      <div class="page-header">
        <div class="header-content">
          <div class="title-section">
            <h1>提示词模板库</h1>
            <p>专业的课程思政内容生成提示词模板，提高AIGC内容质量和教学效果</p>
          </div>

          <div class="actions-section">
            <n-space>
              <n-button type="primary" @click="showCreateModal">
                <template #icon>
                  <n-icon><Icon icon="ant-design:plus-outlined" /></n-icon>
                </template>
                新建模板
              </n-button>
              <n-button @click="showImportModal">
                <template #icon>
                  <n-icon><Icon icon="ant-design:import-outlined" /></n-icon>
                </template>
                导入模板
              </n-button>
              <n-button @click="showSystemTemplates">
                <template #icon>
                  <n-icon><Icon icon="ant-design:star-outlined" /></n-icon>
                </template>
                系统模板
              </n-button>
            </n-space>
          </div>
        </div>
      </div>

      <!-- 统计信息 -->
      <n-grid :cols="4" :x-gap="16">
        <n-grid-item>
          <n-statistic label="总模板数" :value="totalTemplates" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="我的模板" :value="myTemplates" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="系统模板" :value="systemTemplates" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="今日使用" :value="todayUsage" />
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
                  <n-icon><Icon icon="ant-design:search-outlined" /></n-icon>
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
                    {{ template.description }}
                  </p>

                  <div class="template-preview">
                    <n-code
                      :code="template.template_content.substring(0, 200) + '...'"
                      language="text"
                      show-line-numbers
                      :line-height="1.4"
                    />
                  </div>

                  <div class="template-variables" v-if="template.variables.length > 0">
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
                          <n-icon><Icon icon="ant-design:fire-outlined" /></n-icon>
                        </template>
                        {{ template.usage_count }}
                      </n-button>
                      <n-button size="small" text @click.stop="previewTemplate(template)">
                        <template #icon>
                          <n-icon><Icon icon="ant-design:eye-outlined" /></n-icon>
                        </template>
                        预览
                      </n-button>
                      <n-button size="small" text @click.stop="useTemplate(template)">
                        <template #icon>
                          <n-icon><Icon icon="ant-design:play-circle-outlined" /></n-icon>
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
          v-if="!loading && templatesList.length === 0"
          description="暂无模板数据"
          style="margin: 40px 0"
        >
          <template #action>
            <n-button type="primary" @click="showCreateModal">
              创建第一个模板
            </n-button>
          </template>
        </n-empty>
      </n-card>
    </div>

    <!-- 创建/编辑模板弹窗 -->
    <n-modal
      v-model:show="createModalVisible"
      :mask-closable="false"
      preset="dialog"
      style="width: 900px"
      :title="editingTemplate ? '编辑模板' : '新建模板'"
    >
      <n-form
        ref="templateFormRef"
        :model="templateForm"
        :rules="templateFormRules"
        label-placement="left"
        :label-width="120"
        require-mark-placement="right-hanging"
      >
        <n-grid :cols="2" :x-gap="16">
          <n-form-item-grid-item label="模板名称" path="name">
            <n-input
              v-model:value="templateForm.name"
              placeholder="请输入模板名称"
              maxlength="100"
              show-count
            />
          </n-form-item-grid-item>

          <n-form-item-grid-item label="模板类型" path="template_type">
            <n-select
              v-model:value="templateForm.template_type"
              placeholder="选择模板类型"
              :options="templateTypeOptions"
            />
          </n-form-item-grid-item>
        </n-grid>

        <n-form-item label="模板描述" path="description">
          <n-input
            v-model:value="templateForm.description"
            type="textarea"
            placeholder="请输入模板描述"
            :autosize="{ minRows: 2, maxRows: 4 }"
            maxlength="500"
            show-count
          />
        </n-form-item>

        <n-form-item label="分类" path="category">
          <n-select
            v-model:value="templateForm.category"
            placeholder="选择分类"
            :options="categoryOptions"
            filterable
            tag
          />
        </n-form-item>

        <n-grid :cols="2" :x-gap="16">
          <n-form-item-grid-item label="软件工程章节" path="software_engineering_chapter">
            <n-select
              v-model:value="templateForm.software_engineering_chapter"
              placeholder="选择章节"
              :options="chapterOptions"
              clearable
            />
          </n-form-item-grid-item>

          <n-form-item-grid-item label="思政主题" path="ideological_theme">
            <n-select
              v-model:value="templateForm.ideological_theme"
              placeholder="选择主题"
              :options="themeOptions"
              clearable
            />
          </n-form-item-grid-item>
        </n-grid>

        <n-form-item label="模板内容" path="template_content">
          <n-input
            v-model:value="templateForm.template_content"
            type="textarea"
            placeholder="请输入模板内容，使用 {{变量名}} 定义变量"
            :autosize="{ minRows: 8, maxRows: 16 }"
            maxlength="5000"
            show-count
          />
          <template #feedback>
            <n-text depth="3" style="font-size: 12px">
              提示：使用 {{变量名}} 定义变量，如：{{章节}}、{{思政主题}}
            </n-text>
          </template>
        </n-form-item>

        <n-form-item label="提取的变量">
          <n-space>
            <n-tag
              v-for="variable in extractedVariables"
              :key="variable"
              type="info"
              size="small"
            >
              {{ '{' + '{' + variable + '}' + '}' }}
            </n-tag>
            <n-text v-if="extractedVariables.length === 0" depth="3" style="font-size: 12px">
              在模板内容中使用 {{变量名}} 格式定义变量
            </n-text>
          </n-space>
        </n-form-item>
      </n-form>

      <template #action>
        <n-space>
          <n-button @click="createModalVisible = false">取消</n-button>
          <n-button type="primary" @click="handleSubmitTemplate" :loading="submitLoading">
            {{ editingTemplate ? '更新' : '创建' }}
          </n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 模板预览弹窗 -->
    <n-modal
      v-model:show="previewModalVisible"
      preset="dialog"
      style="width: 800px"
      title="模板预览"
    >
      <div v-if="previewTemplate">
        <n-descriptions :column="1" bordered>
          <n-descriptions-item label="模板名称">
            {{ previewTemplate.name }}
          </n-descriptions-item>
          <n-descriptions-item label="模板类型">
            <n-tag type="info">
              {{ getTemplateTypeLabel(previewTemplate.template_type) }}
            </n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="分类">
            {{ previewTemplate.category }}
          </n-descriptions-item>
          <n-descriptions-item label="描述">
            {{ previewTemplate.description }}
          </n-descriptions-item>
          <n-descriptions-item label="变量" v-if="previewTemplate.variables.length > 0">
            <n-space wrap>
              <n-tag v-for="variable in previewTemplate.variables" :key="variable" size="small">
                {{ '{' + '{' + variable + '}' + '}' }}
              </n-tag>
            </n-space>
          </n-descriptions-item>
        </n-descriptions>

        <div style="margin-top: 16px">
          <h4>模板内容：</h4>
          <n-code
            :code="previewTemplate.template_content"
            language="text"
            show-line-numbers
            :line-height="1.6"
          />
        </div>
      </div>

      <template #action>
        <n-space>
          <n-button @click="previewModalVisible = false">关闭</n-button>
          <n-button type="primary" @click="useTemplate(previewTemplate)">
            使用此模板
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </AppPage>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
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
const submitLoading = ref(false)
const createModalVisible = ref(false)
const previewModalVisible = ref(false)
const editingTemplate = ref(null)
const previewTemplate = ref(null)

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

// 模板表单
const templateFormRef = ref()
const templateForm = reactive({
  name: '',
  description: '',
  template_type: null,
  template_content: '',
  variables: [],
  category: null,
  software_engineering_chapter: null,
  ideological_theme: null,
})

// 提取的变量
const extractedVariables = computed(() => {
  const matches = templateForm.template_content.match(/\{\{(\w+)\}\}/g)
  if (!matches) return []
  return [...new Set(matches.map(match => match.slice(2, -2)))]
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

// 表单验证规则
const templateFormRules = {
  name: [
    { required: true, message: '请输入模板名称', trigger: 'blur' },
    { max: 100, message: '名称长度不能超过100个字符', trigger: 'blur' },
  ],
  description: [
    { required: true, message: '请输入模板描述', trigger: 'blur' },
    { max: 500, message: '描述长度不能超过500个字符', trigger: 'blur' },
  ],
  template_type: [
    { required: true, message: '请选择模板类型', trigger: 'change' },
  ],
  template_content: [
    { required: true, message: '请输入模板内容', trigger: 'blur' },
    { max: 5000, message: '内容长度不能超过5000个字符', trigger: 'blur' },
  ],
  category: [
    { required: true, message: '请选择分类', trigger: 'change' },
  ],
}

// 监听模板内容变化，自动提取变量
watch(
  () => templateForm.template_content,
  () => {
    templateForm.variables = extractedVariables.value
  }
)

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
    templatesList.value = response.items
    pagination.itemCount = response.total
  } catch (error) {
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
      templateTypeOptions.value = typesResponse
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
      categoryOptions.value = categoriesResponse.map(item => ({
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
      const themesResponse = await templatesApi.getThemes()
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
    const allResponse = await request.get('/ideological/templates/', { params: { page_size: 1 } })
    totalTemplates.value = allResponse.total

    const systemResponse = await request.get('/ideological/templates/system/list')
    systemTemplates.value = systemResponse.length

    myTemplates.value = totalTemplates.value - systemTemplates.value

    // 模拟今日使用数据
    todayUsage.value = Math.floor(Math.random() * 50) + 10
  } catch (error) {
    console.error('获取统计数据失败:', error)
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

const showCreateModal = () => {
  editingTemplate.value = null
  resetTemplateForm()
  createModalVisible.value = true
}

const resetTemplateForm = () => {
  Object.assign(templateForm, {
    name: '',
    description: '',
    template_type: null,
    template_content: '',
    variables: [],
    category: null,
    software_engineering_chapter: null,
    ideological_theme: null,
  })
}

const editTemplate = (template) => {
  editingTemplate.value = template
  Object.assign(templateForm, template)
  createModalVisible.value = true
}

const handleSubmitTemplate = async () => {
  try {
    await templateFormRef.value?.validate()
    submitLoading.value = true

    const templateData = { ...templateForm }
    templateData.variables = extractedVariables.value

    if (editingTemplate.value) {
      await request.put(`/ideological/templates/${editingTemplate.value.id}`, templateData)
      message.success('模板更新成功')
    } else {
      await request.post('/ideological/templates/', templateData)
      message.success('模板创建成功')
    }

    createModalVisible.value = false
    fetchTemplates()
    fetchStatistics()
  } catch (error) {
    message.error(editingTemplate.value ? '模板更新失败' : '模板创建失败')
  } finally {
    submitLoading.value = false
  }
}

const viewTemplateDetail = (template) => {
  previewTemplate.value = template
  previewModalVisible.value = true
}

const useTemplate = (template) => {
  if (!template) return

  // 跳转到聊天页面并使用该模板
  message.info(`使用模板: ${template.name}`)
  // 这里可以跳转到聊天页面并传递模板信息
}

const getTemplateTypeLabel = (type) => {
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
      { label: '编辑', key: 'edit' },
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
    case 'edit':
      editTemplate(template)
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
  Object.assign(templateForm, newTemplate)
  createModalVisible.value = true
  message.success('模板已复制')
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
  message.info(`评分功能开发中`)
}

const showSystemTemplates = async () => {
  try {
    const response = await request.get('/ideological/templates/system/list')
    templatesList.value = response
    pagination.itemCount = response.length
    message.success('已切换到系统模板视图')
  } catch (error) {
    message.error('获取系统模板失败')
  }
}

const showImportModal = () => {
  message.info('导入功能开发中')
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
  background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
  color: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(124, 58, 237, 0.2);
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
}

.template-description {
  color: var(--n-text-color-depth-3);
  margin: 0;
  line-height: 1.5;
}

.template-preview {
  max-height: 120px;
  overflow: hidden;
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
