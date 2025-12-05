<template>
  <div class="theme-category-tree">
    <n-tree
      :data="treeData"
      :render-label="renderLabel"
      :node-props="getNodeProps"
      block-line
      draggable
      :on-drop="handleDrop"
      :default-expanded-keys="defaultExpandedKeys"
    />
  </div>
</template>

<script setup>
import { h, computed } from 'vue'
import { NTree, NSpace, NButton, NIcon, NText } from 'naive-ui'
import { Icon } from '@iconify/vue'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  expandAll: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['edit', 'delete', 'add-child', 'move'])

// 转换数据格式
const treeData = computed(() => {
  return convertToTreeData(props.data)
})

// 默认展开的节点
const defaultExpandedKeys = computed(() => {
  if (!props.expandAll) return []
  const keys = []
  const collectKeys = (items) => {
    items.forEach(item => {
      if (item.children && item.children.length > 0) {
        keys.push(item.key)
        collectKeys(item.children)
      }
    })
  }
  collectKeys(treeData.value)
  return keys
})

// 转换数据为树组件需要的格式
function convertToTreeData(data) {
  return data.map(item => ({
    key: item.id,
    label: item.name,
    isActive: item.is_active,
    description: item.description,
    children: item.children ? convertToTreeData(item.children) : []
  }))
}

// 自定义节点渲染
function renderLabel({ option }) {
  return h(
    NSpace,
    { align: 'center', justify: 'space-between', style: { width: '100%' } },
    {
      default: () => [
        h(
          NSpace,
          { align: 'center', size: 8 },
          {
            default: () => [
              h(NText, { type: option.isActive ? 'default' : 'error' }, 
                { default: () => option.label }
              ),
              !option.isActive && h(NText, { type: 'error', depth: 3, style: { fontSize: '12px' } }, 
                { default: () => '(已禁用)' }
              )
            ]
          }
        ),
        h(
          NSpace,
          { size: 4 },
          {
            default: () => [
              h(
                NButton,
                {
                  size: 'tiny',
                  text: true,
                  onClick: (e) => {
                    e.stopPropagation()
                    emit('add-child', option.key)
                  }
                },
                {
                  default: () => h(NIcon, null, { default: () => h(Icon, { icon: 'ant-design:plus-outlined' }) })
                }
              ),
              h(
                NButton,
                {
                  size: 'tiny',
                  text: true,
                  onClick: (e) => {
                    e.stopPropagation()
                    emit('edit', option.key)
                  }
                },
                {
                  default: () => h(NIcon, null, { default: () => h(Icon, { icon: 'ant-design:edit-outlined' }) })
                }
              ),
              h(
                NButton,
                {
                  size: 'tiny',
                  text: true,
                  type: 'error',
                  onClick: (e) => {
                    e.stopPropagation()
                    emit('delete', option.key)
                  }
                },
                {
                  default: () => h(NIcon, null, { default: () => h(Icon, { icon: 'ant-design:delete-outlined' }) })
                }
              )
            ]
          }
        )
      ]
    }
  )
}

// 节点属性
function getNodeProps({ option }) {
  return {
    style: {
      padding: '8px 12px',
      borderRadius: '4px'
    }
  }
}

// 处理拖拽
function handleDrop({ node, dragNode, dropPosition }) {
  const dragId = dragNode.key
  const dropId = node.key
  
  let parent_id = null
  let order = 0
  
  if (dropPosition === 'inside') {
    parent_id = dropId
  } else {
    // 获取同级节点
    const parentNode = findParentNode(treeData.value, dropId)
    parent_id = parentNode ? parentNode.key : null
    
    // 计算order
    const siblings = parentNode ? parentNode.children : treeData.value
    const dropIndex = siblings.findIndex(item => item.key === dropId)
    order = dropPosition === 'before' ? dropIndex : dropIndex + 1
  }
  
  emit('move', {
    id: dragId,
    parent_id: parent_id,
    order: order
  })
}

// 查找父节点
function findParentNode(nodes, targetKey, parent = null) {
  for (const node of nodes) {
    if (node.key === targetKey) {
      return parent
    }
    if (node.children && node.children.length > 0) {
      const result = findParentNode(node.children, targetKey, node)
      if (result !== null) {
        return result
      }
    }
  }
  return null
}
</script>

<style scoped>
.theme-category-tree {
  width: 100%;
  min-height: 200px;
  max-height: calc(100vh - 300px);
  overflow-y: auto;
}
</style>
