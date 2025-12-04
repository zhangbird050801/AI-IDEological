<template>
  <NForm
    ref="formRef"
    :model="formData"
    :rules="rules"
    label-placement="left"
    label-align="left"
    :label-width="100"
  >
    <NFormItem label="知识点名称" path="name">
      <NInput
        v-model:value="formData.name"
        placeholder="请输入知识点名称"
        clearable
        maxlength="200"
        show-count
      />
    </NFormItem>

    <NFormItem label="描述" path="description">
      <NInput
        v-model:value="formData.description"
        type="textarea"
        placeholder="请输入知识点描述"
        clearable
        :autosize="{ minRows: 3, maxRows: 6 }"
        maxlength="1000"
        show-count
      />
    </NFormItem>

    <NFormItem label="关键词" path="keywords">
      <NDynamicTags
        v-model:value="formData.keywords"
        :max="20"
      >
        <template #input="{ submit, deactivate }">
          <NInput
            ref="keywordInputRef"
            size="small"
            placeholder="输入关键词后按回车"
            @keyup.enter="submit"
            @blur="deactivate"
          />
        </template>
        <template #trigger="{ activate, disabled }">
          <NButton
            size="small"
            type="primary"
            dashed
            :disabled="disabled"
            @click="activate"
          >
            <template #icon>
              <TheIcon icon="material-symbols:add" />
            </template>
            添加关键词
          </NButton>
        </template>
      </NDynamicTags>
      <div style="margin-top: 8px; color: #999; font-size: 12px;">
        添加与该知识点相关的关键词标签，最多20个
      </div>
    </NFormItem>
  </NForm>
</template>

<script setup>
import { ref, watch } from 'vue'
import { NForm, NFormItem, NInput, NDynamicTags, NButton } from 'naive-ui'
import TheIcon from '@/components/icon/TheIcon.vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({
      chapter_id: null,
      name: '',
      description: '',
      keywords: [],
    }),
  },
})

const emit = defineEmits(['update:modelValue'])

const formRef = ref(null)
const keywordInputRef = ref(null)
const formData = ref({ ...props.modelValue })

// Ensure keywords is always an array
if (!Array.isArray(formData.value.keywords)) {
  formData.value.keywords = []
}

// Watch for external changes to modelValue
watch(
  () => props.modelValue,
  (newVal) => {
    formData.value = { 
      ...newVal,
      keywords: Array.isArray(newVal.keywords) ? newVal.keywords : []
    }
  },
  { deep: true }
)

// Watch for internal changes and emit
watch(
  formData,
  (newVal) => {
    emit('update:modelValue', newVal)
  },
  { deep: true }
)

// Validation rules
const rules = {
  name: [
    {
      required: true,
      message: '请输入知识点名称',
      trigger: ['input', 'blur'],
    },
    {
      max: 200,
      message: '知识点名称不能超过200个字符',
      trigger: 'blur',
    },
  ],
  description: [
    {
      max: 1000,
      message: '描述不能超过1000个字符',
      trigger: 'blur',
    },
  ],
  keywords: [
    {
      type: 'array',
      max: 20,
      message: '关键词最多20个',
      trigger: 'change',
    },
  ],
}

// Expose validation method
const validate = () => {
  return formRef.value?.validate()
}

const restoreValidation = () => {
  formRef.value?.restoreValidation()
}

defineExpose({
  validate,
  restoreValidation,
  formRef,
})
</script>
