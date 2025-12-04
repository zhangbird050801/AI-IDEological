<template>
  <div class="category-tree">
    <NTree
      :data="treeData"
      :expanded-keys="expandedKeys"
      :checked-keys="checkedKeys"
      :checkable="checkable"
      :selectable="selectable"
      :draggable="draggable"
      :render-label="renderLabel"
      :render-suffix="renderSuffix"
      block-line
      @update:expanded-keys="handleExpandedKeysChange"
      @update:checked-keys="handleCheckedKeysChange"
      @drop="handleDrop"
    />
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { NTree } from 'naive-ui'

const props = defineProps({
  data: {
    type: Array,
    default: () => [],
  },
  checkable: {
    type: Boolean,
    default: false,
  },
  selectable: {
    type: Boolean,
    default: true,
  },
  draggable: {
    type: Boolean,
    default: false,
  },
  expandedKeys: {
    type: Array,
    default: () => [],
  },
  checkedKeys: {
    type: Array,
    default: () => [],
  },
  renderLabel: {
    type: Function,
    default: null,
  },
  renderSuffix: {
    type: Function,
    default: null,
  },
})

const emit = defineEmits([
  'update:expandedKeys',
  'update:checkedKeys',
  'drop',
])

const treeData = computed(() => props.data)
const expandedKeys = ref([...props.expandedKeys])
const checkedKeys = ref([...props.checkedKeys])

// Watch for external changes
watch(
  () => props.expandedKeys,
  (newVal) => {
    expandedKeys.value = [...newVal]
  }
)

watch(
  () => props.checkedKeys,
  (newVal) => {
    checkedKeys.value = [...newVal]
  }
)

// Handle expanded keys change
function handleExpandedKeysChange(keys) {
  expandedKeys.value = keys
  emit('update:expandedKeys', keys)
}

// Handle checked keys change
function handleCheckedKeysChange(keys) {
  checkedKeys.value = keys
  emit('update:checkedKeys', keys)
}

// Handle drop
function handleDrop(data) {
  emit('drop', data)
}
</script>

<style scoped>
.category-tree {
  width: 100%;
}
</style>
