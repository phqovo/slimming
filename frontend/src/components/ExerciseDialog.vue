<template>
  <el-dialog
    v-model="dialogVisible"
    title="运动打卡"
    width="600px"
    :before-close="handleClose"
  >
    <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
      <el-form-item label="运动类型" prop="exercise_type">
        <el-select v-model="form.exercise_type" placeholder="选择运动类型" style="width: 100%">
          <el-option label="跑步" value="跑步" />
          <el-option label="游泳" value="游泳" />
          <el-option label="骑行" value="骑行" />
          <el-option label="健身" value="健身" />
          <el-option label="瑜伽" value="瑜伽" />
          <el-option label="球类运动" value="球类运动" />
          <el-option label="跳操" value="跳操" />
          <el-option label="爬山" value="爬山" />
          <el-option label="力量训练" value="力量训练" />
          <el-option label="突击减脂" value="突击减脂" />
          <el-option label="高强度间歇训练" value="高强度间歇训练" />
          <el-option label="户外徒步" value="户外徒步" />
          <el-option label="其他" value="其他" />
        </el-select>
      </el-form-item>

      <el-form-item label="时长" prop="duration">
        <div style="display: flex; align-items: center; width: 100%;">
          <el-input-number
            v-model="form.duration"
            :min="1"
            :max="600"
            controls-position="right"
            style="flex: 1;"
          />
          <span style="margin-left: 8px; white-space: nowrap;">分钟</span>
        </div>
      </el-form-item>

      <el-form-item label="消耗卡路里" prop="calories">
        <div style="display: flex; align-items: center; width: 100%;">
          <el-input-number
            v-model="form.calories"
            :min="0"
            :precision="0"
            controls-position="right"
            style="flex: 1;"
          />
          <span style="margin-left: 8px; white-space: nowrap;">kcal</span>
        </div>
      </el-form-item>

      <el-form-item label="距离" prop="distance">
        <div style="display: flex; align-items: center; width: 100%;">
          <el-input-number
            v-model="form.distance"
            :min="0"
            :precision="2"
            :step="0.1"
            controls-position="right"
            style="flex: 1;"
          />
          <span style="margin-left: 8px; white-space: nowrap;">km</span>
        </div>
      </el-form-item>

      <el-form-item label="运动照片" prop="image_url">
        <el-upload
          :auto-upload="true"
          :show-file-list="false"
          :on-success="handleUploadSuccess"
          :before-upload="beforeUpload"
          action="/health/api/v1/exercise/upload-image"
          :headers="{ Authorization: `Bearer ${token}` }"
        >
          <el-button size="small" type="primary">点击上传</el-button>
        </el-upload>
        <el-image
          v-if="form.image_url"
          :src="form.image_url"
          fit="cover"
          style="width: 100px; height: 100px; margin-top: 10px; border-radius: 8px;"
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

      <el-form-item label="备注" prop="note">
        <el-input
          v-model="form.note"
          type="textarea"
          :rows="3"
          placeholder="记录运动感受..."
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
import { ref, watch, computed } from 'vue'
import { createExerciseRecord } from '@/api/health'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const props = defineProps({
  modelValue: Boolean
})

const emit = defineEmits(['update:modelValue', 'success'])

const dialogVisible = ref(false)
const formRef = ref(null)
const loading = ref(false)

const token = computed(() => localStorage.getItem('token'))

const form = ref({
  exercise_type: '',
  duration: 30,
  calories: 0,
  distance: 0,
  image_url: '',
  record_date: dayjs().format('YYYY-MM-DD'),
  note: ''
})

const rules = {
  exercise_type: [{ required: true, message: '请选择运动类型', trigger: 'change' }],
  duration: [{ required: true, message: '请输入运动时长', trigger: 'blur' }],
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
    exercise_type: '',
    duration: 30,
    calories: 0,
    distance: 0,
    image_url: '',
    record_date: dayjs().format('YYYY-MM-DD'),
    note: ''
  }
  formRef.value?.clearValidate()
}

const beforeUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt5M = file.size / 1024 / 1024 < 5

  if (!isImage) {
    ElMessage.error('只能上传图片文件')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB')
    return false
  }
  return true
}

const handleUploadSuccess = (response) => {
  if (response.code === 200) {
    form.value.image_url = response.data.image_url
    ElMessage.success('图片上传成功')
  }
}

const handleClose = () => {
  dialogVisible.value = false
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    loading.value = true
    
    await createExerciseRecord(form.value)
    
    ElMessage.success('运动记录成功')
    emit('success')
    handleClose()
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    loading.value = false
  }
}
</script>
