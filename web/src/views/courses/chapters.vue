<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NButton,
  NInput,
  NCard,
  NSpace,
  NEmpty,
  NSpin,
  NList,
  NListItem,
  NThing,
  NIcon,
  NModal,
  NAlert,
  NTag,
  NCollapse,
  NCollapseItem,
} from 'naive-ui'
import { DragOutlined, EditOutlined, DeleteOutlined, PlusOutlined } from '@vicons/antd'

import CommonPage from '@/components/page/CommonPage.vue'
import CrudModal from '@/components/table/CrudModal.vue'
import TheIcon from '@/components/icon/TheIcon.vue'

import api from '@/api'
import { useCRUD } from '@/composables'

defineOptions({ name: '章节管理' })

const route = useRoute()
const router = useRouter()

const courseId = computed(() => parseInt(route.params.courseId || route.query.courseId))
const courseName = ref('')
const chapters = ref([])
const loading = ref(false)
const draggingIndex = ref(null)
const chapterKnowledgePoints = ref({}) // 存储每个章节的知识点

// Delete confirmation state
const deleteModalVisible = ref(false)
const deleteModalLoading = ref(false)
const chapterToDelete = ref(null)
const knowledgePointCount = ref(0)

// CRUD composable for chapter management
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
  name: '章节',
  initForm: {
    course_id: courseId.value,
    name: '',
    description: '',
    order: 0,
    is_active: true,
  },
  doCreate: api.createChapter,
  doUpdate: (data) => api.updateChapter(data.id, data),
  doDelete: (params) => api.deleteChapter(params.id),
  refresh: loadChapters,
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

// Load chapters
async function loadChapters() {
  console.log('=== 开始加载章节 ===')
  console.log('课程ID:', courseId.value)
  loading.value = true
  try {
    const response = await api.getChaptersByCourse(courseId.value)
    console.log('章节API响应:', response)
    chapters.value = (response.data || response).sort((a, b) => a.order - b.order)
    console.log('章节数据已加载:', chapters.value.length, '个章节')
    
    // 加载每个章节的知识点
    console.log('准备加载知识点...')
    await loadAllKnowledgePoints()
    console.log('知识点加载完成')
  } catch (error) {
    console.error('Failed to load chapters:', error)
    $message.error('加载章节列表失败')
  } finally {
    loading.value = false
    console.log('=== 章节加载结束 ===')
  }
}

// Load knowledge points for all chapters
async function loadAllKnowledgePoints() {
  if (chapters.value.length === 0) {
    console.log('没有章节，跳过加载知识点')
    return
  }

  const extractPoints = (resp) => {
    const body = resp?.data ?? resp
    if (Array.isArray(body)) return body
    if (Array.isArray(body?.items)) return body.items
    if (Array.isArray(body?.results)) return body.results
    return []
  }
  
  const knowledgePointsMap = {}
  
  console.log('开始加载知识点，章节数量:', chapters.value.length)
  console.log('章节列表:', chapters.value.map(c => ({ id: c.id, name: c.name })))
  
  for (const chapter of chapters.value) {
    try {
      console.log(`正在加载章节 ${chapter.name} (ID: ${chapter.id}) 的知识点...`)
      const response = await api.getKnowledgePointsByChapter(chapter.id)
      console.log(`章节 ${chapter.id} 的原始响应:`, response)
      
      const points = extractPoints(response)
      knowledgePointsMap[chapter.id] = points
      
      console.log(`章节 ${chapter.name} (ID: ${chapter.id}) 的知识点数量:`, knowledgePointsMap[chapter.id].length)
      if (knowledgePointsMap[chapter.id].length > 0) {
        console.log('知识点数据:', knowledgePointsMap[chapter.id])
      }
    } catch (error) {
      console.error(`加载章节 ${chapter.id} 的知识点失败:`, error)
      console.error('错误详情:', error.response?.data || error.message)
      knowledgePointsMap[chapter.id] = []
    }
  }
  
  chapterKnowledgePoints.value = knowledgePointsMap
  console.log('所有知识点加载完成，最终数据:', chapterKnowledgePoints.value)
}

// Handle add chapter
function handleAddChapter() {
  modalForm.value.course_id = courseId.value
  handleAdd()
}

// Handle edit chapter
function handleEditChapter(chapter) {
  handleEdit(chapter)
}

// Handle delete chapter - show confirmation modal with cascade warning
async function handleDeleteChapter(chapter) {
  chapterToDelete.value = chapter
  deleteModalVisible.value = true
  
  // Check if chapter has knowledge points
  try {
    const response = await api.getKnowledgePointsByChapter(chapter.id)
    const knowledgePoints = response.data || response
    knowledgePointCount.value = Array.isArray(knowledgePoints) ? knowledgePoints.length : 0
  } catch (error) {
    console.error('Failed to check knowledge points:', error)
    knowledgePointCount.value = 0
  }
}

// Confirm delete chapter
async function confirmDeleteChapter() {
  if (!chapterToDelete.value) return
  
  deleteModalLoading.value = true
  try {
    await api.deleteChapter(chapterToDelete.value.id)
    $message.success('章节删除成功')
    deleteModalVisible.value = false
    chapterToDelete.value = null
    knowledgePointCount.value = 0
    await loadChapters()
  } catch (error) {
    console.error('Failed to delete chapter:', error)
    $message.error(error.response?.data?.detail || '删除章节失败')
  } finally {
    deleteModalLoading.value = false
  }
}

// Cancel delete
function cancelDeleteChapter() {
  deleteModalVisible.value = false
  chapterToDelete.value = null
  knowledgePointCount.value = 0
}

// Drag and drop handlers
function handleDragStart(index) {
  draggingIndex.value = index
}

function handleDragOver(event, index) {
  event.preventDefault()
  if (draggingIndex.value === null || draggingIndex.value === index) {
    return
  }
  
  // Reorder the array
  const draggedItem = chapters.value[draggingIndex.value]
  const newChapters = [...chapters.value]
  newChapters.splice(draggingIndex.value, 1)
  newChapters.splice(index, 0, draggedItem)
  
  chapters.value = newChapters
  draggingIndex.value = index
}

function handleDragEnd() {
  draggingIndex.value = null
  // Persist the new order
  saveChapterOrder()
}

// Save chapter order to backend
async function saveChapterOrder() {
  try {
    const reorderedChapters = chapters.value.map((chapter, index) => ({
      id: chapter.id,
      order_num: index + 1,
    }))
    
    await api.reorderChapters(reorderedChapters)
    $message.success('章节顺序已更新')
    await loadChapters()
  } catch (error) {
    console.error('Failed to reorder chapters:', error)
    $message.error('更新章节顺序失败')
    await loadChapters() // Reload to reset order
  }
}

// Go back to course list
function goBack() {
  router.push('/courses')
}

// View knowledge points for a chapter
function viewKnowledgePoints(chapter) {
  router.push({
    path: '/courses/knowledge-points',
    query: {
      chapterId: chapter.id,
      chapterName: chapter.name
    }
  })
}

onMounted(() => {
  if (!courseId.value) {
    $message.error('缺少课程ID')
    goBack()
    return
  }
  loadCourse()
  loadChapters()
})
</script>

<template>
  <CommonPage :title="`章节管理 - ${courseName}`">
    <template #action>
      <NSpace>
        <NButton @click="goBack">
          <TheIcon icon="material-symbols:arrow-back" :size="18" class="mr-5" />
          返回课程列表
        </NButton>
        <NButton type="primary" @click="handleAddChapter">
          <TheIcon icon="material-symbols:add" :size="18" class="mr-5" />
          添加章节
        </NButton>
      </NSpace>
    </template>

    <NCard>
      <!-- 调试信息 -->
      <div style="background: #f0f0f0; padding: 12px; margin-bottom: 16px; border-radius: 4px; font-size: 12px;">
        <div>章节数量: {{ chapters.length }}</div>
        <div>知识点数据: {{ Object.keys(chapterKnowledgePoints).length }} 个章节有数据</div>
        <div v-for="(points, chapterId) in chapterKnowledgePoints" :key="chapterId">
          章节 {{ chapterId }}: {{ points.length }} 个知识点
        </div>
      </div>
      
      <NSpin :show="loading">
        <div v-if="chapters.length > 0" class="chapters-list">
          <div
            v-for="(chapter, index) in chapters"
            :key="chapter.id"
            draggable="true"
            :class="{ 'chapter-item': true, 'dragging': draggingIndex === index }"
            @dragstart="handleDragStart(index)"
            @dragover="handleDragOver($event, index)"
            @dragend="handleDragEnd"
          >
            <div class="chapter-header">
              <div class="chapter-left">
                <NIcon size="24" style="cursor: grab; margin-right: 12px;">
                  <DragOutlined />
                </NIcon>
                <div class="chapter-info">
                  <div class="chapter-title">
                    <span style="font-weight: 500; font-size: 16px;">{{ chapter.name }}</span>
                    <span style="margin-left: 12px; color: #999; font-size: 12px;">
                      顺序: {{ chapter.order }}
                    </span>
                    <NTag
                      v-if="chapterKnowledgePoints[chapter.id]"
                      size="small"
                      type="info"
                      :bordered="false"
                      style="margin-left: 8px;"
                    >
                      {{ chapterKnowledgePoints[chapter.id].length }} 个知识点
                    </NTag>
                  </div>
                  <div class="chapter-description">
                    {{ chapter.description || '暂无描述' }}
                  </div>
                </div>
              </div>
              <div class="chapter-actions">
                <NButton
                  size="small"
                  @click.stop="viewKnowledgePoints(chapter)"
                >
                  <template #icon>
                    <TheIcon icon="material-symbols:lightbulb-outline" :size="16" />
                  </template>
                  知识点
                </NButton>
                <NButton
                  size="small"
                  @click.stop="handleEditChapter(chapter)"
                >
                  <template #icon>
                    <TheIcon icon="material-symbols:edit" :size="16" />
                  </template>
                  编辑
                </NButton>
                <NButton
                  size="small"
                  type="error"
                  @click.stop="handleDeleteChapter(chapter)"
                >
                  <template #icon>
                    <TheIcon icon="material-symbols:delete-outline" :size="16" />
                  </template>
                  删除
                </NButton>
              </div>
            </div>

            <!-- 知识点列表 -->
            <div v-if="chapterKnowledgePoints[chapter.id] && chapterKnowledgePoints[chapter.id].length > 0" class="knowledge-points-section">
              <div class="knowledge-points-list">
                <div
                  v-for="(point, idx) in chapterKnowledgePoints[chapter.id]"
                  :key="point.id"
                  class="knowledge-point-item"
                >
                  <div class="knowledge-point-content">
                    <div class="knowledge-point-header">
                      <span class="knowledge-point-order">{{ idx + 1 }}.</span>
                      <span class="knowledge-point-name">{{ point.name }}</span>
                      <NSpace :size="4" style="margin-left: 8px;">
                        <NTag size="tiny" type="warning" :bordered="false">
                          难度: {{ point.difficulty }}
                        </NTag>
                        <NTag size="tiny" type="success" :bordered="false">
                          重要性: {{ point.importance }}
                        </NTag>
                      </NSpace>
                    </div>
                    <div v-if="point.description" class="knowledge-point-description">
                      {{ point.description }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="no-knowledge-points">
              <span style="color: #999; font-size: 13px;">暂无知识点</span>
            </div>
          </div>
        </div>
        <NEmpty v-else description="暂无章节，点击上方按钮添加章节" />
      </NSpin>
    </NCard>

    <!-- Create/Edit Modal -->
    <CrudModal
      v-model:visible="modalVisible"
      :title="modalTitle"
      :loading="modalLoading"
      @save="handleSave"
    >
      <NSpace vertical>
        <div>
          <label style="display: block; margin-bottom: 8px;">章节名称 *</label>
          <NInput
            v-model:value="modalForm.name"
            placeholder="请输入章节名称"
            maxlength="200"
            show-count
          />
        </div>
        <div>
          <label style="display: block; margin-bottom: 8px;">章节描述</label>
          <NInput
            v-model:value="modalForm.description"
            type="textarea"
            placeholder="请输入章节描述"
            :rows="4"
          />
        </div>
      </NSpace>
    </CrudModal>

    <!-- Delete Confirmation Modal -->
    <NModal
      v-model:show="deleteModalVisible"
      preset="dialog"
      title="删除章节确认"
      :positive-text="knowledgePointCount > 0 ? '确认删除' : '删除'"
      negative-text="取消"
      :loading="deleteModalLoading"
      @positive-click="confirmDeleteChapter"
      @negative-click="cancelDeleteChapter"
    >
      <NSpace vertical>
        <div v-if="chapterToDelete">
          <p>确定要删除章节 <strong>{{ chapterToDelete.name }}</strong> 吗？</p>
          <p style="color: #999; font-size: 14px;">删除后将无法恢复。</p>
        </div>
        
        <!-- Cascade delete warning -->
        <NAlert
          v-if="knowledgePointCount > 0"
          type="warning"
          title="级联删除警告"
          style="margin-top: 12px;"
        >
          该章节包含 <strong>{{ knowledgePointCount }}</strong> 个知识点。
          删除章节将同时删除所有关联的知识点，此操作不可恢复。
        </NAlert>
      </NSpace>
    </NModal>
  </CommonPage>
</template>

<style scoped>
.chapters-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chapter-item {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  cursor: move;
  transition: all 0.3s ease;
}

.chapter-item:hover {
  background-color: #f9f9f9;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.chapter-item.dragging {
  opacity: 0.5;
}

.chapter-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  width: 100%;
  gap: 16px;
}

.chapter-left {
  display: flex;
  align-items: flex-start;
  flex: 1;
  min-width: 0;
}

.chapter-info {
  flex: 1;
  min-width: 0;
  padding-top: 2px;
}

.chapter-title {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.chapter-description {
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}

.chapter-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
  align-items: flex-start;
}

/* 知识点部分 */
.knowledge-points-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px dashed #e0e0e0;
}

.knowledge-points-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.knowledge-point-item {
  padding: 8px 12px;
  background: #f9f9f9;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.knowledge-point-item:hover {
  background: #f0f0f0;
}

.knowledge-point-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.knowledge-point-header {
  display: flex;
  align-items: center;
  gap: 4px;
}

.knowledge-point-order {
  color: #999;
  font-size: 13px;
  font-weight: 500;
  min-width: 24px;
}

.knowledge-point-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.knowledge-point-description {
  font-size: 13px;
  color: #666;
  line-height: 1.5;
  margin-left: 28px;
}

.no-knowledge-points {
  margin-top: 12px;
  padding: 12px;
  text-align: center;
  background: #fafafa;
  border-radius: 6px;
}

/* 深色模式适配 */
html[data-theme="dark"] .chapter-item {
  background: #18181c;
  border-color: #3a3a3a;
}

html[data-theme="dark"] .chapter-item:hover {
  background-color: #1f1f23;
}

html[data-theme="dark"] .chapter-description {
  color: #999;
}

html[data-theme="dark"] .knowledge-points-section {
  border-top-color: #3a3a3a;
}

html[data-theme="dark"] .knowledge-point-item {
  background: #1f1f23;
}

html[data-theme="dark"] .knowledge-point-item:hover {
  background: #252529;
}

html[data-theme="dark"] .knowledge-point-name {
  color: #e0e0e0;
}

html[data-theme="dark"] .knowledge-point-description {
  color: #999;
}

html[data-theme="dark"] .no-knowledge-points {
  background: #1f1f23;
}
</style>
