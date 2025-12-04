<script setup>
import { ref, onMounted } from 'vue'
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
} from 'naive-ui'

import CommonPage from '@/components/page/CommonPage.vue'
import CrudModal from '@/components/table/CrudModal.vue'
import TheIcon from '@/components/icon/TheIcon.vue'

import api from '@/api'
import { useCRUD } from '@/composables'

defineOptions({ name: '章节管理' })

const courseName = ref('软件工程')
const courseId = ref(1) // 软件工程课程ID固定为1
const chapters = ref([])
const loading = ref(false)
const draggingIndex = ref(null)

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
  } catch (error) {
    console.error('Failed to load chapters:', error)
    $message.error('加载章节列表失败')
  } finally {
    loading.value = false
  }
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
                <span style="font-weight: 500;">{{ chapter.name }}</span>
                <span style="margin-left: 12px; color: #999; font-size: 12px;">
                  顺序: {{ chapter.order }}
                </span>
              </template>
              <template #description>
                {{ chapter.description || '暂无描述' }}
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
