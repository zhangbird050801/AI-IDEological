<script setup>
import { h, onMounted, ref, watch } from 'vue'
import {
  NButton,
  NForm,
  NFormItem,
  NInput,
  NInputNumber,
  NSwitch,
  NTreeSelect,
  NRadio,
  NRadioGroup,
  NSpace,
  NBadge,
  NCard,
  NTabs,
  NTabPane,
  useMessage,
  useDialog,
} from 'naive-ui'

import CommonPage from '@/components/page/CommonPage.vue'
import CrudModal from '@/components/table/CrudModal.vue'
import IconPicker from '@/components/icon/IconPicker.vue'
import TheIcon from '@/components/icon/TheIcon.vue'
import DraggableMenuTree from './components/DraggableMenuTree.vue'
import RecycleBin from './RecycleBin.vue'

import { useCRUD } from '@/composables'
import api from '@/api'

defineOptions({ name: '菜单管理' })

const message = useMessage()
const dialog = useDialog()

// 回收站相关
const showRecycleBin = ref(false)
const recycleBinCount = ref(0)

// 菜单数据
const menuData = ref([])
const loading = ref(false)

// 表单初始化内容
const initForm = {
  order: 1,
  keepalive: true,
  is_hidden: false,
}

const {
  modalVisible,
  modalTitle,
  modalLoading,
  handleAdd,
  handleEdit,
  handleSave,
  modalForm,
  modalFormRef,
} = useCRUD({
  name: '菜单',
  initForm,
  doCreate: api.createMenu,
  doUpdate: api.updateMenu,
  refresh: () => fetchMenuData(),
})

onMounted(() => {
  fetchMenuData()
  getTreeSelect()
  fetchRecycleBinCount()
})

const showMenuType = ref(false)
const menuOptions = ref([])

// 获取菜单数据
async function fetchMenuData() {
  try {
    loading.value = true
    const { data } = await api.getMenus()
    menuData.value = data || []
  } catch (error) {
    console.error('获取菜单失败:', error)
    message.error('获取菜单失败')
  } finally {
    loading.value = false
  }
}

// 获取树形选择器选项
async function getTreeSelect() {
  const { data } = await api.getMenus()
  const menu = { id: 0, name: '根目录', children: [] }
  menu.children = data
  menuOptions.value = [menu]
}

// 新增根菜单
function handleClickAdd() {
  modalForm.value = {
    ...initForm,
    parent_id: 0,
    menu_type: 'catalog',
  }
  showMenuType.value = true
  modalVisible.value = true
}

// 添加子菜单
function handleAddChild(parent) {
  modalForm.value = {
    ...initForm,
    parent_id: parent.id,
    menu_type: 'menu',
  }
  showMenuType.value = false
  modalVisible.value = true
}

// 编辑菜单
function handleEditMenu(menu) {
  showMenuType.value = false
  handleEdit(menu)
}

// 软删除（移至回收站）
async function handleSoftDelete(id) {
  try {
    await api.softDeleteMenu({ id })
    message.success('菜单已移至回收站')
    fetchMenuData()
    fetchRecycleBinCount()
  } catch (error) {
    console.error('删除失败:', error)
    message.error(error.response?.data?.msg || '删除失败')
  }
}


// 更新排序
async function handleUpdateOrder({ menu_id, new_parent_id, new_order }) {
  try {
    await api.updateMenuOrder({
      menu_id,
      new_order,
      new_parent_id,
    })
    message.success('排序已更新')
    fetchMenuData()
  } catch (error) {
    console.error('更新排序失败:', error)
    message.error('更新排序失败')
  }
}

// 获取回收站数量
async function fetchRecycleBinCount() {
  try {
    const { data } = await api.getRecycleBin()
    recycleBinCount.value = data?.length || 0
  } catch (error) {
    console.error('获取回收站数量失败:', error)
  }
}

// 打开回收站
function openRecycleBin() {
  showRecycleBin.value = true
}

// 回收站操作后刷新
function handleRecycleBinRefresh() {
  fetchMenuData()
  fetchRecycleBinCount()
}

// 保存后刷新
async function handleSaveMenu() {
  await handleSave()
  await getTreeSelect()
}
</script>

<template>
  <CommonPage show-footer title="菜单管理">
    <template #action>
      <NSpace>
        <NButton type="primary" @click="handleClickAdd">
          <template #icon>
            <TheIcon icon="material-symbols:add" :size="18" />
          </template>
          新建根菜单
        </NButton>

        <NBadge :value="recycleBinCount" :max="99" show-zero>
          <NButton @click="openRecycleBin">
            <template #icon>
              <TheIcon icon="material-symbols:delete-outline" :size="18" />
            </template>
            回收站
          </NButton>
        </NBadge>

        <NButton @click="fetchMenuData">
          <template #icon>
            <TheIcon icon="material-symbols:refresh" :size="18" />
          </template>
          刷新
        </NButton>
      </NSpace>
    </template>

    <!-- 菜单树 -->
    <NCard title="菜单树形结构" :bordered="false">
      <template #header-extra>
        <span style="color: #999; font-size: 12px">
          提示：支持拖拽调整菜单顺序和层级关系
        </span>
      </template>

      <n-spin :show="loading">
        <DraggableMenuTree
          v-if="menuData.length > 0"
          :data="menuData"
          @edit="handleEditMenu"
          @delete="handleSoftDelete"
          @add-child="handleAddChild"
          @update-order="handleUpdateOrder"
        />
        <n-empty
          v-else
          description="暂无菜单数据，点击上方按钮添加根菜单"
          style="margin: 40px 0"
        />
      </n-spin>
    </NCard>

    <!-- 新增/编辑弹窗 -->
    <CrudModal
      v-model:visible="modalVisible"
      :title="modalTitle"
      :loading="modalLoading"
      @save="handleSaveMenu"
    >
      <NForm
        ref="modalFormRef"
        label-placement="left"
        label-align="left"
        :label-width="90"
        :model="modalForm"
      >
        <NFormItem label="菜单类型" path="menu_type">
          <NRadioGroup v-model:value="modalForm.menu_type">
            <NRadio label="目录" value="catalog" />
            <NRadio label="菜单" value="menu" />
          </NRadioGroup>
        </NFormItem>

        <NFormItem label="上级菜单" path="parent_id">
          <NTreeSelect
            v-model:value="modalForm.parent_id"
            key-field="id"
            label-field="name"
            :options="menuOptions"
            default-expand-all
          />
        </NFormItem>

        <NFormItem
          label="菜单名称"
          path="name"
          :rule="{
            required: true,
            message: '请输入菜单名称',
            trigger: ['input', 'blur'],
          }"
        >
          <NInput v-model:value="modalForm.name" placeholder="请输入菜单名称" />
        </NFormItem>

        <NFormItem
          label="访问路径"
          path="path"
          :rule="{
            required: true,
            message: '请输入访问路径',
            trigger: ['blur'],
          }"
        >
          <NInput v-model:value="modalForm.path" placeholder="例如：/system/user" />
        </NFormItem>

        <NFormItem v-if="modalForm.menu_type === 'menu'" label="组件路径" path="component">
          <NInput
            v-model:value="modalForm.component"
            placeholder="请输入组件路径，例如：/system/user"
          />
        </NFormItem>

        <NFormItem label="跳转路径" path="redirect">
          <NInput
            v-model:value="modalForm.redirect"
            :disabled="modalForm.parent_id !== 0"
            :placeholder="
              modalForm.parent_id !== 0 ? '只有一级菜单可以设置跳转路径' : '请输入跳转路径'
            "
          />
        </NFormItem>

        <NFormItem label="菜单图标" path="icon">
          <IconPicker v-model:value="modalForm.icon" />
        </NFormItem>

        <NFormItem label="显示排序" path="order">
          <NInputNumber v-model:value="modalForm.order" :min="1" style="width: 100%" />
        </NFormItem>

        <NFormItem label="是否隐藏" path="is_hidden">
          <NSwitch v-model:value="modalForm.is_hidden">
            <template #checked>隐藏</template>
            <template #unchecked>显示</template>
          </NSwitch>
        </NFormItem>

        <NFormItem label="KeepAlive" path="keepalive">
          <NSwitch v-model:value="modalForm.keepalive">
            <template #checked>开启</template>
            <template #unchecked>关闭</template>
          </NSwitch>
        </NFormItem>
      </NForm>
    </CrudModal>

    <!-- 回收站弹窗 -->
    <RecycleBin v-model:show="showRecycleBin" @refresh="handleRecycleBinRefresh" />
  </CommonPage>
</template>

<style scoped>
:deep(.n-card-header) {
  padding: 16px 20px;
}

:deep(.n-card__content) {
  padding: 20px;
}
</style>
