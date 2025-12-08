<template>
  <el-dialog
    v-model="dialogVisible"
    title="饮水记录"
    width="400px"
    :before-close="handleClose"
  >
    <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
      <el-form-item label="饮水量" prop="amount">
        <el-input-number
          v-model="form.amount"
          :min="1"
          :max="5000"
          :step="50"
          controls-position="right"
          style="width: 100%"
        />
        <span style="margin-left: 8px">ml</span>
      </el-form-item>

      <el-form-item label="记录日期" prop="record_date">
        <el-date-picker
          v-model="form.record_date"
          type="date"
          placeholder="选择日期"
          style="width: 100%"
          value-format="YYYY-MM-DD"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="loading">
        确定
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { createWaterRecord } from '@/api/health'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const props = defineProps({
  modelValue: Boolean
})

const emit = defineEmits(['update:modelValue', 'success'])

const dialogVisible = ref(false)
const formRef = ref(null)
const loading = ref(false)

const form = ref({
  amount: 200,
  record_date: dayjs().format('YYYY-MM-DD')
})

const rules = {
  amount: [{ required: true, message: '请输入饮水量', trigger: 'blur' }],
  record_date: [{ required: true, message: '请选择日期', trigger: 'change' }]
}

watch(() => props.modelValue, (val) => {
  dialogVisible.value = val
  if (val) {
    resetForm()
  }
})

watch(dialogVisible, (val) => {
  emit('update:modelValue', val)
})

const resetForm = () => {
  form.value = {
    amount: 200,
    record_date: dayjs().format('YYYY-MM-DD')
  }
  formRef.value?.clearValidate()
}

const handleClose = () => {
  dialogVisible.value = false
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    loading.value = true
    
    await createWaterRecord(form.value)
    
    ElMessage.success('饮水记录成功')
    emit('success')
    handleClose()
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    loading.value = false
  }
}
</script>
