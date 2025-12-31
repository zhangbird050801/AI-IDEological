<template>
  <div class="draggable-menu-tree">
    <n-tree
      ref="treeRef"
      block-line
      :data="treeData"
      :node-props="nodeProps"
      :render-prefix="renderPrefix"
      :render-suffix="renderSuffix"
      default-expand-all
      draggable
      @drop="handleDrop"
    />
  </div>
</template>

<script setup>
import { ref, h, computed } from 'vue'
import { NTree, NButton, NSpace, NTag, NSwitch, NPopconfirm, useMessage } from 'naive-ui'
import { Icon } from '@iconify/vue'
import TheIcon from '@/components/icon/TheIcon.vue'

const props = defineProps({
  data: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['edit', 'delete', 'add-child', 'update-order'])

const message = useMessage()
const treeRef = ref(null)

// 转换数据为树形结构
const treeData = computed(() => {
  return convertToTreeData(props.data)
})

function convertToTreeData(data) {
  return data.map(item => ({
    key: item.id,
    label: item.name,
    ...item,
    children: item.children ? convertToTreeData(item.children) : undefined,
  }))
}

// 节点前缀（图标和类型标签）
const renderPrefix = ({ option }) => {
  return h(NSpace, { size: 8, align: 'center' }, () => [
    h(TheIcon, { icon: option.icon || 'material-symbols:menu', size: 18 }),
    h(
      NTag,
      {
        size: 'small',
        type: option.menu_type === 'catalog' ? 'info' : 'success',
        bordered: false,
      },
      { default: () => (option.menu_type === 'catalog' ? '目录' : '菜单') }
    ),
  ])
}

// 节点后缀（操作按钮）
const renderSuffix = ({ option }) => {
  return h(
    NSpace,
    { size: 4, style: 'margin-left: 12px' },
    () => [
      // 排序号
      h(
        NTag,
        { size: 'tiny', bordered: false },
        { default: () => `#${option.order}` }
      ),
      // 添加子菜单
      option.menu_type !== 'menu' &&
        h(
          NButton,
          {
            size: 'tiny',
            tertiary: true,
            type: 'primary',
            onClick: () => emit('add-child', option),
          },
          {
            default: () => '添加',
            icon: () => h(Icon, { icon: 'material-symbols:add' }),
          }
        ),
      // 编辑
      h(
        NButton,
        {
          size: 'tiny',
          tertiary: true,
          type: 'info',
          onClick: () => emit('edit', option),
        },
        {
          default: () => '编辑',
          icon: () => h(Icon, { icon: 'material-symbols:edit-outline' }),
        }
      ),
      // 删除
      h(
        NPopconfirm,
        {
          onPositiveClick: () => emit('delete', option.id),
        },
        {
          trigger: () =>
            h(
              NButton,
              {
                size: 'tiny',
                tertiary: true,
                type: 'error',
                disabled: option.children && option.children.length > 0,
              },
              {
                default: () => '删除',
                icon: () => h(Icon, { icon: 'material-symbols:delete-outline' }),
              }
            ),
          default: () => '确定删除该菜单吗？',
        }
      ),
    ]
  )
}

// 节点属性
const nodeProps = ({ option }) => {
  return {
    style: {
      padding: '8px 0',
    },
  }
}

// 拖拽结束处理
async function handleDrop({ node, dragNode, dropPosition }) {
  console.log('拖拽信息:', { node, dragNode, dropPosition })
  
  const draggedMenu = dragNode
  const targetMenu = node
  
  // 验证拖拽规则：菜单不能拖到其他菜单下
  if (dropPosition === 'inside') {
    // 拖入目标节点内部
    if (draggedMenu.menu_type === 'menu' && targetMenu.menu_type === 'menu') {
      message.error('菜单不能拖入其他菜单下，只能拖到目录下')
      return
    }
    if (targetMenu.menu_type === 'menu') {
      message.error('不能将节点拖入菜单类型节点')
      return
    }
  }
  
  // 计算新的parent_id和order
  let newParentId = 0
  let newOrder = draggedMenu.order
  
  if (dropPosition === 'inside') {
    // 拖入目标节点内部（已通过验证）
    newParentId = targetMenu.id
    newOrder = (targetMenu.children?.length || 0) + 1
  } else if (dropPosition === 'before' || dropPosition === 'after') {
    // 拖到目标节点前后
    newParentId = targetMenu.parent_id
    newOrder = dropPosition === 'before' ? targetMenu.order : targetMenu.order + 1
  }
  
  // 触发更新排序事件
  emit('update-order', {
    menu_id: draggedMenu.id,
    new_parent_id: newParentId,
    new_order: newOrder,
  })
  
  message.info('正在更新菜单顺序...')
}
</script>

<style scoped>
.draggable-menu-tree {
  width: 100%;
}

:deep(.n-tree-node-content) {
  padding: 4px 8px;
}

:deep(.n-tree-node--pending) {
  opacity: 0.6;
}

:deep(.n-tree-node--disabled) {
  cursor: not-allowed;
  opacity: 0.5;
}
</style>
