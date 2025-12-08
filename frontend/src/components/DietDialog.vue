<template>
  <el-dialog
    v-model="dialogVisible"
    title="饮食记录"
    width="500px"
    :before-close="handleClose"
  >
    <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
      <el-form-item label="餐次" prop="meal_type">
        <el-select v-model="form.meal_type" placeholder="选择餐次" style="width: 100%">
          <el-option label="早餐" value="breakfast" />
          <el-option label="午餐" value="lunch" />
          <el-option label="晚餐" value="dinner" />
          <el-option label="加餐" value="snack" />
        </el-select>
      </el-form-item>

      <el-form-item label="食物名称" prop="food_name">
        <div style="display: flex; gap: 8px;">
          <el-input
            v-model="form.food_name"
            placeholder="请输入食物名称"
            style="flex: 1;"
          />
          <el-button type="primary" @click="handleOpenFoodSelector">
            选择食物
          </el-button>
        </div>
      </el-form-item>

      <el-form-item label="卡路里" prop="calories">
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

      <el-form-item label="蛋白质" prop="protein">
        <div style="display: flex; align-items: center; width: 100%;">
          <el-input-number
            v-model="form.protein"
            :min="0"
            :precision="1"
            controls-position="right"
            style="flex: 1;"
          />
          <span style="margin-left: 8px; white-space: nowrap;">g</span>
        </div>
      </el-form-item>

      <el-form-item label="碳水化合物" prop="carbs">
        <div style="display: flex; align-items: center; width: 100%;">
          <el-input-number
            v-model="form.carbs"
            :min="0"
            :precision="1"
            controls-position="right"
            style="flex: 1;"
          />
          <span style="margin-left: 8px; white-space: nowrap;">g</span>
        </div>
      </el-form-item>

      <el-form-item label="脂肪" prop="fat">
        <div style="display: flex; align-items: center; width: 100%;">
          <el-input-number
            v-model="form.fat"
            :min="0"
            :precision="1"
            controls-position="right"
            style="flex: 1;"
          />
          <span style="margin-left: 8px; white-space: nowrap;">g</span>
        </div>
      </el-form-item>

      <el-form-item label="份量" prop="portion">
        <el-input
          v-model="form.portion"
          placeholder="例如：一碗、200g"
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
          :rows="2"
          placeholder="备注..."
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
import { createDietRecord } from '@/api/health'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const props = defineProps({
  modelValue: Boolean,
  mealType: String
})

const emit = defineEmits(['update:modelValue', 'success', 'food-selected'])

const dialogVisible = ref(false)
const formRef = ref(null)
const loading = ref(false)
const showFoodSelector = ref(false)

const form = ref({
  meal_type: '',
  food_name: '',
  calories: 0,
  protein: 0,
  carbs: 0,
  fat: 0,
  portion: '',
  record_date: dayjs().format('YYYY-MM-DD'),
  note: ''
})

const rules = {
  meal_type: [{ required: true, message: '请选择餐次', trigger: 'change' }],
  food_name: [{ required: true, message: '请输入食物名称', trigger: 'blur' }],
  record_date: [{ required: true, message: '请选择日期', trigger: 'change' }]
}

watch(() => props.modelValue, (val) => {
  dialogVisible.value = val
  if (val) {
    resetForm()
    if (props.mealType) {
      form.value.meal_type = props.mealType
    }
  }
})

watch(dialogVisible, (val) => {
  emit('update:modelValue', val)
})

const resetForm = () => {
  form.value = {
    meal_type: '',
    food_name: '',
    calories: 0,
    protein: 0,
    carbs: 0,
    fat: 0,
    portion: '',
    record_date: dayjs().format('YYYY-MM-DD'),
    note: ''
  }
  formRef.value?.clearValidate()
}

const handleClose = () => {
  dialogVisible.value = false
}

const handleOpenFoodSelector = () => {
  // 针对不同的布局，需要不同的处理方式
  // 在 DietDialog 中：发送 emit 给父组件
  emit('open-food-selector')
}

const handleFoodSelected = (selectedFood) => {
  // 回显食物名称和营养成分
  console.log('[DietDialog] Food selected:', selectedFood)
  
  // 兼容不同的数据格式
  const foodName = selectedFood.name || selectedFood.food_name
  const calories = selectedFood.calories
  const protein = selectedFood.protein
  const carbs = selectedFood.carbs
  const fat = selectedFood.fat
  const portion = selectedFood.portion || (selectedFood.total_weight ? `${selectedFood.total_weight}g` : '')
  
  form.value.food_name = foodName
  form.value.calories = calories || 0
  form.value.protein = protein || 0
  form.value.carbs = carbs || 0
  form.value.fat = fat || 0
  form.value.portion = portion
  
  console.log('[DietDialog] Form updated:', form.value)
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    loading.value = true
    
    await createDietRecord(form.value)
    
    ElMessage.success('饮食记录成功')
    emit('success')
    handleClose()
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    loading.value = false
  }
}

// 导出手动方法，供父组件调用
defineExpose({
  handleFoodSelected
})
</script>
