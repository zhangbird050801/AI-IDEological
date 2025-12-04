<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NButton,
  NInput,
  NCard,
  NSpace,
  NEmpty,
  NSpin,
  NDataTable,
  NPopconfirm,
  NTag,
  NSelect,
} from 'naive-ui'

import CommonPage from '@/components/page/CommonPage.vue'
import CrudModal from '@/components/table/CrudModal.vue'
import KnowledgePointForm from '@/components/course/KnowledgePointForm.vue'
import TheIcon from '@/components/icon/TheIcon.vue'

import api from '@/api'
import { useCRUD } from '@/composables'
import { renderIcon } from '@/utils'

defineOptions({ name: '知识点管理' })

const route = useRoute()
const router = useRouter()

const courseId = computed(() => parseInt(route.params.courseId || route.query.courseId))
const chapterId = ref(parseInt(route.params.chapterId || route.query.chapterId) || null)

const courseName = ref('')
const chapters = ref([])
const knowledgePoints = ref([])
const loading = ref(false)
const keyword = ref('')

// CRUD composable
const {
  modalVisible,
  modalTitle,
  modalAction,
  modalLoading,
  handleSave,
  modalForm,
  modalFormRef,
  handleEdit,
  handleDelete,
  handleAdd,
} = useCRUD({
  name: '知识点',
  initForm: {
    chapter_id: chapterId.value,
    name: '',
    description: '',
    keywords: [],
  },
  doCreate: api.createKnowledgePoint,
  doUpdate: (data) => api.updateKnowledgePoint(data.id, data),
  doDelete: (params) => api.deleteKnowledgePoint(params.id),
  refresh: loadKnowledgePoints,
})

// Load course details
async function loadCourse() {
  try {
    const response = await api.getCourse(courseId.value)
    const course = response.data || response
    courseName.value = course.name
  } catch (error) {
    console.error('Failed to load course:', error)
    $message.error('加载课程信息失败')
  }
}

// Load chapters for dropdown
async function loadChapters() {
  try {
    const response = await api.getChaptersByCourse(courseId.value)
    chapters.value = (response.data || response).sort((a, b) => a.order - b.order)
  } catch (error) {
    console.error('Failed to load chapters:', error)
    $message.error('加载章节列表失败')
  }
}

// Load knowledge points
async function loadKnowledgePoints() {
  if (!chapterId.value) {
    knowledgePoints.value = []
    return
  }

  const extractPoints = (resp) => {
    const body = resp?.data ?? resp
    if (Array.isArray(body)) return body
    if (Array.isArray(body?.items)) return body.items
    if (Array.isArray(body?.results)) return body.results
    return []
  }
  
  loading.value = true
  try {
    const response = await api.getKnowledgePointsByChapter(chapterId.value)
    knowledgePoints.value = extractPoints(response)
  } catch (error) {
    console.error('Failed to load knowledge points:', error)
    $message.error('加载知识点列表失败')
  } finally {
    loading.value = false
  }
}

// Filtered knowledge points based on keyword
const filteredKnowledgePoints = computed(() => {
  if (!keyword.value) return knowledgePoints.value
  
  const kw = keyword.value.toLowerCase()
  return knowledgePoints.value.filter(kp => 
    kp.name.toLowerCase().includes(kw) ||
    (kp.description && kp.description.toLowerCase().includes(kw)) ||
    (kp.keywords && kp.keywords.some(k => k.toLowerCase().includes(kw)))
  )
})

// Chapter options for select
const chapterOptions = computed(() => 
  chapters.value.map(ch => ({
    label: ch.name,
    value: ch.id,
  }))
)

// Handle chapter change
function handleChapterChange(value) {
  chapterId.value = value
  loadKnowledgePoints()
}

// Handle add knowledge point
function handleAddKnowledgePoint() {
  if (!chapterId.value) {
    $message.warning('请先选择章节')
    return
  }
  modalForm.value.chapter_id = chapterId.value
  handleAdd()
}

// Handle edit knowledge point
function handleEditKnowledgePoint(kp) {
  handleEdit(kp)
}

// Table columns
const columns = [
  {
    title: '知识点名称',
    key: 'name',
    width: 200,
    ellipsis: { tooltip: true },
  },
  {
    title: '描述',
    key: 'description',
    width: 300,
    ellipsis: { tooltip: true },
    render(row) {
      return row.description || '-'
    },
  },
  {
    title: '关键词',
    key: 'keywords',
    width: 250,
    render(row) {
      if (!row.keywords || row.keywords.length === 0) return '-'
      return row.keywords.map(keyword => 
        h(NTag, { 
          type: 'info', 
          size: 'small',
          style: 'margin-right: 4px; margin-bottom: 4px;'
        }, { default: () => keyword })
      )
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 180,
    align: 'center',
    fixed: 'right',
    render(row) {
      return [
        h(
          NButton,
          {
            size: 'small',
            type: 'primary',
            style: 'margin-right: 8px;',
            onClick: () => handleEditKnowledgePoint(row),
          },
          {
            default: () => '编辑',
            icon: renderIcon('material-symbols:edit', { size: 16 }),
          }
        ),
        h(
          NPopconfirm,
          {
            onPositiveClick: () => handleDelete({ id: row.id }),
          },
          {
            trigger: () =>
              h(
                NButton,
                {
                  size: 'small',
                  type: 'error',
                },
                {
                  default: () => '删除',
                  icon: renderIcon('material-symbols:delete-outline', { size: 16 }),
                }
              ),
            default: () => '确定删除该知识点吗？',
          }
        ),
      ]
    },
  },
]

// Go back
function goBack() {
  router.push('/aigc/chapters')
}

onMounted(() => {
  if (!courseId.value) {
    $message.error('缺少课程ID')
    goBack()
    return
  }
  loadCourse()
  loadChapters()
  if (chapterId.value) {
    loadKnowledgePoints()
  }
})
</script>

<template>
  <CommonPage :title="`知识点管理 - ${courseName}`">
    <template #action>
      <NSpace>
        <NButton @click="goBack">
          <TheIcon icon="material-symbols:arrow-back" :size="18" class="mr-5" />
          返回课程列表
        </NButton>
        <NButton type="primary" @click="handleAddKnowledgePoint">
          <TheIcon icon="material-symbols:add" :size="18" class="mr-5" />
          添加知识点
        </NButton>
      </NSpace>
    </template>

    <NCard>
      <!-- Filter controls -->
      <NSpace vertical :size="16" style="margin-bottom: 16px;">
        <NSpace>
          <div style="width: 300px;">
            <label style="display: block; margin-bottom: 8px; font-weight: 500;">选择章节</label>
            <NSelect
              v-model:value="chapterId"
              :options="chapterOptions"
              placeholder="请选择章节"
              clearable
              @update:value="handleChapterChange"
            />
          </div>
          <div style="width: 300px;">
            <label style="display: block; margin-bottom: 8px; font-weight: 500;">搜索关键词</label>
            <NInput
              v-model:value="keyword"
              placeholder="搜索知识点名称、描述或关键词"
              clearable
            >
              <template #prefix>
                <TheIcon icon="material-symbols:search" :size="18" />
              </template>
            </NInput>
          </div>
        </NSpace>
      </NSpace>

      <!-- Table -->
      <NSpin :show="loading">
        <NDataTable
          v-if="chapterId"
          :columns="columns"
          :data="filteredKnowledgePoints"
          :pagination="{ pageSize: 10 }"
          :scroll-x="1000"
        />
        <NEmpty 
          v-else 
          description="请先选择章节以查看知识点"
          style="padding: 40px 0;"
        />
      </NSpin>
    </NCard>

    <!-- Create/Edit Modal -->
    <CrudModal
      v-model:visible="modalVisible"
      :title="modalTitle"
      :loading="modalLoading"
      @save="handleSave"
    >
      <KnowledgePointForm ref="modalFormRef" v-model="modalForm" />
    </CrudModal>
  </CommonPage>
</template>
