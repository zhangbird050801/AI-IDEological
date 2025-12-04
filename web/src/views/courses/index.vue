<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  NButton,
  NCard,
  NSpace,
  NEmpty,
  NSpin,
  NList,
  NListItem,
  NThing,
  NModal,
  NAlert,
  NInput,
  NTag,
  NDataTable,
  NPopconfirm,
  NInputNumber,
} from 'naive-ui'

import CommonPage from '@/components/page/CommonPage.vue'
import CrudModal from '@/components/table/CrudModal.vue'
import TheIcon from '@/components/icon/TheIcon.vue'

import api from '@/api'
import { useCRUD } from '@/composables'

defineOptions({ name: '章节管理' })

const router = useRouter()

const courseName = ref('软件工程')
const courseId = ref(1) // 软件工程课程ID固定为1
const chapters = ref([])
const loading = ref(false)
const draggingIndex = ref(null)
const chapterKnowledgePoints = ref({}) // 存储每个章节的知识点
const expandedChapters = ref(new Set()) // 存储展开的章节ID

// 知识点管理弹窗状态
const knowledgePointModalVisible = ref(false)
const currentChapter = ref(null)
const currentKnowledgePoints = ref([])
const knowledgePointFormVisible = ref(false)
const knowledgePointForm = ref({
  name: '',
  description: '',
  difficulty: 3,
  importance: 3,
  keywords: '',
})
const editingKnowledgePointId = ref(null)
const draggingKnowledgePointIndex = ref(null)

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
    course_id: null,
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

// Load chapters
async function loadChapters() {
  loading.value = true
  try {
    const response = await api.getChaptersByCourse(courseId.value)
    chapters.value = (response.data || response).sort((a, b) => a.order - b.order)
    // 加载每个章节的知识点
    await loadAllKnowledgePoints()
  } catch (error) {
    console.error('Failed to load chapters:', error)
    $message.error('加载章节列表失败')
  } finally {
    loading.value = false
  }
}

// Load knowledge points for all chapters
async function loadAllKnowledgePoints() {
  if (chapters.value.length === 0) return
  
  const extractPoints = (resp) => {
    const body = resp?.data ?? resp
    if (Array.isArray(body)) return body
    if (Array.isArray(body?.items)) return body.items
    if (Array.isArray(body?.results)) return body.results
    return []
  }
  
  const knowledgePointsMap = {}
  
  for (const chapter of chapters.value) {
    try {
      const response = await api.getKnowledgePointsByChapter(chapter.id)
      const points = extractPoints(response)
      // 按 order 字段排序
      knowledgePointsMap[chapter.id] = points.sort((a, b) => (a.order || 0) - (b.order || 0))
    } catch (error) {
      console.error(`加载章节 ${chapter.id} 的知识点失败:`, error)
      knowledgePointsMap[chapter.id] = []
    }
  }
  
  chapterKnowledgePoints.value = knowledgePointsMap
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

// Handle delete chapter
async function handleDeleteChapter(chapter) {
  chapterToDelete.value = chapter
  deleteModalVisible.value = true
  
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
  
  const draggedItem = chapters.value[draggingIndex.value]
  const newChapters = [...chapters.value]
  newChapters.splice(draggingIndex.value, 1)
  newChapters.splice(index, 0, draggedItem)
  
  chapters.value = newChapters
  draggingIndex.value = index
}

function handleDragEnd() {
  draggingIndex.value = null
  saveChapterOrder()
}

// Toggle chapter knowledge points expansion
function toggleKnowledgePoints(chapterId) {
  if (expandedChapters.value.has(chapterId)) {
    expandedChapters.value.delete(chapterId)
  } else {
    expandedChapters.value.add(chapterId)
  }
  // 触发响应式更新
  expandedChapters.value = new Set(expandedChapters.value)
}

// Open knowledge points management modal
function manageKnowledgePoints(chapter) {
  currentChapter.value = chapter
  currentKnowledgePoints.value = chapterKnowledgePoints.value[chapter.id] || []
  knowledgePointModalVisible.value = true
}

// Close knowledge point modal
function closeKnowledgePointModal() {
  knowledgePointModalVisible.value = false
  knowledgePointFormVisible.value = false
  currentChapter.value = null
  resetKnowledgePointForm()
}

// Show add knowledge point form
function showAddKnowledgePointForm() {
  editingKnowledgePointId.value = null
  resetKnowledgePointForm()
  knowledgePointFormVisible.value = true
}

// Show edit knowledge point form
function showEditKnowledgePointForm(kp) {
  editingKnowledgePointId.value = kp.id
  knowledgePointForm.value = {
    name: kp.name,
    description: kp.description || '',
    difficulty: kp.difficulty,
    importance: kp.importance,
    keywords: kp.keywords ? (Array.isArray(kp.keywords) ? kp.keywords.join(', ') : kp.keywords) : '',
  }
  knowledgePointFormVisible.value = true
}

// Reset knowledge point form
function resetKnowledgePointForm() {
  knowledgePointForm.value = {
    name: '',
    description: '',
    difficulty: 3,
    importance: 3,
    keywords: '',
  }
  editingKnowledgePointId.value = null
}

// Save knowledge point
async function saveKnowledgePoint() {
  if (!knowledgePointForm.value.name) {
    $message.warning('请输入知识点名称')
    return
  }
  
  try {
    // 计算 order：如果是新增，设置为最大值+1
    let order = 0
    if (!editingKnowledgePointId.value && currentKnowledgePoints.value.length > 0) {
      const maxOrder = Math.max(...currentKnowledgePoints.value.map(kp => kp.order || 0))
      order = maxOrder + 1
    } else if (editingKnowledgePointId.value) {
      // 编辑时保持原 order
      const existingKp = currentKnowledgePoints.value.find(kp => kp.id === editingKnowledgePointId.value)
      order = existingKp?.order || 0
    }
    
    const data = {
      name: knowledgePointForm.value.name,
      description: knowledgePointForm.value.description,
      difficulty: knowledgePointForm.value.difficulty,
      importance: knowledgePointForm.value.importance,
      keywords: knowledgePointForm.value.keywords ? knowledgePointForm.value.keywords.split(',').map(k => k.trim()).filter(k => k) : [],
      order: order,
      chapter_id: currentChapter.value.id,
    }
    
    if (editingKnowledgePointId.value) {
      // 编辑
      await api.updateKnowledgePoint(editingKnowledgePointId.value, data)
      $message.success('知识点更新成功')
    } else {
      // 新增
      await api.createKnowledgePoint(data)
      $message.success('知识点添加成功')
    }
    
    // 重新加载知识点
    await loadAllKnowledgePoints()
    currentKnowledgePoints.value = chapterKnowledgePoints.value[currentChapter.value.id] || []
    knowledgePointFormVisible.value = false
    resetKnowledgePointForm()
  } catch (error) {
    console.error('保存知识点失败:', error)
    $message.error('保存失败')
  }
}

// Delete knowledge point
async function deleteKnowledgePoint(kpId) {
  try {
    await api.deleteKnowledgePoint(kpId)
    $message.success('知识点删除成功')
    // 重新加载知识点
    await loadAllKnowledgePoints()
    currentKnowledgePoints.value = chapterKnowledgePoints.value[currentChapter.value.id] || []
  } catch (error) {
    console.error('删除知识点失败:', error)
    $message.error('删除失败')
  }
}

// Knowledge point drag and drop handlers
function handleKpDragStart(index) {
  draggingKnowledgePointIndex.value = index
}

function handleKpDragOver(event, index) {
  event.preventDefault()
  if (draggingKnowledgePointIndex.value === null || draggingKnowledgePointIndex.value === index) {
    return
  }
  
  const draggedItem = currentKnowledgePoints.value[draggingKnowledgePointIndex.value]
  const newKnowledgePoints = [...currentKnowledgePoints.value]
  newKnowledgePoints.splice(draggingKnowledgePointIndex.value, 1)
  newKnowledgePoints.splice(index, 0, draggedItem)
  
  currentKnowledgePoints.value = newKnowledgePoints
  draggingKnowledgePointIndex.value = index
}

function handleKpDragEnd() {
  draggingKnowledgePointIndex.value = null
  saveKnowledgePointOrder()
}

// Save knowledge point order
async function saveKnowledgePointOrder() {
  try {
    const reorderedKnowledgePoints = currentKnowledgePoints.value.map((kp, index) => ({
      id: kp.id,
      order: index,
    }))
    
    await api.reorderKnowledgePoints(reorderedKnowledgePoints)
    $message.success('知识点顺序已更新')
    // 重新加载知识点
    await loadAllKnowledgePoints()
    currentKnowledgePoints.value = chapterKnowledgePoints.value[currentChapter.value.id] || []
  } catch (error) {
    console.error('保存知识点顺序失败:', error)
    $message.error('保存顺序失败，请重试')
    // 重新加载知识点以恢复正确的顺序
    await loadAllKnowledgePoints()
    currentKnowledgePoints.value = chapterKnowledgePoints.value[currentChapter.value.id] || []
  }
}

// Save chapter order
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
    await loadChapters()
  }
}

onMounted(() => {
  loadChapters()
})
</script>

<template>
  <CommonPage :title="`${courseName} - 章节管理`">
    <template #action>
      <NButton type="primary" @click="handleAddChapter">
        <TheIcon icon="material-symbols:add" :size="18" class="mr-5" />
        添加章节
      </NButton>
    </template>

    <NCard>
      <NSpin :show="loading">
        <NList v-if="chapters.length > 0" hoverable clickable>
          <NListItem
            v-for="(chapter, index) in chapters"
            :key="chapter.id"
            draggable="true"
            :class="{ 'dragging': draggingIndex === index }"
            @dragstart="handleDragStart(index)"
            @dragover="handleDragOver($event, index)"
            @dragend="handleDragEnd"
            style="cursor: move; border-bottom: 1px solid #f0f0f0;"
          >
            <NThing>
              <template #avatar>
                <TheIcon icon="material-symbols:drag-indicator" :size="24" style="cursor: grab;" />
              </template>
              <template #header>
                <NSpace align="center">
                  <span style="font-weight: 500;">{{ chapter.name }}</span>
                  <span style="color: #999; font-size: 12px;">顺序: {{ chapter.order }}</span>
                  <NTag
                    v-if="chapterKnowledgePoints[chapter.id]"
                    size="small"
                    type="info"
                    :bordered="false"
                    style="cursor: pointer;"
                    @click.stop="toggleKnowledgePoints(chapter.id)"
                  >
                    <template #icon>
                      <TheIcon :icon="expandedChapters.has(chapter.id) ? 'material-symbols:expand-less' : 'material-symbols:expand-more'" :size="14" />
                    </template>
                    {{ chapterKnowledgePoints[chapter.id].length }} 个知识点
                  </NTag>
                </NSpace>
              </template>
              <template #description>
                <div>
                  <div style="margin-bottom: 8px;">{{ chapter.description || '暂无描述' }}</div>
                  <!-- 知识点列表 -->
                  <div v-if="expandedChapters.has(chapter.id) && chapterKnowledgePoints[chapter.id] && chapterKnowledgePoints[chapter.id].length > 0" style="margin-top: 12px; padding-top: 12px; border-top: 1px dashed #e0e0e0;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                      <div style="font-weight: 500; color: #666; font-size: 13px;">📚 知识点列表：</div>
                      <NButton size="tiny" type="primary" @click.stop="manageKnowledgePoints(chapter)">
                        <template #icon>
                          <TheIcon icon="material-symbols:edit" :size="14" />
                        </template>
                        管理知识点
                      </NButton>
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 6px;">
                      <div
                        v-for="(point, idx) in chapterKnowledgePoints[chapter.id]"
                        :key="point.id"
                        style="padding: 6px 10px; background: #f9f9f9; border-radius: 4px; font-size: 13px;"
                      >
                        <div style="margin-bottom: 4px;">
                          <NSpace align="center" :size="8">
                            <span style="color: #999; font-weight: 500;">{{ idx + 1 }}.</span>
                            <span style="color: #333; font-weight: 500;">{{ point.name }}</span>
                            <NTag size="tiny" type="warning" :bordered="false">难度: {{ point.difficulty }}</NTag>
                            <NTag size="tiny" type="success" :bordered="false">重要性: {{ point.importance }}</NTag>
                          </NSpace>
                        </div>
                        <div v-if="point.description" style="margin-left: 24px; color: #666; font-size: 12px; margin-bottom: 4px;">{{ point.description }}</div>
                        <div v-if="point.keywords && point.keywords.length > 0" style="margin-left: 24px; display: flex; gap: 4px; flex-wrap: wrap;">
                          <NTag
                            v-for="(keyword, kidx) in (Array.isArray(point.keywords) ? point.keywords : [])"
                            :key="kidx"
                            size="tiny"
                            type="info"
                            :bordered="false"
                          >
                            {{ keyword }}
                          </NTag>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div v-else-if="expandedChapters.has(chapter.id) && chapterKnowledgePoints[chapter.id]" style="margin-top: 12px; padding-top: 12px; border-top: 1px dashed #e0e0e0;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                      <div style="font-weight: 500; color: #666; font-size: 13px;">📚 知识点列表：</div>
                      <NButton size="tiny" type="primary" @click.stop="manageKnowledgePoints(chapter)">
                        <template #icon>
                          <TheIcon icon="material-symbols:add" :size="14" />
                        </template>
                        添加知识点
                      </NButton>
                    </div>
                    <div style="padding: 12px; background: #fafafa; border-radius: 4px; text-align: center; color: #999; font-size: 12px;">
                      暂无知识点，点击上方按钮添加
                    </div>
                  </div>
                </div>
              </template>
              <template #action>
                <NSpace>
                  <NButton
                    size="small"
                    type="primary"
                    @click.stop="handleEditChapter(chapter)"
                  >
                    <TheIcon icon="material-symbols:edit" :size="16" class="mr-5" />
                    编辑
                  </NButton>
                  <NButton
                    size="small"
                    type="error"
                    @click.stop="handleDeleteChapter(chapter)"
                  >
                    <TheIcon icon="material-symbols:delete-outline" :size="16" class="mr-5" />
                    删除
                  </NButton>
                </NSpace>
              </template>
            </NThing>
          </NListItem>
        </NList>
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

    <!-- Knowledge Points Management Modal -->
    <NModal
      v-model:show="knowledgePointModalVisible"
      preset="card"
      :title="`管理知识点 - ${currentChapter?.name || ''}`"
      style="width: 800px;"
      :segmented="{ content: true }"
    >
      <NSpace vertical :size="16">
        <!-- 添加/编辑表单 -->
        <div v-if="knowledgePointFormVisible" style="padding: 16px; background: #f5f5f5; border-radius: 8px;">
          <h4 style="margin: 0 0 12px 0;">{{ editingKnowledgePointId ? '编辑知识点' : '添加知识点' }}</h4>
          <NSpace vertical :size="12">
            <div>
              <label style="display: block; margin-bottom: 4px; font-weight: 500;">名称*</label>
              <NInput v-model:value="knowledgePointForm.name" placeholder="请输入知识点名称" />
            </div>
            <div>
              <label style="display: block; margin-bottom: 4px; font-weight: 500;">描述</label>
              <NInput
                v-model:value="knowledgePointForm.description"
                type="textarea"
                placeholder="请输入知识点描述"
                :rows="3"
              />
            </div>
            <div>
              <label style="display: block; margin-bottom: 4px; font-weight: 500;">关键词</label>
              <NInput
                v-model:value="knowledgePointForm.keywords"
                placeholder="请输入关键词，多个关键词用逗号分隔"
              />
              <div style="margin-top: 4px; font-size: 12px; color: #999;">示例：软件, 工程, 开发</div>
            </div>
            <NSpace>
              <div>
                <label style="display: block; margin-bottom: 4px; font-weight: 500;">难度 (1-5)</label>
                <NInputNumber v-model:value="knowledgePointForm.difficulty" :min="1" :max="5" style="width: 120px;" />
              </div>
              <div>
                <label style="display: block; margin-bottom: 4px; font-weight: 500;">重要性 (1-5)</label>
                <NInputNumber v-model:value="knowledgePointForm.importance" :min="1" :max="5" style="width: 120px;" />
              </div>
            </NSpace>
            <NSpace>
              <NButton type="primary" @click="saveKnowledgePoint">保存</NButton>
              <NButton @click="knowledgePointFormVisible = false">取消</NButton>
            </NSpace>
          </NSpace>
        </div>

        <!-- 知识点列表 -->
        <div v-if="!knowledgePointFormVisible">
          <NSpace justify="space-between" style="margin-bottom: 12px;">
            <h4 style="margin: 0;">知识点列表 ({{ currentKnowledgePoints.length }}个)</h4>
            <NButton type="primary" size="small" @click="showAddKnowledgePointForm">
              <template #icon>
                <TheIcon icon="material-symbols:add" :size="16" />
              </template>
              添加知识点
            </NButton>
          </NSpace>
          
          <div v-if="currentKnowledgePoints.length > 0" style="max-height: 400px; overflow-y: auto;">
            <div
              v-for="(kp, idx) in currentKnowledgePoints"
              :key="kp.id"
              draggable="true"
              :class="{ 'dragging': draggingKnowledgePointIndex === idx }"
              style="padding: 12px; margin-bottom: 8px; background: white; border: 1px solid #e0e0e0; border-radius: 6px; cursor: move; transition: all 0.3s ease;"
              @dragstart="handleKpDragStart(idx)"
              @dragover="handleKpDragOver($event, idx)"
              @dragend="handleKpDragEnd"
            >
              <div style="display: flex; justify-content: space-between; align-items: start;">
                <div style="flex: 1;">
                  <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                    <TheIcon icon="material-symbols:drag-indicator" :size="18" style="color: #999; cursor: grab;" />
                    <span style="font-weight: 500;">{{ idx + 1 }}. {{ kp.name }}</span>
                    <NTag size="tiny" type="warning" :bordered="false">难度: {{ kp.difficulty }}</NTag>
                    <NTag size="tiny" type="success" :bordered="false">重要性: {{ kp.importance }}</NTag>
                  </div>
                  <div v-if="kp.description" style="color: #666; font-size: 13px; margin-bottom: 4px;">{{ kp.description }}</div>
                  <div v-if="kp.keywords && kp.keywords.length > 0" style="display: flex; gap: 4px; flex-wrap: wrap;">
                    <NTag
                      v-for="(keyword, kidx) in (Array.isArray(kp.keywords) ? kp.keywords : [])"
                      :key="kidx"
                      size="tiny"
                      type="info"
                      :bordered="false"
                    >
                      {{ keyword }}
                    </NTag>
                  </div>
                </div>
                <NSpace>
                  <NButton size="tiny" @click="showEditKnowledgePointForm(kp)">
                    <template #icon>
                      <TheIcon icon="material-symbols:edit" :size="14" />
                    </template>
                  </NButton>
                  <NPopconfirm @positive-click="deleteKnowledgePoint(kp.id)">
                    <template #trigger>
                      <NButton size="tiny" type="error">
                        <template #icon>
                          <TheIcon icon="material-symbols:delete-outline" :size="14" />
                        </template>
                      </NButton>
                    </template>
                    确定删除该知识点吗？
                  </NPopconfirm>
                </NSpace>
              </div>
            </div>
          </div>
          
          <NEmpty v-else description="暂无知识点，点击上方按钮添加" style="padding: 40px 0;" />
        </div>
      </NSpace>

      <template #footer>
        <NSpace justify="end">
          <NButton @click="closeKnowledgePointModal">关闭</NButton>
        </NSpace>
      </template>
    </NModal>
  </CommonPage>
</template>

<style scoped>
.dragging {
  opacity: 0.5;
}

:deep(.n-list-item) {
  transition: all 0.3s ease;
}

:deep(.n-list-item:hover) {
  background-color: #f5f5f5;
}
</style>
