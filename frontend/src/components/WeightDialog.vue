<template>
  <el-dialog
    v-model="dialogVisible"
    title="记录体重"
    width="500px"
    :before-close="handleClose"
  >
    <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
      <el-form-item label="早晨体重" prop="morning_weight">
        <div style="display: flex; align-items: center; width: 100%;">
          <el-input-number
            v-model="form.morning_weight"
            :min="30"
            :max="settingsStore.weightUnit === 'jin' ? 600 : 300"
            :precision="1"
            :step="0.1"
            controls-position="right"
            style="flex: 1;"
            @change="handleMorningWeightChange"
          />
          <span style="margin-left: 8px; white-space: nowrap;">{{ settingsStore.getWeightUnitText() }}</span>
        </div>
      </el-form-item>

      <el-form-item label="睡前体重" prop="evening_weight">
        <div style="display: flex; align-items: center; width: 100%;">
          <el-input-number
            v-model="form.evening_weight"
            :min="30"
            :max="settingsStore.weightUnit === 'jin' ? 600 : 300"
            :precision="1"
            :step="0.1"
            controls-position="right"
            style="flex: 1;"
          />
          <span style="margin-left: 8px; white-space: nowrap;">{{ settingsStore.getWeightUnitText() }}</span>
        </div>
      </el-form-item>

      <el-form-item label="体重" prop="weight">
        <div style="display: flex; align-items: center; width: 100%;">
          <el-input-number
            v-model="form.weight"
            :min="30"
            :max="settingsStore.weightUnit === 'jin' ? 600 : 300"
            :precision="1"
            :step="0.1"
            controls-position="right"
            style="flex: 1;"
          />
          <span style="margin-left: 8px; white-space: nowrap;">{{ settingsStore.getWeightUnitText() }}</span>
        </div>
      </el-form-item>

      <el-form-item label="体脂率" prop="body_fat">
        <div style="display: flex; align-items: center; width: 100%;">
          <el-input-number
            v-model="form.body_fat"
            :min="0"
            :max="100"
            :precision="1"
            :step="0.1"
            controls-position="right"
            style="flex: 1;"
          />
          <span style="margin-left: 8px; white-space: nowrap;">%</span>
        </div>
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
          placeholder="记录今天的感受..."
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
import { useSettingsStore } from '@/stores/settings'
import { createWeightRecord, getWeightRecords } from '@/api/weight'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const props = defineProps({
  modelValue: Boolean
})

const emit = defineEmits(['update:modelValue', 'success'])

const settingsStore = useSettingsStore()
const dialogVisible = ref(false)
const formRef = ref(null)
const loading = ref(false)

const form = ref({
  weight: null,
  morning_weight: null,
  evening_weight: null,
  body_fat: null,
  record_date: dayjs().format('YYYY-MM-DD'),
  note: ''
})

const rules = {
  record_date: [{ required: true, message: '请选择日期', trigger: 'change' }]
}

watch(() => props.modelValue, async (val) => {
  dialogVisible.value = val
  if (val) {
    await loadTodayData()
  }
})

watch(dialogVisible, (val) => {
  emit('update:modelValue', val)
})

const resetForm = () => {
  form.value = {
    weight: null,
    morning_weight: null,
    evening_weight: null,
    body_fat: null,
    record_date: dayjs().format('YYYY-MM-DD'),
    note: ''
  }
  formRef.value?.clearValidate()
}

// 加载今日数据
const loadTodayData = async () => {
  try {
    const today = dayjs().format('YYYY-MM-DD')
    const data = await getWeightRecords({ record_date: today, limit: 1 })
    
    console.log('今日体重数据:', data)
    
    if (data && data.length > 0) {
      // 有今日数据，回显
      const todayRecord = data[0]
      form.value = {
        weight: todayRecord.weight ? settingsStore.convertWeightToDisplay(todayRecord.weight) : null,
        morning_weight: todayRecord.morning_weight ? settingsStore.convertWeightToDisplay(todayRecord.morning_weight) : null,
        evening_weight: todayRecord.evening_weight ? settingsStore.convertWeightToDisplay(todayRecord.evening_weight) : null,
        body_fat: todayRecord.body_fat,
        record_date: todayRecord.record_date,
        note: todayRecord.note || ''
      }
      console.log('回显表单数据:', form.value)
    } else {
      // 无今日数据，重置表单
      console.log('无今日数据，重置表单')
      resetForm()
    }
    
    formRef.value?.clearValidate()
  } catch (error) {
    console.error('加载今日数据失败:', error)
    resetForm()
  }
}

const handleClose = () => {
  dialogVisible.value = false
}

const handleMorningWeightChange = () => {
  // 早晨体重改变时，如果体重为null，自动填充为早晨体重
  if (form.value.morning_weight && !form.value.weight) {
    form.value.weight = form.value.morning_weight
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    
    // 检查是否至少填写了一项体重数据
    if (!form.value.weight && !form.value.morning_weight && !form.value.evening_weight) {
      ElMessage.error('请至少填写一项体重数据（当前体重、早晨体重或睡前体重）')
      return
    }
    
    loading.value = true
    
    // 智能填充：如果没有填写当前体重，自动使用早晨体重或睡前体重
    let weight = form.value.weight
    if (!weight) {
      weight = form.value.morning_weight || form.value.evening_weight
    }
    
    // 准备保存的数据（体重需要转换为kg）
    const saveData = {
      weight: weight ? settingsStore.convertWeightToKg(weight) : null,
      morning_weight: form.value.morning_weight ? settingsStore.convertWeightToKg(form.value.morning_weight) : null,
      evening_weight: form.value.evening_weight ? settingsStore.convertWeightToKg(form.value.evening_weight) : null,
      body_fat: form.value.body_fat || null,
      record_date: form.value.record_date,
      note: form.value.note
    }
    
    await createWeightRecord(saveData)
    
    ElMessage.success('体重记录成功')
    emit('success')
    handleClose()
  } catch (error) {
    console.error('提交失败:', error)
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    }
  } finally {
    loading.value = false
  }
}
</script>
