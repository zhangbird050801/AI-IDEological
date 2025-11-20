<template>
  <AppPage>
    <div class="cases-page">
      <!-- 页面头部 -->
      <div class="page-header">
        <div class="header-content">
          <div class="title-section">
            <h1>课程思政案例库</h1>
            <p>丰富的软件工程课程思政教学案例，助力教学质量提升</p>
          </div>

          <div class="actions-section">
            <n-space>
              <n-button type="primary" @click="showCreateModal">
                <template #icon>
                  <n-icon><Icon icon="ant-design:plus-outlined" /></n-icon>
                </template>
                新建案例
              </n-button>
              <n-button @click="showImportModal">
                <template #icon>
                  <n-icon><Icon icon="ant-design:import-outlined" /></n-icon>
                </template>
                导入案例
              </n-button>
            </n-space>
          </div>
        </div>
      </div>

      <!-- 搜索和筛选区域 -->
      <n-card class="search-section">
        <n-form :model="searchForm" label-placement="left" :show-feedback="false">
          <n-grid :cols="4" :x-gap="16">
            <n-form-item-grid-item :span="1" label="关键词">
              <n-input
                v-model:value="searchForm.keyword"
                placeholder="搜索案例标题或内容"
                clearable
                @clear="handleSearch"
                @keyup.enter="handleSearch"
              >
                <template #prefix>
                  <n-icon><Icon icon="ant-design:search-outlined" /></n-icon>
                </template>
              </n-input>
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

            <n-form-item-grid-item :span="1" label="案例类型">
              <n-select
                v-model:value="searchForm.case_type"
                placeholder="选择类型"
                :options="caseTypeOptions"
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

      <!-- 案例列表 -->
      <n-card title="案例列表" class="cases-list">
        <template #header-extra>
          <n-space>
            <n-select
              v-model:value="searchForm.difficulty_level"
              placeholder="难度等级"
              :options="difficultyOptions"
              style="width: 120px"
              clearable
              @update:value="handleSearch"
            />
            <n-button-group>
              <n-button
                :type="viewMode === 'grid' ? 'primary' : 'default'"
                @click="viewMode = 'grid'"
              >
                <n-icon><Icon icon="ant-design:appstore-outlined" /></n-icon>
              </n-button>
              <n-button
                :type="viewMode === 'list' ? 'primary' : 'default'"
                @click="viewMode = 'list'"
              >
                <n-icon><Icon icon="ant-design:unordered-list-outlined" /></n-icon>
              </n-button>
            </n-button-group>
          </n-space>
        </template>

        <!-- 网格视图 -->
        <div v-if="viewMode === 'grid'" class="grid-view">
          <n-grid :cols="3" :x-gap="16" :y-gap="16">
            <n-grid-item v-for="case_item in casesList" :key="case_item.id">
              <n-card
                class="case-card"
                hoverable
                @click="viewCaseDetail(case_item)"
              >
                <template #header>
                  <div class="case-header">
                    <span class="case-title">{{ case_item.title }}</span>
                    <n-tag
                      :type="getDifficultyTagType(case_item.difficulty_level)"
                      size="small"
                    >
                      难度{{ case_item.difficulty_level }}
                    </n-tag>
                  </div>
                </template>

                <div class="case-content">
                  <p class="case-description">
                    {{ case_item.content.substring(0, 120) }}...
                  </p>

                  <div class="case-meta">
                    <n-space size="small">
                      <n-tag size="small" type="info">
                        {{ case_item.software_engineering_chapter }}
                      </n-tag>
                      <n-tag size="small" type="success">
                        {{ case_item.ideological_theme }}
                      </n-tag>
                    </n-space>
                  </div>
                </div>

                <template #footer>
                  <div class="case-footer">
                    <n-space justify="space-between">
                      <n-space size="small">
                        <n-button
                          size="small"
                          text
                          @click.stop="toggleFavorite(case_item)"
                        >
                          <template #icon>
                            <n-icon
                              :color="case_item.is_favorited ? '#f0a020' : '#999'"
                            >
                              <Icon icon="ant-design:heart-outlined" />
                            </n-icon>
                          </template>
                          {{ case_item.usage_count }}
                        </n-button>
                        <n-button size="small" text @click.stop="rateCase(case_item)">
                          <template #icon>
                            <n-icon><Icon icon="ant-design:star-outlined" /></n-icon>
                          </template>
                          {{ case_item.rating.toFixed(1) }}
                        </n-button>
                      </n-space>

                      <n-dropdown
                        trigger="hover"
                        :options="getCaseActionOptions(case_item)"
                        @select="handleCaseAction"
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

        <!-- 列表视图 -->
        <div v-else class="list-view">
          <n-data-table
            :columns="columns"
            :data="casesList"
            :pagination="pagination"
            :loading="loading"
            @update:page="handlePageChange"
          />
        </div>

        <!-- 空状态 -->
        <n-empty
          v-if="!loading && casesList.length === 0"
          description="暂无案例数据"
          style="margin: 40px 0"
        >
          <template #action>
            <n-button type="primary" @click="showCreateModal">
              创建第一个案例
            </n-button>
          </template>
        </n-empty>
      </n-card>
    </div>

    <!-- 创建/编辑案例弹窗 -->
    <n-modal
      v-model:show="createModalVisible"
      :mask-closable="false"
      preset="dialog"
      style="width: 800px"
      :title="editingCase ? '编辑案例' : '新建案例'"
    >
      <n-form
        ref="caseFormRef"
        :model="caseForm"
        :rules="caseFormRules"
        label-placement="left"
        :label-width="100"
        require-mark-placement="right-hanging"
      >
        <n-form-item label="案例标题" path="title">
          <n-input
            v-model:value="caseForm.title"
            placeholder="请输入案例标题"
            maxlength="100"
            show-count
          />
        </n-form-item>

        <n-grid :cols="2" :x-gap="16">
          <n-form-item-grid-item label="软件工程章节" path="software_engineering_chapter">
            <n-select
              v-model:value="caseForm.software_engineering_chapter"
              placeholder="选择章节"
              :options="chapterOptions"
            />
          </n-form-item-grid-item>

          <n-form-item-grid-item label="思政主题" path="ideological_theme">
            <n-select
              v-model:value="caseForm.ideological_theme"
              placeholder="选择主题"
              :options="themeOptions"
            />
          </n-form-item-grid-item>
        </n-grid>

        <n-grid :cols="2" :x-gap="16">
          <n-form-item-grid-item label="案例类型" path="case_type">
            <n-select
              v-model:value="caseForm.case_type"
              placeholder="选择类型"
              :options="caseTypeOptions"
            />
          </n-form-item-grid-item>

          <n-form-item-grid-item label="难度等级" path="difficulty_level">
            <n-rate
              v-model:value="caseForm.difficulty_level"
              :count="5"
              color="var(--primary-color)"
            />
          </n-form-item-grid-item>
        </n-grid>

        <n-form-item label="案例内容" path="content">
          <n-input
            v-model:value="caseForm.content"
            type="textarea"
            placeholder="请输入详细的案例内容"
            :autosize="{ minRows: 6, maxRows: 12 }"
            maxlength="5000"
            show-count
          />
        </n-form-item>

        <n-form-item label="关键知识点" path="key_points">
          <n-dynamic-tags
            v-model:value="caseForm.key_points"
            placeholder="按回车添加知识点"
          />
        </n-form-item>

        <n-form-item label="讨论问题" path="discussion_questions">
          <n-dynamic-tags
            v-model:value="caseForm.discussion_questions"
            placeholder="按回车添加讨论问题"
          />
        </n-form-item>

        <n-form-item label="教学建议" path="teaching_suggestions">
          <n-input
            v-model:value="caseForm.teaching_suggestions"
            type="textarea"
            placeholder="请输入教学建议"
            :autosize="{ minRows: 3, maxRows: 6 }"
          />
        </n-form-item>

        <n-form-item label="标签" path="tags">
          <n-dynamic-tags
            v-model:value="caseForm.tags"
            placeholder="按回车添加标签"
          />
        </n-form-item>

        <n-form-item label="公开设置">
          <n-switch v-model:value="caseForm.is_public" />
          <span style="margin-left: 8px; color: #999">
            公开后其他用户可以查看此案例
          </span>
        </n-form-item>
      </n-form>

      <template #action>
        <n-space>
          <n-button @click="createModalVisible = false">取消</n-button>
          <n-button type="primary" @click="handleSubmitCase" :loading="submitLoading">
            {{ editingCase ? '更新' : '创建' }}
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </AppPage>
</template>

<script setup>
import { ref, reactive, onMounted, h } from 'vue'
import {
  NCard,
  NButton,
  NIcon,
  NSpace,
  NForm,
  NFormItem,
  NInput,
  NSelect,
  NGrid,
  NGridItem,
  NTag,
  NModal,
  NRate,
  NDynamicTags,
  NSwitch,
  NDataTable,
  NEmpty,
  NDropdown,
  useMessage,
  useDialog,
} from 'naive-ui'
import { Icon } from '@iconify/vue'
import AppPage from '@/components/page/AppPage.vue'
import { request } from '@/utils/http'
import { casesApi } from '@/api/ideological'

// 响应式数据
const message = useMessage()
const dialog = useDialog()

const loading = ref(false)
const submitLoading = ref(false)
const createModalVisible = ref(false)
const editingCase = ref(null)
const viewMode = ref('grid')

// 搜索表单
const searchForm = reactive({
  keyword: '',
  software_engineering_chapter: null,
  ideological_theme: null,
  case_type: null,
  difficulty_level: null,
})

// 案例表单
const caseFormRef = ref()
const caseForm = reactive({
  title: '',
  content: '',
  software_engineering_chapter: null,
  ideological_theme: null,
  case_type: null,
  difficulty_level: 3,
  key_points: [],
  discussion_questions: [],
  teaching_suggestions: '',
  tags: [],
  is_public: true,
})

// 案例列表
const casesList = ref([])
const pagination = reactive({
  page: 1,
  pageSize: 12,
  itemCount: 0,
  showSizePicker: true,
  pageSizes: [12, 24, 48, 96],
})

// 选项数据
const chapterOptions = ref([])
const themeOptions = ref([])
const caseTypeOptions = ref([
  { label: '案例分析', value: 'case_study' },
  { label: '讨论题', value: 'discussion' },
  { label: '思考题', value: 'thinking' },
  { label: '示例', value: 'example' },
  { label: '实践项目', value: 'practice' },
])

const difficultyOptions = ref([
  { label: '难度1', value: 1 },
  { label: '难度2', value: 2 },
  { label: '难度3', value: 3 },
  { label: '难度4', value: 4 },
  { label: '难度5', value: 5 },
])

// 表单验证规则
const caseFormRules = {
  title: [
    { required: true, message: '请输入案例标题', trigger: 'blur' },
    { max: 100, message: '标题长度不能超过100个字符', trigger: 'blur' },
  ],
  content: [
    { required: true, message: '请输入案例内容', trigger: 'blur' },
    { max: 5000, message: '内容长度不能超过5000个字符', trigger: 'blur' },
  ],
  software_engineering_chapter: [
    { required: true, message: '请选择软件工程章节', trigger: 'change' },
  ],
  ideological_theme: [
    { required: true, message: '请选择思政主题', trigger: 'change' },
  ],
  case_type: [
    { required: true, message: '请选择案例类型', trigger: 'change' },
  ],
}

// 表格列定义
const columns = [
  {
    title: '案例标题',
    key: 'title',
    ellipsis: {
      tooltip: true,
    },
  },
  {
    title: '软件工程章节',
    key: 'software_engineering_chapter',
    width: 150,
  },
  {
    title: '思政主题',
    key: 'ideological_theme',
    width: 120,
  },
  {
    title: '案例类型',
    key: 'case_type',
    width: 100,
    render(row) {
      return h(
        NTag,
        { type: 'info', size: 'small' },
        { default: () => getCaseTypeLabel(row.case_type) }
      )
    },
  },
  {
    title: '难度',
    key: 'difficulty_level',
    width: 80,
    render(row) {
      return h(NRate, { value: row.difficulty_level, readonly: true, count: 5, size: 'small' })
    },
  },
  {
    title: '使用次数',
    key: 'usage_count',
    width: 80,
  },
  {
    title: '评分',
    key: 'rating',
    width: 80,
    render(row) {
      return `${row.rating.toFixed(1)} (${row.rating_count})`
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 150,
    render(row) {
      return h(
        NSpace,
        { size: 'small' },
        {
          default: () => [
            h(
              NButton,
              { size: 'small', text: true, onClick: () => viewCaseDetail(row) },
              { default: () => '查看' }
            ),
            h(
              NButton,
              { size: 'small', text: true, onClick: () => editCase(row) },
              { default: () => '编辑' }
            ),
            h(
              NButton,
              { size: 'small', text: true, type: 'error', onClick: () => deleteCase(row) },
              { default: () => '删除' }
            ),
          ],
        }
      )
    },
  },
]

// 方法
const fetchCases = async () => {
  loading.value = true
  try {
    const params = {
      ...searchForm,
      page: viewMode.value === 'list' ? pagination.page : 1,
      page_size: viewMode.value === 'list' ? pagination.pageSize : 12,
    }

    const response = await request.get('/ideological/cases/', { params })
    casesList.value = response.items

    if (viewMode.value === 'list') {
      pagination.itemCount = response.total
    }
  } catch (error) {
    message.error('获取案例列表失败')
  } finally {
    loading.value = false
  }
}

const fetchOptions = async () => {
  try {
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
      const themesResponse = await casesApi.getThemes()
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

const handleSearch = () => {
  pagination.page = 1
  fetchCases()
}

const resetSearch = () => {
  Object.assign(searchForm, {
    keyword: '',
    software_engineering_chapter: null,
    ideological_theme: null,
    case_type: null,
    difficulty_level: null,
  })
  handleSearch()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchCases()
}

const showCreateModal = () => {
  editingCase.value = null
  resetCaseForm()
  createModalVisible.value = true
}

const resetCaseForm = () => {
  Object.assign(caseForm, {
    title: '',
    content: '',
    software_engineering_chapter: null,
    ideological_theme: null,
    case_type: null,
    difficulty_level: 3,
    key_points: [],
    discussion_questions: [],
    teaching_suggestions: '',
    tags: [],
    is_public: true,
  })
}

const editCase = (case_item) => {
  editingCase.value = case_item
  Object.assign(caseForm, case_item)
  createModalVisible.value = true
}

const handleSubmitCase = async () => {
  try {
    await caseFormRef.value?.validate()
    submitLoading.value = true

    if (editingCase.value) {
      await request.put(`/ideological/cases/${editingCase.value.id}`, caseForm)
      message.success('案例更新成功')
    } else {
      await request.post('/ideological/cases/', caseForm)
      message.success('案例创建成功')
    }

    createModalVisible.value = false
    fetchCases()
  } catch (error) {
    message.error(editingCase.value ? '案例更新失败' : '案例创建失败')
  } finally {
    submitLoading.value = false
  }
}

const deleteCase = (case_item) => {
  dialog.warning({
    title: '删除确认',
    content: `确定要删除案例"${case_item.title}"吗？此操作不可恢复。`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await request.delete(`/ideological/cases/${case_item.id}`)
        message.success('案例删除成功')
        fetchCases()
      } catch (error) {
        message.error('案例删除失败')
      }
    },
  })
}

const viewCaseDetail = (case_item) => {
  // 跳转到案例详情页面
  message.info(`查看案例: ${case_item.title}`)
}

const toggleFavorite = async (case_item) => {
  // 实现收藏功能
  case_item.is_favorited = !case_item.is_favorited
  if (case_item.is_favorited) {
    case_item.usage_count += 1
  } else {
    case_item.usage_count = Math.max(0, case_item.usage_count - 1)
  }
}

const rateCase = (case_item) => {
  // 实现评分功能
  message.info(`评分案例: ${case_item.title}`)
}

const getCaseTypeLabel = (type) => {
  const option = caseTypeOptions.value.find(item => item.value === type)
  return option ? option.label : type
}

const getDifficultyTagType = (level) => {
  if (level <= 2) return 'success'
  if (level <= 4) return 'warning'
  return 'error'
}

const getCaseActionOptions = (case_item) => {
  return [
    { label: '查看详情', key: 'view' },
    { label: '编辑', key: 'edit' },
    { label: '复制', key: 'copy' },
    { label: '导出', key: 'export' },
    { type: 'divider' },
    { label: '删除', key: 'delete' },
  ]
}

const handleCaseAction = (key, case_item) => {
  switch (key) {
    case 'view':
      viewCaseDetail(case_item)
      break
    case 'edit':
      editCase(case_item)
      break
    case 'copy':
      message.success('案例已复制')
      break
    case 'export':
      message.info('导出功能开发中')
      break
    case 'delete':
      deleteCase(case_item)
      break
  }
}

const showImportModal = () => {
  message.info('导入功能开发中')
}

// 初始化
onMounted(() => {
  fetchOptions()
  fetchCases()
})
</script>

<style scoped>
.cases-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-header {
  background: linear-gradient(135deg, #18a058 0%, #36ad6a 100%);
  color: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(24, 160, 88, 0.2);
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

.cases-list {
  flex: 1;
}

.grid-view {
  min-height: 400px;
}

.case-card {
  height: 100%;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.case-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.case-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.case-title {
  font-weight: 600;
  flex: 1;
  margin-right: 8px;
}

.case-description {
  color: var(--n-text-color-depth-3);
  margin: 12px 0;
  line-height: 1.5;
}

.case-meta {
  margin-top: 12px;
}

.case-footer {
  margin-top: 12px;
}

.list-view {
  min-height: 400px;
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
