<template>
  <AppPage>
    <n-card title="生成历史" size="small">
      <n-data-table
        :columns="columns"
        :data="histories"
        :loading="loading"
        :pagination="pagination"
        @update:page="handlePageChange"
        @update:page-size="handlePageSizeChange"
      />
    </n-card>

    <n-modal v-model:show="ratingVisible" preset="card" title="评分" style="width: 360px">
      <n-space vertical>
        <n-rate v-model:value="ratingValue" allow-half />
        <n-space justify="end">
          <n-button @click="ratingVisible = false">取消</n-button>
          <n-button type="primary" :loading="ratingSubmitting" @click="submitRating">提交</n-button>
        </n-space>
      </n-space>
    </n-modal>
  </AppPage>
</template>

<script setup>
import { h, onMounted, reactive, ref } from 'vue'
import { NButton, NCard, NDataTable, NModal, NRate, NSpace, useMessage } from 'naive-ui'
import AppPage from '@/components/page/AppPage.vue'
import { getGenerationHistory, rateGenerationHistory } from '@/api/aigc-history'
import { themeCategoriesApi } from '@/api/ideological'

const message = useMessage()
const histories = ref([])
const loading = ref(false)
const ratingVisible = ref(false)
const ratingSubmitting = ref(false)
const ratingValue = ref(5)
const currentHistoryId = ref(null)
const themeMap = ref({})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  pageCount: 0,
  itemCount: 0,
  showSizePicker: true,
  pageSizes: [10, 20, 50],
})

function formatTime(value) {
  if (!value) return ''
  const date = new Date(value)
  return date.toLocaleString('zh-CN')
}

function truncate(text, length = 80) {
  if (!text) return ''
  if (text.length <= length) return text
  return `${text.slice(0, length)}...`
}

function resolveThemeLabel(themeId) {
  if (!themeId) return '-'
  return themeMap.value[themeId] || `主题 ${themeId}`
}

const columns = [
  {
    title: '时间',
    key: 'created_at',
    width: 160,
    render: (row) => formatTime(row.created_at),
  },
  {
    title: '章节',
    key: 'software_engineering_chapter',
    width: 140,
    render: (row) => row.software_engineering_chapter || '-',
  },
  {
    title: '思政主题',
    key: 'theme_category_id',
    width: 140,
    render: (row) => resolveThemeLabel(row.theme_category_id),
  },
  {
    title: '用户输入',
    key: 'user_input',
    render: (row) => truncate(row.user_input),
  },
  {
    title: '生成内容',
    key: 'generated_content',
    render: (row) => truncate(row.generated_content, 120),
  },
  {
    title: '评分',
    key: 'user_rating',
    width: 120,
    render: (row) =>
      h(NRate, { value: row.user_rating || 0, readonly: true, size: 'small', allowHalf: true }),
  },
  {
    title: '操作',
    key: 'actions',
    width: 120,
    render: (row) =>
      h(
        NButton,
        {
          size: 'small',
          onClick: () => openRating(row),
        },
        { default: () => '评分' }
      ),
  },
]

async function fetchThemes() {
  try {
    const response = await themeCategoriesApi.getList()
    const items = response?.data?.data || response?.data || response || []
    if (Array.isArray(items)) {
      themeMap.value = Object.fromEntries(
        items.filter((item) => item.is_active).map((item) => [item.id, item.name])
      )
    }
  } catch (error) {
    themeMap.value = {}
  }
}

async function fetchHistory() {
  loading.value = true
  try {
    const res = await getGenerationHistory({
      page: pagination.page,
      page_size: pagination.pageSize,
    })
    const data = res?.data || res || {}
    histories.value = data.items || []
    pagination.itemCount = data.total || 0
    pagination.pageCount = data.pages || 0
  } catch (error) {
    message.error('获取生成历史失败')
  } finally {
    loading.value = false
  }
}

function handlePageChange(page) {
  pagination.page = page
  fetchHistory()
}

function handlePageSizeChange(size) {
  pagination.pageSize = size
  pagination.page = 1
  fetchHistory()
}

function openRating(row) {
  currentHistoryId.value = row.id
  ratingValue.value = row.user_rating || 5
  ratingVisible.value = true
}

async function submitRating() {
  if (!currentHistoryId.value) return
  ratingSubmitting.value = true
  try {
    await rateGenerationHistory(currentHistoryId.value, ratingValue.value)
    message.success('评分成功')
    ratingVisible.value = false
    fetchHistory()
  } catch (error) {
    message.error('评分失败')
  } finally {
    ratingSubmitting.value = false
  }
}

onMounted(async () => {
  await fetchThemes()
  await fetchHistory()
})
</script>
