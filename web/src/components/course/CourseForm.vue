<template>
  <NForm
    ref="formRef"
    :model="formData"
    :rules="rules"
    label-placement="left"
    label-align="left"
    :label-width="100"
  >
    <NFormItem label="课程名称" path="name">
      <NInput
        v-model:value="formData.name"
        placeholder="请输入课程名称"
        clearable
        maxlength="100"
        show-count
      />
    </NFormItem>

    <NFormItem label="课程代码" path="code">
      <NInput
        v-model:value="formData.code"
        placeholder="请输入课程代码（如：SE-101）"
        clearable
        maxlength="50"
      />
    </NFormItem>

    <NFormItem label="课程描述" path="description">
      <NInput
        v-model:value="formData.description"
        type="textarea"
        placeholder="请输入课程描述"
        clearable
        :autosize="{ minRows: 3, maxRows: 6 }"
        maxlength="500"
        show-count
      />
    </NFormItem>

    <NFormItem label="学分" path="credit_hours">
      <NInputNumber
        v-model:value="formData.credit_hours"
        placeholder="请输入学分"
        clearable
        :min="0"
        :max="10"
        :precision="1"
        :step="0.5"
        style="width: 100%"
      />
    </NFormItem>

    <NFormItem label="状态" path="is_active">
      <NSwitch
        v-model:value="formData.is_active"
        :checked-value="true"
        :unchecked-value="false"
      >
        <template #checked>启用</template>
        <template #unchecked>禁用</template>
      </NSwitch>
    </NFormItem>
  </NForm>
</template>

<script setup>
import { ref, watch } from 'vue'
import { NForm, NFormItem, NInput, NInputNumber, NSwitch } from 'naive-ui'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({
      name: '',
      code: '',
      description: '',
      credit_hours: null,
      is_active: true,
    }),
  },
})

const emit = defineEmits(['update:modelValue'])

const formRef = ref(null)
const formData = ref({ ...props.modelValue })

// Watch for external changes to modelValue
watch(
  () => props.modelValue,
  (newVal) => {
    formData.value = { ...newVal }
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
      message: '请输入课程名称',
      trigger: ['input', 'blur'],
    },
    {
      max: 100,
      message: '课程名称不能超过100个字符',
      trigger: 'blur',
    },
  ],
  code: [
    {
      required: true,
      message: '请输入课程代码',
      trigger: ['input', 'blur'],
    },
    {
      pattern: /^[A-Z0-9-]+$/,
      message: '课程代码只能包含大写字母、数字和连字符',
      trigger: 'blur',
    },
    {
      max: 50,
      message: '课程代码不能超过50个字符',
      trigger: 'blur',
    },
  ],
  description: [
    {
      max: 500,
      message: '课程描述不能超过500个字符',
      trigger: 'blur',
    },
  ],
  credit_hours: [
    {
      type: 'number',
      message: '学分必须是数字',
      trigger: 'blur',
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
