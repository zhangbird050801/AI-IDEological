<template>
  <n-modal
    v-model:show="visible"
    preset="card"
    title="菜单回收站"
    style="width: 1000px"
    :bordered="false"
    :segmented="{ content: 'soft' }"
  >
    <template #header-extra>
      <n-space>
        <n-button
          type="error"
          size="small"
          :disabled="recycleBinData.length === 0"
          @click="handleEmptyRecycleBin"
        >
          <template #icon>
            <n-icon><Icon icon="material-symbols:delete-forever" /></n-icon>
          </template>
          清空回收站
        </n-button>
        <n-button size="small" @click="refreshRecycleBin">
          <template #icon>
            <n-icon><Icon icon="material-symbols:refresh" /></n-icon>
          </template>
          刷新
        </n-button>
      </n-space>
    </template>

    <n-spin :show="loading">
      <n-data-table
        :columns="columns"
        :data="recycleBinData"
        :pagination="pagination"
        :bordered="false"
        :single-line="false"
      />
      
      <n-empty
        v-if="!loading && recycleBinData.length === 0"
        description="回收站为空"
        style="margin-top: 40px"
      />
    </n-spin>
  </n-modal>
</template>

<script setup>
import { ref, h } from 'vue'
import { NButton, NSpace, NTag, NPopconfirm, NIcon, useMessage, useDialog } from 'naive-ui'
import { Icon } from '@iconify/vue'
import TheIcon from '@/components/icon/TheIcon.vue'
import { formatDate } from '@/utils'
import api from '@/api'

const props = defineProps({
  show: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:show', 'refresh'])

const message = useMessage()
const dialog = useDialog()

const visible = ref(props.show)
const loading = ref(false)
const recycleBinData = ref([])

const pagination = {
  pageSize: 10,
}

const columns = [
  { title: 'ID', key: 'id', width: 60, align: 'center' },
  { title: '菜单名称', key: 'name', width: 120, ellipsis: { tooltip: true } },
  {
    title: '菜单类型',
    key: 'menu_type',
    width: 100,
    align: 'center',
    render(row) {
      return h(
        NTag,
        { 
          type: row.menu_type === 'catalog' ? 'info' : 'success',
          size: 'small'
        },
        { default: () => (row.menu_type === 'catalog' ? '目录' : '菜单') }
      )
    },
  },
  {
    title: '图标',
    key: 'icon',
    width: 60,
    align: 'center',
    render(row) {
      return h(TheIcon, { icon: row.icon, size: 20 })
    },
  },
  { title: '路径', key: 'path', width: 150, ellipsis: { tooltip: true } },
  {
    title: '删除时间',
    key: 'deleted_at',
    width: 160,
    align: 'center',
    render(row) {
      return h('span', formatDate(row.deleted_at))
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 160,
    align: 'center',
    fixed: 'right',
    render(row) {
      return h(NSpace, { justify: 'center' }, () => [
        h(
          NButton,
          {
            size: 'small',
            type: 'success',
            secondary: true,
            onClick: () => handleRestore(row.id),
          },
          {
            default: () => '恢复',
            icon: () => h(Icon, { icon: 'material-symbols:restore' }),
          }
        ),
        h(
          NPopconfirm,
          {
            onPositiveClick: () => handlePermanentDelete(row.id),
          },
          {
            trigger: () =>
              h(
                NButton,
                {
                  size: 'small',
                  type: 'error',
                  secondary: true,
                },
                {
                  default: () => '永久删除',
                  icon: () => h(Icon, { icon: 'material-symbols:delete-forever' }),
                }
              ),
            default: () => h('div', {}, '确定永久删除该菜单吗？此操作不可恢复！'),
          }
        ),
      ])
    },
  },
]

// 监听props变化
watch(
  () => props.show,
  (val) => {
    visible.value = val
    if (val) {
      fetchRecycleBin()
    }
  }
)

// 监听visible变化
watch(visible, (val) => {
  emit('update:show', val)
})

// 获取回收站列表
async function fetchRecycleBin() {
  try {
    loading.value = true
    const { data } = await api.getRecycleBin()
    recycleBinData.value = data || []
  } catch (error) {
    console.error('获取回收站列表失败:', error)
    message.error('获取回收站列表失败')
  } finally {
    loading.value = false
  }
}

// 刷新回收站
function refreshRecycleBin() {
  fetchRecycleBin()
}

// 恢复菜单
async function handleRestore(id) {
  try {
    await api.restoreMenu({ id })
    message.success('菜单已恢复')
    fetchRecycleBin()
    emit('refresh')
  } catch (error) {
    console.error('恢复菜单失败:', error)
    message.error(error.response?.data?.msg || '恢复菜单失败')
  }
}

// 永久删除菜单
async function handlePermanentDelete(id) {
  try {
    await api.permanentDeleteMenu({ id })
    message.success('菜单已永久删除')
    fetchRecycleBin()
    emit('refresh')
  } catch (error) {
    console.error('永久删除失败:', error)
    message.error(error.response?.data?.msg || '永久删除失败')
  }
}

// 清空回收站
function handleEmptyRecycleBin() {
  dialog.warning({
    title: '清空回收站',
    content: `确定要清空回收站吗？这将永久删除 ${recycleBinData.value.length} 个菜单，此操作不可恢复！`,
    positiveText: '确定清空',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await api.emptyRecycleBin()
        message.success('回收站已清空')
        fetchRecycleBin()
        emit('refresh')
      } catch (error) {
        console.error('清空回收站失败:', error)
        message.error('清空回收站失败')
      }
    },
  })
}
</script>

<style scoped>
:deep(.n-data-table-th) {
  text-align: center;
}
</style>
