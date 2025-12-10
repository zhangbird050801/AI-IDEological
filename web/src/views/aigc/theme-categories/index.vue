<template>
  <div class="theme-category-management">
    <n-card title="思政主题分类管理" :bordered="false">
      <template #header-extra>
        <n-space>
          <n-button type="primary" @click="handleAdd(null)">
            <template #icon>
              <n-icon><Icon icon="ant-design:plus-outlined" /></n-icon>
            </template>
            添加根分类
          </n-button>
          <n-button @click="handleRefresh">
            <template #icon>
              <n-icon><Icon icon="ant-design:reload-outlined" /></n-icon>
            </template>
            刷新
          </n-button>
          <n-switch v-model:value="expandAll" @update:value="handleExpandChange">
            <template #checked>全部展开</template>
            <template #unchecked>全部折叠</template>
          </n-switch>
        </n-space>
      </template>

      <n-spin :show="loading">
        <theme-category-tree
          :data="categories"
          :expand-all="expandAll"
          :case-count="caseCountStats"
          @edit="handleEdit"
          @delete="handleDelete"
          @add-child="handleAdd"
          @move="handleMove"
          @view-cases="handleViewCases"
        />
        
        <n-empty
          v-if="!loading && categories.length === 0"
          description="暂无分类数据"
          style="margin-top: 40px"
        />
      </n-spin>
    </n-card>

    <!-- 编辑/新增弹窗 -->
    <n-modal
      v-model:show="showModal"
      :title="modalTitle"
      preset="card"
      style="width: 600px"
      :mask-closable="false"
    >
      <n-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-placement="left"
        label-width="100"
      >
        <n-form-item label="分类名称" path="name">
          <n-input v-model:value="formData.name" placeholder="请输入分类名称" />
        </n-form-item>

        <n-form-item label="分类描述" path="description">
          <n-input
            v-model:value="formData.description"
            type="textarea"
            placeholder="请输入分类描述"
            :rows="3"
          />
        </n-form-item>

        <n-form-item label="父分类" path="parent_id">
          <n-select
            v-model:value="formData.parent_id"
            :options="parentOptions"
            placeholder="请选择父分类（不选则为根分类）"
            clearable
            filterable
          />
        </n-form-item>

        <n-form-item label="排序" path="order">
          <n-input-number
            v-model:value="formData.order"
            placeholder="请输入排序值"
            :min="0"
            style="width: 100%"
          />
        </n-form-item>

        <n-form-item label="是否启用" path="is_active">
          <n-switch v-model:value="formData.is_active" />
        </n-form-item>
      </n-form>

      <template #footer>
        <n-space justify="end">
          <n-button @click="showModal = false">取消</n-button>
          <n-button type="primary" :loading="submitting" @click="handleSubmit">
            确定
          </n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 查看案例列表弹窗 -->
    <n-modal
      v-model:show="showCasesModal"
      :title="`${currentCategoryName} - 案例列表`"
      preset="card"
      style="width: 900px; max-height: 80vh"
      :mask-closable="true"
    >
      <n-spin :show="casesLoading">
        <n-scrollbar style="max-height: 60vh">
        <n-list hoverable clickable>
          <n-list-item v-for="case_item in categoryCases" :key="case_item.id" @click="viewCaseDetail(case_item)">
            <n-thing>
              <template #header>
                <n-space align="center">
                  <span>{{ case_item.title }}</span>
                  <n-tag size="small" type="info">{{ case_item.software_engineering_chapter }}</n-tag>
                  <n-tag size="small">{{ case_item.case_type }}</n-tag>
                  <n-rate :value="case_item.difficulty_level" readonly size="small" :count="5" />
                </n-space>
              </template>
              <template #description>
                {{ case_item.content }}
              </template>
              <template #footer>
                <n-space size="small">
                  <n-text depth="3">评分: {{ case_item.rating.toFixed(1) }}</n-text>
                  <n-text depth="3">使用: {{ case_item.usage_count }}次</n-text>
                  <n-text depth="3">{{ case_item.is_public ? '公开' : '私有' }}</n-text>
                </n-space>
              </template>
            </n-thing>
          </n-list-item>
        </n-list>
        </n-scrollbar>
        
        <n-empty
          v-if="!casesLoading && categoryCases.length === 0"
          description="该分类下暂无案例"
          style="margin-top: 20px"
        />
      </n-spin>
    </n-modal>

    <!-- 案例详情弹窗 -->
    <n-modal
      v-model:show="showCaseDetailModal"
      title="案例详情"
      preset="card"
      style="width: 800px; max-height: 80vh"
      :mask-closable="true"
    >
      <div v-if="currentCase">
        <n-descriptions :column="2" bordered>
          <n-descriptions-item label="标题">{{ currentCase.title }}</n-descriptions-item>
          <n-descriptions-item label="章节">{{ currentCase.software_engineering_chapter }}</n-descriptions-item>
          <n-descriptions-item label="类型">{{ currentCase.case_type }}</n-descriptions-item>
          <n-descriptions-item label="难度">
            <n-rate :value="currentCase.difficulty_level" readonly size="small" :count="5" />
          </n-descriptions-item>
          <n-descriptions-item label="评分">{{ currentCase.rating.toFixed(1) }}</n-descriptions-item>
          <n-descriptions-item label="使用次数">{{ currentCase.usage_count }}</n-descriptions-item>
        </n-descriptions>
        
        <n-divider />
        
        <n-text strong>案例内容：</n-text>
        <div style="margin-top: 12px; white-space: pre-wrap;">{{ currentCase.content }}</div>
      </div>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { 
  NCard, NButton, NSpace, NIcon, NSpin, NEmpty, NModal, NForm, 
  NFormItem, NInput, NInputNumber, NSelect, NSwitch, NList, NListItem,
  NThing, NTag, NRate, NText, NDescriptions, NDescriptionsItem, NDivider,
  NScrollbar, useMessage, useDialog 
} from 'naive-ui'
import { Icon } from '@iconify/vue'
import ThemeCategoryTree from '@/components/theme/ThemeCategoryTree.vue'
import { themeCategoriesApi } from '@/api/ideological'

const message = useMessage()
const dialog = useDialog()

// 数据状态
const categories = ref([])
const loading = ref(false)
const expandAll = ref(true)
const caseCountStats = ref({})

// 案例列表相关
const showCasesModal = ref(false)
const casesLoading = ref(false)
const categoryCases = ref([])
const currentCategoryName = ref('')

// 案例详情相关
const showCaseDetailModal = ref(false)
const currentCase = ref(null)

// 弹窗状态
const showModal = ref(false)
const modalTitle = computed(() => formData.value.id ? '编辑分类' : '添加分类')
const formRef = ref(null)
const submitting = ref(false)

// 表单数据
const formData = ref({
  id: null,
  name: '',
  description: '',
  parent_id: null,
  order: 0,
  is_active: true
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' },
    { min: 1, max: 100, message: '分类名称长度在1-100个字符', trigger: 'blur' }
  ]
}

// 父分类选项（只显示根分类）
const parentOptions = computed(() => {
  // categories.value 是树形结构，第一层就是根分类
  const options = categories.value
    .filter(item => item.id !== formData.value.id) // 排除当前编辑的分类
    .map(item => ({
      label: item.name,
      value: item.id,
      disabled: !item.is_active
    }))
  
  return options
})

// 获取分类树
async function fetchCategories() {
  try {
    loading.value = true
    const response = await themeCategoriesApi.getTree()
    categories.value = response.data || response
    
    // 同时获取案例数量统计
    await fetchCaseCountStats()
  } catch (error) {
    console.error('获取分类失败:', error)
    message.error('获取分类失败')
  } finally {
    loading.value = false
  }
}

// 获取案例数量统计
async function fetchCaseCountStats() {
  try {
    const response = await themeCategoriesApi.getCaseCountStats()
    caseCountStats.value = response.data || response
  } catch (error) {
    console.error('获取案例数量统计失败:', error)
  }
}

// 刷新
function handleRefresh() {
  fetchCategories()
}

// 展开/折叠切换
function handleExpandChange(value) {
  expandAll.value = value
}

// 添加分类
function handleAdd(parentId) {
  formData.value = {
    id: null,
    name: '',
    description: '',
    parent_id: parentId,
    order: 0,
    is_active: true
  }
  showModal.value = true
}

// 编辑分类
async function handleEdit(id) {
  try {
    const response = await themeCategoriesApi.getById(id)
    const category = response.data || response
    formData.value = {
      id: category.id,
      name: category.name,
      description: category.description,
      parent_id: category.parent_id,
      order: category.order,
      is_active: category.is_active
    }
    showModal.value = true
  } catch (error) {
    console.error('获取分类详情失败:', error)
    message.error('获取分类详情失败')
  }
}

// 删除分类
function handleDelete(id) {
  dialog.warning({
    title: '确认删除',
    content: '确定要删除该分类吗？如果该分类下有子分类，则无法删除。',
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await themeCategoriesApi.delete(id)
        message.success('删除成功')
        await fetchCategories()
      } catch (error) {
        console.error('删除分类失败:', error)
        message.error(error.response?.data?.detail || '删除分类失败')
      }
    }
  })
}

// 移动分类（拖拽）
async function handleMove(data) {
  try {
    await themeCategoriesApi.move(data.id, { parent_id: data.parent_id, order: data.order })
    message.success('移动成功')
    await fetchCategories()
  } catch (error) {
    console.error('移动分类失败:', error)
    message.error('移动分类失败')
  }
}

// 提交表单
async function handleSubmit() {
  try {
    await formRef.value?.validate()
    submitting.value = true
    
    const data = { ...formData.value }
    delete data.id
    
    if (formData.value.id) {
      await themeCategoriesApi.update(formData.value.id, data)
      message.success('更新成功')
    } else {
      await themeCategoriesApi.create(data)
      message.success('添加成功')
    }
    
    showModal.value = false
    await fetchCategories()
  } catch (error) {
    if (error?.errorFields) {
      message.error('请检查表单填写')
      return
    }
    console.error('保存分类失败:', error)
    message.error(error.response?.data?.detail || '保存分类失败')
  } finally {
    submitting.value = false
  }
}

// 查看某个分类的案例列表
async function handleViewCases(categoryId) {
  try {
    casesLoading.value = true
    showCasesModal.value = true
    
    const response = await themeCategoriesApi.getCategoryCases(categoryId)
    const data = response.data || response
    
    currentCategoryName.value = data.category?.name || '未知分类'
    categoryCases.value = data.cases || []
  } catch (error) {
    console.error('获取案例列表失败:', error)
    message.error('获取案例列表失败')
  } finally {
    casesLoading.value = false
  }
}

// 查看案例详情
function viewCaseDetail(case_item) {
  currentCase.value = case_item
  showCaseDetailModal.value = true
}

// 初始化
onMounted(() => {
  fetchCategories()
})
</script>

<style scoped>
.theme-category-management {
  padding: 20px;
}
</style>
