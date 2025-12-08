<template>
  <el-dialog
    v-model="dialogVisible"
    :title="mode === 'create' ? '新增历史记录' : (isEdit ? '编辑历史记录' : '查看历史记录')"
    width="1000px"
    :before-close="handleClose"
  >
    <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
      <!-- 日期选择 -->
      <el-form-item label="记录日期" prop="record_date">
        <el-date-picker
          v-model="form.record_date"
          type="date"
          placeholder="选择日期"
          style="width: 100%"
          value-format="YYYY-MM-DD"
          :disabled-date="disabledDate"
          :disabled="!isEdit"
        />
      </el-form-item>

      <!-- 体重数据 -->
      <el-divider content-position="left">体重数据</el-divider>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="早晨体重">
            <div style="display: flex; align-items: center; width: 100%;">
              <el-input-number
                v-model="form.weight_record.morning_weight"
                :min="30"
                :max="settingsStore.weightUnit === 'jin' ? 600 : 300"
                :precision="1"
                :step="0.1"
                controls-position="right"
                style="flex: 1;"
                placeholder="可不填"
                :disabled="!isEdit"
              />
              <span style="margin-left: 8px; white-space: nowrap;">{{ settingsStore.getWeightUnitText() }}</span>
            </div>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="睡前体重">
            <div style="display: flex; align-items: center; width: 100%;">
              <el-input-number
                v-model="form.weight_record.evening_weight"
                :min="30"
                :max="settingsStore.weightUnit === 'jin' ? 600 : 300"
                :precision="1"
                :step="0.1"
                controls-position="right"
                style="flex: 1;"
                placeholder="可不填"
                :disabled="!isEdit"
              />
              <span style="margin-left: 8px; white-space: nowrap;">{{ settingsStore.getWeightUnitText() }}</span>
            </div>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="体脂率">
            <div style="display: flex; align-items: center; width: 100%;">
              <el-input-number
                v-model="form.weight_record.body_fat"
                :min="0"
                :max="100"
                :precision="1"
                :step="0.1"
                controls-position="right"
                style="flex: 1;"
                placeholder="可不填"
                :disabled="!isEdit"
              />
              <span style="margin-left: 8px; white-space: nowrap;">%</span>
            </div>
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 饮食记录 -->
      <el-divider content-position="left">
        饮食记录
        <el-button v-if="isEdit" type="primary" size="small" @click="addDiet" style="margin-left: 10px;">
          添加
        </el-button>
      </el-divider>
      <el-table :data="form.diet_records" border style="width: 100%; margin-bottom: 20px;">
        <el-table-column label="餐次" width="100">
          <template #default="{ row, $index }">
            <el-select v-model="row.meal_type" placeholder="选择餐次" size="small" :disabled="!isEdit">
              <el-option label="早餐" value="breakfast" />
              <el-option label="午餐" value="lunch" />
              <el-option label="晚餐" value="dinner" />
              <el-option label="加餐" value="snack" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="食物名称" width="180">
          <template #default="{ row, $index }">
            <div v-if="isEdit" style="display: flex; gap: 4px;">
              <el-input v-model="row.food_name" size="small" style="flex: 1;" />
              <el-button type="primary" size="small" @click="openFoodSelector($index)">
                选
              </el-button>
            </div>
            <el-input v-else v-model="row.food_name" size="small" disabled />
          </template>
        </el-table-column>
        <el-table-column label="卡路里(kcal)" width="120">
          <template #default="{ row }">
            <el-input-number v-model="row.calories" :min="0" size="small" controls-position="right" style="width: 100%;" :disabled="!isEdit" />
          </template>
        </el-table-column>
        <el-table-column label="蛋白质(g)" width="100">
          <template #default="{ row }">
            <el-input-number v-model="row.protein" :min="0" :precision="1" size="small" controls-position="right" style="width: 100%;" :disabled="!isEdit" />
          </template>
        </el-table-column>
        <el-table-column label="碳水(g)" width="100">
          <template #default="{ row }">
            <el-input-number v-model="row.carbs" :min="0" :precision="1" size="small" controls-position="right" style="width: 100%;" :disabled="!isEdit" />
          </template>
        </el-table-column>
        <el-table-column label="脂肪(g)" width="100">
          <template #default="{ row }">
            <el-input-number v-model="row.fat" :min="0" :precision="1" size="small" controls-position="right" style="width: 100%;" :disabled="!isEdit" />
          </template>
        </el-table-column>
        <el-table-column label="份量" width="100">
          <template #default="{ row }">
            <el-input v-model="row.portion" size="small" :disabled="!isEdit" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" v-if="isEdit">
          <template #default="{ $index }">
            <el-button type="danger" size="small" @click="removeDiet($index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 运动记录 -->
      <el-divider content-position="left">
        运动记录
        <el-button v-if="isEdit" type="primary" size="small" @click="addExercise" style="margin-left: 10px;">
          添加
        </el-button>
      </el-divider>
      <el-table :data="form.exercise_records" border style="width: 100%; margin-bottom: 20px;">
        <el-table-column label="运动类型" width="150">
          <template #default="{ row }">
            <el-select v-model="row.exercise_type" placeholder="选择类型" size="small" :disabled="!isEdit">
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
          </template>
        </el-table-column>
        <el-table-column label="时长(分钟)" width="120">
          <template #default="{ row }">
            <el-input-number v-model="row.duration" :min="1" size="small" controls-position="right" style="width: 100%;" :disabled="!isEdit" />
          </template>
        </el-table-column>
        <el-table-column label="消耗卡路里(kcal)" width="150">
          <template #default="{ row }">
            <el-input-number v-model="row.calories" :min="0" size="small" controls-position="right" style="width: 100%;" :disabled="!isEdit" />
          </template>
        </el-table-column>
        <el-table-column label="距离(km)" width="120">
          <template #default="{ row }">
            <el-input-number v-model="row.distance" :min="0" :precision="2" size="small" controls-position="right" style="width: 100%;" :disabled="!isEdit" />
          </template>
        </el-table-column>
        <el-table-column label="备注" min-width="150">
          <template #default="{ row }">
            <el-input v-model="row.note" size="small" :disabled="!isEdit" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" v-if="isEdit">
          <template #default="{ $index }">
            <el-button type="danger" size="small" @click="removeExercise($index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 睡眠记录 -->
      <el-divider content-position="left">
        睡眠记录
        <el-button v-if="isEdit" type="primary" size="small" @click="addSleep" style="margin-left: 10px;">
          添加
        </el-button>
      </el-divider>
      <el-table :data="form.sleep_records" border style="width: 100%; margin-bottom: 20px;">
        <el-table-column label="时长(小时)" width="120">
          <template #default="{ row }">
            <el-input-number v-model="row.duration" :min="0" :precision="1" size="small" controls-position="right" style="width: 100%;" :disabled="!isEdit" />
          </template>
        </el-table-column>
        <el-table-column label="质量" width="150">
          <template #default="{ row }">
            <el-select v-model="row.quality" placeholder="选择质量" size="small" :disabled="!isEdit">
              <el-option label="优秀" value="excellent" />
              <el-option label="良好" value="good" />
              <el-option label="一般" value="fair" />
              <el-option label="较差" value="poor" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="入睡时间" width="180">
          <template #default="{ row }">
            <el-date-picker
              v-model="row.sleep_time"
              type="datetime"
              placeholder="选择时间"
              size="small"
              value-format="YYYY-MM-DD HH:mm:ss"
              style="width: 100%;"
              :disabled="!isEdit"
            />
          </template>
        </el-table-column>
        <el-table-column label="起床时间" width="180">
          <template #default="{ row }">
            <el-date-picker
              v-model="row.wake_time"
              type="datetime"
              placeholder="选择时间"
              size="small"
              value-format="YYYY-MM-DD HH:mm:ss"
              style="width: 100%;"
              :disabled="!isEdit"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" v-if="isEdit">
          <template #default="{ $index }">
            <el-button type="danger" size="small" @click="removeSleep($index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 饮水记录 -->
      <el-divider content-position="left">
        饮水记录
        <el-button v-if="isEdit" type="primary" size="small" @click="addWater" style="margin-left: 10px;">
          添加
        </el-button>
      </el-divider>
      <el-table :data="form.water_records" border style="width: 100%; margin-bottom: 20px;">
        <el-table-column label="饮水量(ml)" width="200">
          <template #default="{ row }">
            <el-input-number v-model="row.amount" :min="0" :step="100" size="small" controls-position="right" style="width: 100%;" :disabled="!isEdit" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" v-if="isEdit">
          <template #default="{ $index }">
            <el-button type="danger" size="small" @click="removeWater($index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 备注 -->
      <el-form-item label="备注">
        <el-input
          v-model="form.note"
          type="textarea"
          :rows="3"
          placeholder="记录今天的感受..."
          :disabled="!isEdit"
        />
      </el-form-item>
    </el-form>

    <!-- 食物选择器 -->
    <FoodSelector v-model="showFoodSelector" @select="handleFoodSelected" />

    <template #footer>
      <el-button @click="handleClose">{{ isEdit ? '取消' : '关闭' }}</el-button>
      <el-button v-if="isEdit" type="primary" @click="handleSubmit" :loading="loading">
        保存
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { getDailyHistoryDetail, createDailyHistory, updateDailyHistory } from '@/api/daily'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import FoodSelector from './FoodSelector.vue'

const props = defineProps({
  modelValue: Boolean,
  historyId: Number,
  mode: {
    type: String,
    default: 'view' // view, edit, create
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

const settingsStore = useSettingsStore()
const dialogVisible = ref(false)
const formRef = ref(null)
const loading = ref(false)
const isEdit = ref(false)
const showFoodSelector = ref(false)
const selectedDietIndex = ref(-1)

const form = ref({
  record_date: dayjs().subtract(1, 'day').format('YYYY-MM-DD'),
  diet_records: [],
  exercise_records: [],
  weight_record: {
    morning_weight: null,
    evening_weight: null,
    body_fat: null,
    note: ''
  },
  sleep_records: [],
  water_records: [],
  note: ''
})

const rules = {
  record_date: [{ required: true, message: '请选择日期', trigger: 'change' }]
}

// 禁用今天及以后的日期
const disabledDate = (time) => {
  return time.getTime() >= new Date().setHours(0, 0, 0, 0)
}

watch(() => props.modelValue, (val) => {
  dialogVisible.value = val
  if (val) {
    isEdit.value = props.mode === 'edit' || props.mode === 'create'
    if (props.mode === 'create') {
      resetForm()
    } else if (props.historyId) {
      loadDetail()
    }
  }
})

watch(dialogVisible, (val) => {
  emit('update:modelValue', val)
})

const resetForm = () => {
  form.value = {
    record_date: dayjs().subtract(1, 'day').format('YYYY-MM-DD'),
    diet_records: [],
    exercise_records: [],
    weight_record: {
      morning_weight: null,
      evening_weight: null,
      body_fat: null,
      note: ''
    },
    sleep_records: [],
    water_records: [],
    note: ''
  }
  formRef.value?.clearValidate()
}

const loadDetail = async () => {
  try {
    loading.value = true
    const response = await getDailyHistoryDetail(props.historyId)
    
    // 转换体重单位
    if (response.weight_record) {
      response.weight_record.morning_weight = response.weight_record.morning_weight 
        ? settingsStore.convertWeightToDisplay(response.weight_record.morning_weight) 
        : null
      response.weight_record.evening_weight = response.weight_record.evening_weight 
        ? settingsStore.convertWeightToDisplay(response.weight_record.evening_weight) 
        : null
    } else {
      response.weight_record = {
        morning_weight: null,
        evening_weight: null,
        body_fat: null,
        note: ''
      }
    }
    
    form.value = response
  } catch (error) {
    console.error('加载详情失败:', error)
    ElMessage.error('加载详情失败')
  } finally {
    loading.value = false
  }
}

// 添加记录方法
const addDiet = () => {
  form.value.diet_records.push({
    meal_type: 'breakfast',
    food_name: '',
    calories: 0,
    protein: 0,
    carbs: 0,
    fat: 0,
    portion: '',
    note: ''
  })
}

const removeDiet = (index) => {
  form.value.diet_records.splice(index, 1)
}

const addExercise = () => {
  form.value.exercise_records.push({
    exercise_type: '跑步',
    duration: 30,
    calories: 0,
    distance: 0,
    note: ''
  })
}

const removeExercise = (index) => {
  form.value.exercise_records.splice(index, 1)
}

const addSleep = () => {
  form.value.sleep_records.push({
    duration: 8,
    quality: 'good',
    sleep_time: null,
    wake_time: null
  })
}

const removeSleep = (index) => {
  form.value.sleep_records.splice(index, 1)
}

const addWater = () => {
  form.value.water_records.push({
    amount: 250
  })
}

const removeWater = (index) => {
  form.value.water_records.splice(index, 1)
}

const openFoodSelector = (index) => {
  selectedDietIndex.value = index
  showFoodSelector.value = true
}

const handleFoodSelected = (selectedFood) => {
  if (selectedDietIndex.value >= 0 && selectedDietIndex.value < form.value.diet_records.length) {
    const dietRecord = form.value.diet_records[selectedDietIndex.value]
    dietRecord.food_name = selectedFood.name
    dietRecord.calories = selectedFood.calories
    dietRecord.protein = selectedFood.protein
    dietRecord.carbs = selectedFood.carbs
    dietRecord.fat = selectedFood.fat
    dietRecord.portion = selectedFood.portion
  }
}

const handleClose = () => {
  dialogVisible.value = false
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    loading.value = true
    
    // 智能填充：如果没有填写当前体重，自动使用早晨体重或睡前体重
    let weight = null
    if (form.value.weight_record.morning_weight || form.value.weight_record.evening_weight) {
      weight = form.value.weight_record.morning_weight || form.value.weight_record.evening_weight
    }
    
    // 准备提交的数据（体重需要转换回kg）
    const submitData = {
      record_date: form.value.record_date,
      diet_records: form.value.diet_records,
      exercise_records: form.value.exercise_records,
      weight_record: {
        weight: weight ? settingsStore.convertWeightToKg(weight) : null,
        morning_weight: form.value.weight_record.morning_weight 
          ? settingsStore.convertWeightToKg(form.value.weight_record.morning_weight) 
          : null,
        evening_weight: form.value.weight_record.evening_weight 
          ? settingsStore.convertWeightToKg(form.value.weight_record.evening_weight) 
          : null,
        body_fat: form.value.weight_record.body_fat || null,
        note: form.value.weight_record.note || ''
      },
      sleep_records: form.value.sleep_records,
      water_records: form.value.water_records,
      note: form.value.note
    }
    
    if (props.mode === 'create') {
      await createDailyHistory(submitData)
      ElMessage.success('创建成功')
    } else {
      await updateDailyHistory(props.historyId, submitData)
      ElMessage.success('更新成功')
    }
    
    emit('success')
    handleClose()
  } catch (error) {
    console.error('提交失败:', error)
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else {
      ElMessage.error('操作失败')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.el-divider {
  margin: 20px 0;
}
</style>
