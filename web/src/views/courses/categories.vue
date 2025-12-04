<script setup>
import { ref, h, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import {
  NButton,
  NCard,
  NSpace,
  NSpin,
  NTree,
  NEmpty,
  NInput,
  NModal,
  NPopconfirm,
  NTag,
  NList,
  NListItem,
  NThing,
  NText,
  NCollapse,
  NCollapseItem,
  NGrid,
  NGridItem,
  NDescriptions,
  NDescriptionsItem,
  NRate,
  NScrollbar,
  NOl,
  NLi,
  NBreadcrumb,
  NBreadcrumbItem,
  NIcon,
  NDivider,
} from 'naive-ui'
import { Icon } from '@iconify/vue'

import CommonPage from '@/components/page/CommonPage.vue'
import CrudModal from '@/components/table/CrudModal.vue'
import CategoryTree from '@/components/category/CategoryTree.vue'
import TheIcon from '@/components/icon/TheIcon.vue'

import api from '@/api'
import { request } from '@/utils'
import { useCRUD } from '@/composables'

defineOptions({ name: '案例分类管理' })

const treeData = ref([])
const loading = ref(false)
const expandedKeys = ref([])
const filterKeyword = ref('')
const router = useRouter()
const message = useMessage()
const selectedCategory = ref(null)
const categoryCase = ref([])
const loadingCases = ref(false)
const showCaseList = ref(false)
const detailModalVisible = ref(false)
const currentCase = ref(null)

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
  name: '分类',
  initForm: {
    name: '',
    description: '',
    parent_id: null,
  },
  doCreate: api.createCategory,
  doUpdate: (data) => api.updateCategory(data.id, data),
  doDelete: (params) => api.deleteCategory(params.id),
  refresh: loadCategories,
})

// Load category tree
async function loadCategories() {
  loading.value = true
  try {
    const response = await api.getCategoryTree()
    const categories = response.data || response
    treeData.value = buildTreeData(categories)
    
    // Restore expanded keys from session storage
    const savedKeys = sessionStorage.getItem('category-expanded-keys')
    if (savedKeys) {
      expandedKeys.value = JSON.parse(savedKeys)
    } else {
      // 默认展开顶级节点
      expandedKeys.value = treeData.value.map((n) => n.key)
    }
  } catch (error) {
    console.error('Failed to load categories:', error)
    message.error('加载分类树失败')
  } finally {
    loading.value = false
  }
}

// Build tree data for NTree component
function buildTreeData(categories) {
  if (!Array.isArray(categories)) {
    console.warn('buildTreeData: categories is not an array', categories)
    return []
  }

  // 递归映射节点，确保所有字段都正确传递
  const mapNode = (cat) => {
    if (!cat) {
      console.warn('buildTreeData: invalid category node', cat)
      return null
    }
    
    const node = {
      // NTree 需要的字段
      key: cat.id,
      label: cat.name || `分类-${cat.id}`,
      
      // 保留所有原始字段
      id: cat.id,
      name: cat.name,
      parent_id: cat.parent_id,
      description: cat.description,
      icon: cat.icon,
      color: cat.color,
      order: cat.order,
      is_active: cat.is_active,
      level: cat.level || 0,
      case_count: cat.case_count || 0,
      created_at: cat.created_at,
      updated_at: cat.updated_at,
      
      // 递归处理子节点
      children: [],
    }
    
    // 递归处理子节点
    if (Array.isArray(cat.children) && cat.children.length > 0) {
      node.children = cat.children.map(mapNode).filter(n => n !== null)
    }
    
    return node
  }
  
  return categories.map(mapNode).filter(n => n !== null)
}

// 查看分类下的案例
async function handleViewInCases(node) {
  console.log('查看分类案例:', node)
  selectedCategory.value = node
  showCaseList.value = true
  
  // 收集当前分类及其所有子分类的ID
  const categoryIds = collectCategoryIds(node)
  console.log('包含子分类的ID列表:', categoryIds)
  
  await loadCategoryCases(categoryIds)
}

// 递归收集分类及其所有子分类的ID
function collectCategoryIds(category) {
  const ids = [category.id]
  if (category.children && category.children.length > 0) {
    category.children.forEach(child => {
      ids.push(...collectCategoryIds(child))
    })
  }
  return ids
}

// 加载分类下的案例（包含子分类）
async function loadCategoryCases(categoryIds) {
  loadingCases.value = true
  try {
    console.log('正在加载分类ID为', categoryIds, '的案例')
    
    const params = {
      category_ids: categoryIds,  // 传递分类ID数组
      page: 1,
      page_size: 100,
    }
    
    console.log('请求参数:', params)
    
    const response = await request.get('/ideological/cases/', { 
      params,
      paramsSerializer: (params) => {
        // 使用自定义序列化器来处理数组参数
        const searchParams = new URLSearchParams()
        Object.keys(params).forEach(key => {
          const value = params[key]
          if (Array.isArray(value)) {
            value.forEach(v => searchParams.append(key, v))
          } else if (value !== null && value !== undefined) {
            searchParams.append(key, value)
          }
        })
        return searchParams.toString()
      }
    })
    
    console.log('获取分类案例响应:', response)
    
    // 响应数据可能在 response.data 或 response 中
    const data = response?.data || response
    categoryCase.value = data?.items || []
    
    console.log('分类案例数据:', categoryCase.value)
    
    if (categoryCase.value.length === 0) {
      console.warn('该分类及其子分类下没有找到案例')
    }
  } catch (error) {
    console.error('Failed to load category cases:', error)
    console.error('错误详情:', error.response?.data || error.message)
    message.error('加载案例失败: ' + (error.response?.data?.detail || error.message))
    categoryCase.value = []
  } finally {
    loadingCases.value = false
  }
}

// 显示案例详情
async function goToCaseDetail(caseItem) {
  try {
    // 获取完整的案例详情
    const response = await request.get(`/ideological/cases/${caseItem.id}`)
    const caseDetail = response?.data || response
    
    // 确保收藏状态
    const favorites = getFavorites()
    caseDetail.is_favorited = favorites.includes(caseDetail.id)
    if (!caseDetail.favorite_count) {
      caseDetail.favorite_count = 0
    }
    
    currentCase.value = caseDetail
    detailModalVisible.value = true
  } catch (error) {
    console.error('获取案例详情失败:', error)
    message.error('获取案例详情失败')
  }
}

// 收藏功能
const FAVORITES_STORAGE_KEY = 'aigc_case_favorites'

const getFavorites = () => {
  try {
    const favorites = localStorage.getItem(FAVORITES_STORAGE_KEY)
    return favorites ? JSON.parse(favorites) : []
  } catch (error) {
    console.error('读取收藏数据失败:', error)
    return []
  }
}

const saveFavorites = (favorites) => {
  try {
    localStorage.setItem(FAVORITES_STORAGE_KEY, JSON.stringify(favorites))
  } catch (error) {
    console.error('保存收藏数据失败:', error)
  }
}

const toggleFavorite = (caseItem) => {
  const favorites = getFavorites()
  const caseId = caseItem.id
  const isFavorited = favorites.includes(caseId)
  
  if (isFavorited) {
    const index = favorites.indexOf(caseId)
    favorites.splice(index, 1)
    caseItem.is_favorited = false
    caseItem.favorite_count = (caseItem.favorite_count || 1) - 1
    message.success('已取消收藏')
  } else {
    favorites.push(caseId)
    caseItem.is_favorited = true
    caseItem.favorite_count = (caseItem.favorite_count || 0) + 1
    message.success('收藏成功')
  }
  
  saveFavorites(favorites)
}

const formatContent = (content) => {
  if (!content) return ''
  return content.replace(/\n/g, '<br>')
}

const getCategoryName = (catId) => {
  const findCategory = (categories, id) => {
    for (const cat of categories) {
      if (cat.id === id) return cat.name
      if (cat.children) {
        const found = findCategory(cat.children, id)
        if (found) return found
      }
    }
    return null
  }
  return findCategory(treeData.value, catId) || `分类${catId}`
}

const getCaseTypeLabel = (type) => {
  const types = {
    'real_case': '真实案例',
    'hypothetical': '假设案例',
    'mixed': '混合案例'
  }
  return types[type] || type
}

// 导出案例为Markdown
const exportCase = (caseItem) => {
  const markdown = `# ${caseItem.title}

## 基本信息

- **软件工程章节**: ${caseItem.software_engineering_chapter}
- **思政主题**: ${caseItem.ideological_theme}
- **案例类型**: ${getCaseTypeLabel(caseItem.case_type)}
- **难度等级**: ${caseItem.difficulty_level}/5
- **评分**: ${caseItem.rating?.toFixed(1) || 0} (${caseItem.rating_count}人评价)

## 案例内容

${caseItem.content}

## 关键知识点

${caseItem.key_points?.map(p => `- ${p}`).join('\n') || '无'}

## 讨论问题

${caseItem.discussion_questions?.map((q, i) => `${i + 1}. ${q}`).join('\n') || '无'}

## 教学建议

${caseItem.teaching_suggestions || '无'}

## 标签

${caseItem.tags?.map(t => `#${t}`).join(' ') || '无'}
`

  const blob = new Blob([markdown], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${caseItem.title}.md`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  message.success('导出成功')
}

// 关闭案例列表
function closeCaseList() {
  showCaseList.value = false
  selectedCategory.value = null
  categoryCase.value = []
}

// Handle add root category
function handleAddRoot() {
  modalForm.value.parent_id = null
  handleAdd()
}

// Handle add child category
function handleAddChild(node) {
  modalForm.value.parent_id = node.id
  handleAdd()
}

// Handle edit category
function handleEditCategory(node) {
  handleEdit(node)
}

// Handle delete category
async function handleDeleteCategory(node) {
  if (node.children && node.children.length > 0) {
    message.warning('该分类包含子分类，请先删除子分类')
    return
  }
  
  if (node.case_count > 0) {
    message.warning(`该分类包含 ${node.case_count} 个案例，请先移除关联`)
    return
  }
  
  await handleDelete({ id: node.id })
}

// Handle node drag and drop
async function handleDrop(data) {
  const { node, dragNode, dropPosition } = data
  
  // Prevent dropping on itself or its descendants
  if (isDescendant(dragNode, node)) {
    $message.warning('不能将分类移动到其子分类下')
    await loadCategories()
    return
  }
  
  try {
    let newParentId = null
    
    if (dropPosition === 'inside') {
      newParentId = node.id
    } else {
      newParentId = node.parent_id
    }
    
    await api.moveCategory(dragNode.id, {
      parent_id: newParentId,
      order_num: 0, // Backend will handle order
    })
    
    $message.success('分类移动成功')
    await loadCategories()
  } catch (error) {
    console.error('Failed to move category:', error)
    $message.error('移动分类失败')
    await loadCategories()
  }
}

// Check if node is descendant of another node
function isDescendant(node, potentialAncestor) {
  if (node.id === potentialAncestor.id) return true
  
  if (potentialAncestor.children) {
    for (const child of potentialAncestor.children) {
      if (isDescendant(node, child)) return true
    }
  }
  
  return false
}

// Expand all nodes
function expandAll() {
  const keys = []
  const collectKeys = (nodes) => {
    nodes.forEach(node => {
      keys.push(node.key)
      if (node.children) {
        collectKeys(node.children)
      }
    })
  }
  collectKeys(treeData.value)
  expandedKeys.value = keys
  saveExpandedKeys()
}

// Collapse all nodes
function collapseAll() {
  expandedKeys.value = []
  saveExpandedKeys()
}

// Save expanded keys to session storage
function saveExpandedKeys() {
  sessionStorage.setItem('category-expanded-keys', JSON.stringify(expandedKeys.value))
}

// Handle expand change
function handleExpandedKeysChange(keys) {
  expandedKeys.value = keys
  saveExpandedKeys()
}

// Render tree label with case count - 点击整行显示案例
function renderLabel({ option }) {
  return h(
    'div',
    { 
      style: 'display: flex; align-items: center; justify-content: space-between; width: 100%; cursor: pointer;',
      onClick: (e) => {
        // 点击分类名称时显示案例列表（包括0案例的情况）
        e.stopPropagation()
        handleViewInCases(option)
      }
    },
    [
      h('span', { style: 'font-weight: 500;' }, option.label),
      h(
        NTag,
        {
          size: 'small',
          type: option.case_count > 0 ? 'info' : 'default',
          style: { marginLeft: '8px' }
        },
        { default: () => `${option.case_count || 0} 案例` }
      )
    ]
  )
}

// Render tree suffix with action buttons
function renderSuffix({ option }) {
  return h(
    'div',
    { style: 'display: flex; align-items: center; gap: 6px;' },
    [
      h(
        NSpace,
        { size: 4 },
        {
          default: () => [
            h(
              NButton,
              {
                size: 'tiny',
                type: 'primary',
                onClick: (e) => {
                  e.stopPropagation()
                  handleAddChild(option)
                },
              },
              { default: () => '添加子类' }
            ),
            h(
              NButton,
              {
                size: 'tiny',
                type: 'default',
                onClick: (e) => {
                  e.stopPropagation()
                  handleEditCategory(option)
                },
              },
              { default: () => '编辑' }
            ),
            h(
              NPopconfirm,
              {
                onPositiveClick: () => handleDeleteCategory(option),
              },
              {
                trigger: () =>
                  h(
                    NButton,
                    {
                      size: 'tiny',
                      type: 'error',
                      onClick: (e) => e.stopPropagation(),
                    },
                    { default: () => '删除' }
                  ),
                default: () => '确定删除该分类吗？',
              }
            ),
          ],
        }
      ),
    ]
  )
}

onMounted(() => {
  loadCategories()
  // 默认展开根节点
  expandedKeys.value = [0]
})
</script>

<template>
  <CommonPage title="案例分类管理">
    <template #action>
      <NSpace>
        <NInput
          v-model:value="filterKeyword"
          placeholder="搜索分类"
          clearable
          style="width: 220px"
        />
        <NButton @click="expandAll">
          <TheIcon icon="material-symbols:unfold-more" :size="18" class="mr-5" />
          展开全部
        </NButton>
        <NButton @click="collapseAll">
          <TheIcon icon="material-symbols:unfold-less" :size="18" class="mr-5" />
          收起全部
        </NButton>
        <NButton type="primary" @click="handleAddRoot">
          <TheIcon icon="material-symbols:add" :size="18" class="mr-5" />
          添加根分类
        </NButton>
      </NSpace>
    </template>

    <n-grid :cols="showCaseList ? 2 : 1" :x-gap="16">
      <n-grid-item>
        <NCard title="分类树">
          <NSpin :show="loading">
            <NTree
              v-if="treeData.length > 0"
              :data="treeData"
              :pattern="filterKeyword"
              :expanded-keys="expandedKeys"
              :render-label="renderLabel"
              :render-suffix="renderSuffix"
              draggable
              block-line
              @drop="handleDrop"
              @update:expanded-keys="handleExpandedKeysChange"
            />
            <NEmpty v-else description="暂无分类，点击上方按钮添加根分类" />
          </NSpin>
        </NCard>
      </n-grid-item>

      <n-grid-item v-if="showCaseList">
        <NCard>
          <template #header>
            <n-space justify="space-between" align="center">
              <span>{{ selectedCategory?.name }} - 案例列表</span>
              <NButton text @click="closeCaseList">
                <template #icon>
                  <TheIcon icon="material-symbols:close" :size="18" />
                </template>
              </NButton>
            </n-space>
          </template>

          <NSpin :show="loadingCases">
            <NList v-if="categoryCase.length > 0" hoverable clickable>
              <NListItem
                v-for="caseItem in categoryCase"
                :key="caseItem.id"
                @click="goToCaseDetail(caseItem)"
              >
                <template #prefix>
                  <n-icon size="40" color="#667eea">
                    <Icon icon="mdi:book-open-page-variant" />
                  </n-icon>
                </template>
                <NThing>
                  <template #header>
                    <n-space align="center" :size="12">
                      <span style="font-weight: 600; font-size: 15px;">{{ caseItem.title }}</span>
                      <NTag 
                        v-if="caseItem.ideological_theme" 
                        size="small" 
                        type="success"
                        :bordered="false"
                        round
                      >
                        <template #icon>
                          <n-icon><Icon icon="mdi:lightbulb-on" /></n-icon>
                        </template>
                        {{ caseItem.ideological_theme }}
                      </NTag>
                    </n-space>
                  </template>
                  <template #description>
                    <n-space vertical :size="8">
                      <NText depth="3" style="line-height: 1.6;">
                        {{ caseItem.content?.substring(0, 120) }}{{ caseItem.content?.length > 120 ? '...' : '' }}
                      </NText>
                      <n-space :size="12" align="center">
                        <n-space :size="4" align="center">
                          <n-icon size="14" color="#2080f0">
                            <Icon icon="mdi:book-outline" />
                          </n-icon>
                          <NText depth="3" style="font-size: 12px;">
                            {{ caseItem.software_engineering_chapter }}
                          </NText>
                        </n-space>
                        <n-divider vertical />
                        <n-space :size="4" align="center">
                          <n-icon size="14" color="#f0a020">
                            <Icon icon="mdi:star" />
                          </n-icon>
                          <NText depth="3" style="font-size: 12px;">
                            {{ caseItem.rating?.toFixed(1) || 0 }}
                          </NText>
                        </n-space>
                        <n-divider vertical />
                        <n-space :size="4" align="center">
                          <n-icon size="14" color="#18a058">
                            <Icon icon="mdi:eye-outline" />
                          </n-icon>
                          <NText depth="3" style="font-size: 12px;">
                            {{ caseItem.usage_count || 0 }}次
                          </NText>
                        </n-space>
                      </n-space>
                    </n-space>
                  </template>
                </NThing>
              </NListItem>
            </NList>
            <NEmpty v-else description="该分类下暂无案例" />
          </NSpin>
        </NCard>
      </n-grid-item>
    </n-grid>

    <!-- Create/Edit Modal -->
    <CrudModal
      v-model:visible="modalVisible"
      :title="modalTitle"
      :loading="modalLoading"
      @save="handleSave"
    >
      <NSpace vertical>
        <div>
          <label style="display: block; margin-bottom: 8px;">分类名称 *</label>
          <NInput
            v-model:value="modalForm.name"
            placeholder="请输入分类名称"
            maxlength="100"
            show-count
          />
        </div>
        <div>
          <label style="display: block; margin-bottom: 8px;">分类描述</label>
          <NInput
            v-model:value="modalForm.description"
            type="textarea"
            placeholder="请输入分类描述"
            :rows="4"
            maxlength="500"
            show-count
          />
        </div>
        <div v-if="modalForm.parent_id" style="color: #999; font-size: 12px;">
          将作为子分类添加
        </div>
      </NSpace>
    </CrudModal>

    <!-- 案例详情弹窗 -->
    <n-modal
      v-model:show="detailModalVisible"
      preset="card"
      style="width: 900px; max-height: 80vh"
      :title="currentCase?.title"
      :bordered="false"
      :segmented="{ content: 'soft' }"
    >
      <n-scrollbar style="max-height: 60vh" v-if="currentCase">
        <n-space vertical size="large">
          <!-- 核心思政主题 - 突出显示 -->
          <n-card size="small" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
            <n-space align="center" justify="space-between">
              <n-space align="center">
                <n-icon size="24">
                  <Icon icon="mdi:lightbulb-on" />
                </n-icon>
                <div>
                  <div style="font-size: 12px; opacity: 0.9;">核心思政主题</div>
                  <div style="font-size: 18px; font-weight: 600; margin-top: 4px;">
                    {{ currentCase.ideological_theme }}
                  </div>
                </div>
              </n-space>
              <n-space align="center">
                <n-rate :value="currentCase.rating" readonly allow-half size="small" style="--n-item-color-active: #ffd700;" />
                <span style="font-size: 14px;">{{ currentCase.rating?.toFixed(1) || 0 }}</span>
              </n-space>
            </n-space>
          </n-card>

          <!-- 基本信息 -->
          <n-descriptions :column="2" bordered size="small">
            <n-descriptions-item label="软件工程章节">
              <n-tag type="info" size="small">{{ currentCase.software_engineering_chapter }}</n-tag>
            </n-descriptions-item>
            <n-descriptions-item label="案例类型">
              <n-tag size="small">{{ getCaseTypeLabel(currentCase.case_type) }}</n-tag>
            </n-descriptions-item>
            <n-descriptions-item label="难度等级">
              <n-rate :value="currentCase.difficulty_level" readonly :count="5" size="small" />
            </n-descriptions-item>
            <n-descriptions-item label="使用次数">
              {{ currentCase.usage_count }} 次
            </n-descriptions-item>
            <n-descriptions-item label="收藏次数">
              <n-space align="center" :size="4">
                <n-icon color="#f0a020">
                  <Icon icon="ant-design:heart-filled" />
                </n-icon>
                <span>{{ currentCase.favorite_count || 0 }} 次</span>
              </n-space>
            </n-descriptions-item>
            <n-descriptions-item label="评价人数">
              {{ currentCase.rating_count }} 人
            </n-descriptions-item>
          </n-descriptions>

          <!-- 课程关联层级 -->
          <n-card 
            title="课程关联" 
            size="small" 
            v-if="currentCase.course_name || currentCase.chapter_name || currentCase.knowledge_point_name"
          >
            <n-space vertical size="small">
              <div v-if="currentCase.course_name" style="display: flex; align-items: center;">
                <n-icon size="18" style="margin-right: 8px;">
                  <Icon icon="ant-design:book-outlined" />
                </n-icon>
                <n-breadcrumb>
                  <n-breadcrumb-item>
                    <n-tag type="primary">{{ currentCase.course_name }}</n-tag>
                  </n-breadcrumb-item>
                  <n-breadcrumb-item v-if="currentCase.chapter_name">
                    <n-tag type="info">{{ currentCase.chapter_name }}</n-tag>
                  </n-breadcrumb-item>
                  <n-breadcrumb-item v-if="currentCase.knowledge_point_name">
                    <n-tag type="success">{{ currentCase.knowledge_point_name }}</n-tag>
                  </n-breadcrumb-item>
                </n-breadcrumb>
              </div>
            </n-space>
          </n-card>

          <!-- 案例分类 - 次要信息 -->
          <n-card 
            size="small" 
            v-if="currentCase.category_ids && currentCase.category_ids.length > 0"
          >
            <template #header>
              <n-space align="center" :size="8">
                <n-icon size="16">
                  <Icon icon="material-symbols:category-outline" />
                </n-icon>
                <span style="font-size: 14px;">所属分类</span>
              </n-space>
            </template>
            <n-space :size="8">
              <n-tag 
                v-for="catId in currentCase.category_ids" 
                :key="catId"
                type="default"
                size="small"
                :bordered="false"
              >
                <template #icon>
                  <n-icon><Icon icon="mdi:folder-outline" /></n-icon>
                </template>
                {{ getCategoryName(catId) }}
              </n-tag>
            </n-space>
          </n-card>

          <!-- 案例内容 -->
          <n-card title="案例内容" size="small">
            <div class="case-detail-content" v-html="formatContent(currentCase.content)"></div>
          </n-card>

          <!-- 关键知识点 -->
          <n-card title="关键知识点" size="small" v-if="currentCase.key_points?.length">
            <n-space>
              <n-tag v-for="point in currentCase.key_points" :key="point" type="info">
                {{ point }}
              </n-tag>
            </n-space>
          </n-card>

          <!-- 讨论问题 -->
          <n-card title="讨论问题" size="small" v-if="currentCase.discussion_questions?.length">
            <n-ol>
              <n-li v-for="(question, index) in currentCase.discussion_questions" :key="index">
                {{ question }}
              </n-li>
            </n-ol>
          </n-card>

          <!-- 教学建议 -->
          <n-card title="教学建议" size="small" v-if="currentCase.teaching_suggestions">
            <p>{{ currentCase.teaching_suggestions }}</p>
          </n-card>

          <!-- 标签 -->
          <n-card title="标签" size="small" v-if="currentCase.tags?.length">
            <n-space>
              <n-tag v-for="tag in currentCase.tags" :key="tag">
                {{ tag }}
              </n-tag>
            </n-space>
          </n-card>
        </n-space>
      </n-scrollbar>

      <template #footer>
        <n-space justify="space-between">
          <n-space>
            <n-button @click="toggleFavorite(currentCase)">
              <template #icon>
                <n-icon :color="currentCase.is_favorited ? '#f0a020' : undefined">
                  <Icon icon="ant-design:heart-outlined" />
                </n-icon>
              </template>
              {{ currentCase.is_favorited ? '已收藏' : '收藏' }}
            </n-button>
          </n-space>
          <n-space>
            <n-button @click="exportCase(currentCase)">
              <template #icon>
                <n-icon><Icon icon="ant-design:export-outlined" /></n-icon>
              </template>
              导出
            </n-button>
            <n-button @click="detailModalVisible = false">
              关闭
            </n-button>
          </n-space>
        </n-space>
      </template>
    </n-modal>
  </CommonPage>
</template>

<style scoped>
.case-detail-content {
  line-height: 1.8;
  white-space: pre-wrap;
  word-wrap: break-word;
}

/* 案例列表项悬停效果 */
:deep(.n-list-item) {
  transition: all 0.3s ease;
  border-radius: 8px;
  padding: 12px;
}

:deep(.n-list-item:hover) {
  background-color: rgba(102, 126, 234, 0.05);
  transform: translateX(4px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

/* 思政主题卡片样式 */
:deep(.n-card) {
  border-radius: 8px;
}
</style>
