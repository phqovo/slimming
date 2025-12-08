<template>
  <el-dialog
    v-model="dialogVisible"
    title="睡眠记录"
    width="500px"
    :before-close="handleClose"
  >
    <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
      <el-form-item label="睡眠时长" prop="duration">
        <el-input-number
          v-model="form.duration"
          :min="0"
          :max="24"
          :precision="1"
          :step="0.5"
          controls-position="right"
          style="width: 100%"
        />
        <span style="margin-left: 8px">小时</span>
      </el-form-item>

      <el-form-item label="睡眠质量" prop="quality">
        <el-select v-model="form.quality" placeholder="选择睡眠质量" style="width: 100%">
          <el-option label="优秀" value="excellent" />
          <el-option label="良好" value="good" />
          <el-option label="一般" value="fair" />
          <el-option label="较差" value="poor" />
        </el-select>
      </el-form-item>

      <el-form-item label="入睡时间" prop="sleep_time">
        <el-time-picker
          v-model="form.sleep_time"
          placeholder="选择时间"
          style="width: 100%"
          value-format="YYYY-MM-DD HH:mm:ss"
        />
      </el-form-item>

      <el-form-item label="起床时间" prop="wake_time">
        <el-time-picker
          v-model="form.wake_time"
          placeholder="选择时间"
          style="width: 100%"
          value-format="YYYY-MM-DD HH:mm:ss"
        />
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
import { createSleepRecord, updateSleepRecord } from '@/api/health'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const props = defineProps({
  modelValue: Boolean,
  record: Object
})

const emit = defineEmits(['update:modelValue', 'success'])

const dialogVisible = ref(false)
const formRef = ref(null)
const loading = ref(false)

const form = ref({
  duration: 8,
  quality: 'good',
  sleep_time: null,
  wake_time: null,
  record_date: dayjs().format('YYYY-MM-DD')
})

const rules = {
  duration: [{ required: true, message: '请输入睡眠时长', trigger: 'blur' }],
  record_date: [{ required: true, message: '请选择日期', trigger: 'change' }]
}

watch(() => props.modelValue, (val) => {
  dialogVisible.value = val
  if (val) {
    if (props.record) {
      form.value = { ...props.record }
    } else {
      resetForm()
    }
  }
})

watch(dialogVisible, (val) => {
  emit('update:modelValue', val)
})

const resetForm = () => {
  form.value = {
    duration: 8,
    quality: 'good',
    sleep_time: null,
    wake_time: null,
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
    
    if (props.record?.id) {
      await updateSleepRecord(props.record.id, form.value)
      ElMessage.success('更新成功')
    } else {
      await createSleepRecord(form.value)
      ElMessage.success('记录成功')
    }
    
    emit('success')
    handleClose()
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    loading.value = false
  }
}
</script>
