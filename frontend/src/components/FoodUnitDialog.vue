<template>
  <el-dialog 
    title="管理食物单位"
    v-model="dialogVisible"
    width="500px"
  >
    <!-- 单位列表 -->
    <div class="unit-list" v-if="unitList.length > 0">
      <div class="unit-item" v-for="unit in unitList" :key="unit.unit_id">
        <div class="unit-info">
          <span class="unit-name">{{ unit.unit_name }}</span>
          <span class="unit-weight">{{ unit.unit_weight }}g</span>
        </div>
        <div class="unit-actions">
          <el-button 
            type="primary" 
            link 
            size="small"
            @click="handleEdit(unit)"
          >
            编辑
          </el-button>
          <el-button 
            type="danger" 
            link 
            size="small"
            @click="handleDelete(unit.unit_id)"
          >
            删除
          </el-button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <el-empty v-else description="暂无自定义单位" />

    <!-- 添加/编辑表单 -->
    <div class="form-section">
      <el-divider />
      <h4>{{ editingUnit ? '编辑单位' : '添加新单位' }}</h4>
      
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="80px"
        size="small"
      >
        <el-form-item label="单位名称" prop="unit_name">
          <el-input
            v-model="formData.unit_name"
            placeholder="例：份、个、只、碗"
            maxlength="20"
          />
        </el-form-item>

        <el-form-item label="单位重量" prop="unit_weight">
          <div class="weight-input">
            <el-input-number
              v-model="formData.unit_weight"
              :min="1"
              :precision="0"
              placeholder="克"
            />
            <span class="unit-label">克</span>
          </div>
        </el-form-item>
      </el-form>

      <!-- 预设单位快速添加 -->
      <div class="preset-units">
        <p class="preset-title">快速添加预设单位：</p>
        <div class="preset-buttons">
          <el-button 
            v-for="preset in presetUnits" 
            :key="preset.name"
            size="small"
            @click="addPresetUnit(preset)"
          >
            {{ preset.name }}
          </el-button>
        </div>
      </div>
    </div>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button 
        type="primary" 
        @click="handleSubmit"
        :loading="submitting"
      >
        {{ editingUnit ? '更新' : '添加' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createFoodUnit,
  getFoodUnits,
  updateFoodUnit,
  deleteFoodUnit,
} from '@/api/foodUnit'

const props = defineProps({
  modelValue: Boolean,
  foodId: Number,
})

const emit = defineEmits(['update:modelValue', 'update'])

const dialogVisible = ref(false)
const unitList = ref([])
const submitting = ref(false)
const editingUnit = ref(null)

const formRef = ref(null)
const formData = ref({
  unit_name: '',
  unit_weight: 100,
})

const rules = {
  unit_name: [
    { required: true, message: '请输入单位名称', trigger: 'blur' },
    { min: 1, max: 20, message: '单位名称长度在1-20个字符', trigger: 'blur' },
  ],
  unit_weight: [
    { required: true, message: '请输入单位重量', trigger: 'blur' },
  ],
}

// 预设单位列表
const presetUnits = [
  { name: '份', weight: 100 },
  { name: '个', weight: 50 },
  { name: '只', weight: 100 },
  { name: '碗', weight: 200 },
  { name: '杯', weight: 150 },
  { name: '勺', weight: 20 },
  { name: '片', weight: 30 },
  { name: '根', weight: 100 },
  { name: '条', weight: 80 },
  { name: '盒', weight: 250 },
  { name: '袋', weight: 80 },
  { name: '罐', weight: 300 },
]

watch(() => props.modelValue, (val) => {
  dialogVisible.value = val
  if (val) {
    loadUnits()
    resetForm()
  }
})

watch(dialogVisible, (val) => {
  emit('update:modelValue', val)
})

const loadUnits = async () => {
  try {
    const data = await getFoodUnits(props.foodId)
    unitList.value = data || []
  } catch (error) {
    console.error('加载单位失败:', error)
    ElMessage.error('加载单位失败')
  }
}

const resetForm = () => {
  editingUnit.value = null
  formData.value = {
    unit_name: '',
    unit_weight: 100,
  }
  formRef.value?.clearValidate()
}

const handleEdit = (unit) => {
  editingUnit.value = unit
  formData.value = {
    unit_name: unit.unit_name,
    unit_weight: unit.unit_weight,
  }
}

const addPresetUnit = (preset) => {
  formData.value.unit_name = preset.name
  formData.value.unit_weight = preset.weight
}

const handleSubmit = async () => {
  await formRef.value?.validate()

  submitting.value = true
  try {
    if (editingUnit.value) {
      // 更新
      await updateFoodUnit(props.foodId, editingUnit.value.unit_id, {
        unit_name: formData.value.unit_name,
        unit_weight: formData.value.unit_weight,
      })
      ElMessage.success('单位已更新')
    } else {
      // 创建
      await createFoodUnit(props.foodId, {
        unit_name: formData.value.unit_name,
        unit_weight: formData.value.unit_weight,
      })
      ElMessage.success('单位已添加')
    }

    await loadUnits()
    resetForm()
    emit('update')
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error(error.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

const handleDelete = (unitId) => {
  ElMessageBox.confirm('确定删除该单位吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(async () => {
      try {
        await deleteFoodUnit(props.foodId, unitId)
        ElMessage.success('单位已删除')
        await loadUnits()
        emit('update')
      } catch (error) {
        console.error('删除失败:', error)
        ElMessage.error('删除失败')
      }
    })
    .catch(() => {
      // 取消删除
    })
}

const handleClose = () => {
  dialogVisible.value = false
  resetForm()
}
</script>

<style scoped>
.unit-list {
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: 20px;
}

.unit-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 8px;
}

.unit-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.unit-name {
  font-weight: 600;
  color: #333;
  min-width: 60px;
}

.unit-weight {
  color: #666;
  font-size: 12px;
}

.unit-actions {
  display: flex;
  gap: 8px;
}

.form-section {
  margin-top: 20px;
}

.form-section h4 {
  margin: 0 0 16px 0;
  font-size: 14px;
  color: #333;
}

.weight-input {
  display: flex;
  align-items: center;
  gap: 8px;
}

.weight-input :deep(.el-input-number) {
  flex: 1;
}

.unit-label {
  color: #666;
  font-size: 14px;
}

.preset-units {
  margin-top: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.preset-title {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: #666;
  font-weight: 600;
}

.preset-buttons {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.preset-buttons :deep(.el-button) {
  font-size: 12px;
}
</style>
