<template>
  <el-dialog
    v-model="dialogVisible"
    title="选择食物"
    width="85%"
    max-width="1000px"
    :before-close="handleClose"
    class="food-selector-dialog"
  >
    <!-- 库切换选项卡 -->
    <div class="library-tabs">
      <el-radio-group v-model="selectedLibrary" size="large">
        <el-radio-button label="local">本地食物库</el-radio-button>
        <el-radio-button label="online">在线食物库</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 搜索栏 -->
    <div class="search-section">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索食物..."
        clearable
        @keyup.enter="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-button type="primary" @click="handleSearch" :loading="loading">
        搜索
      </el-button>
    </div>

    <!-- 左右布局容器 -->
    <div class="main-container">
      <!-- 左侧：食物列表 -->
      <div class="left-section">
        <!-- 食物列表 -->
        <div class="food-list-container" v-loading="loading">
          <el-empty
            v-if="!foods.length && searched"
            description="未找到相关食物"
          />
          
          <el-radio-group v-else-if="foods.length" v-model="selectedFood" @change="handleFoodSelect">
            <div class="food-items">
              <div
                v-for="food in foods"
                :key="food.id || food.external_id"
                class="food-item-wrapper"
              >
                <el-radio :label="food" :value="food" class="food-radio">
                  <div class="food-item-content">
                    <div class="food-basic">
                      <div class="food-name">{{ food.name }}</div>
                      <div class="food-calories">
                        {{ food.calories }} 千卡/100g
                      </div>
                    </div>
                    <div class="food-nutrients">
                      <span class="nutrient-badge">蛋白: {{ food.protein || 0 }}g</span>
                      <span class="nutrient-badge">碳水: {{ food.carbs || 0 }}g</span>
                      <span class="nutrient-badge">脂肪: {{ food.fat || 0 }}g</span>
                    </div>
                  </div>
                </el-radio>
              </div>
            </div>
          </el-radio-group>

          <el-empty
            v-else-if="!foods.length && selectedLibrary === 'online' && !searched"
            description="输入关键词下手搜索"
          />
        </div>
      </div>

      <!-- 右侧：选中食物的详情（图片+分量+营养） -->
      <div v-if="selectedFood" class="right-detail-section">
        <!-- 食物图片 -->
        <div class="image-container">
          <img
            v-if="selectedFood?.image_url"
            :src="selectedFood.image_url"
            :alt="selectedFood.name"
            class="food-image"
          />
          <div v-else class="image-placeholder">
            <div class="placeholder-icon">🍳</div>
            <div class="placeholder-text">暂无图片</div>
          </div>
        </div>

        <!-- 分量和营养信息 -->
        <div class="detail-info-section">
          <!-- 分量设置 -->
          <div class="portion-section">
            <h4 class="portion-title">份量：</h4>
            <div class="portion-input">
              <el-input-number
                v-model="portionAmount"
                :min="1"
                :max="1000"
                :precision="0"
                size="small"
                @change="handlePortionChange"
              />
              <span class="portion-unit">克</span>
            </div>
          </div>

          <!-- 营养成分 -->
          <div class="nutrition-display">
            <div class="nutrition-grid">
              <div class="nutrition-item">
                <div class="nutrition-label">热量</div>
                <div class="nutrition-value-unit">
                  <span class="nutrition-value">{{ calculatedNutrition.calories }}</span>
                  <span class="nutrition-unit">kcal</span>
                </div>
              </div>
              <div class="nutrition-item">
                <div class="nutrition-label">蛋白质</div>
                <div class="nutrition-value-unit">
                  <span class="nutrition-value">{{ calculatedNutrition.protein }}</span>
                  <span class="nutrition-unit">g</span>
                </div>
              </div>
              <div class="nutrition-item">
                <div class="nutrition-label">碳水</div>
                <div class="nutrition-value-unit">
                  <span class="nutrition-value">{{ calculatedNutrition.carbs }}</span>
                  <span class="nutrition-unit">g</span>
                </div>
              </div>
              <div class="nutrition-item">
                <div class="nutrition-label">脂肪</div>
                <div class="nutrition-value-unit">
                  <span class="nutrition-value">{{ calculatedNutrition.fat }}</span>
                  <span class="nutrition-unit">g</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 其他单位 -->
          <div class="other-unit-section">
            <div class="section-header">
              <h4 class="section-title">其他单位</h4>
              <el-button 
                type="primary" 
                link 
                size="small"
                @click="showUnitDialog = true"
              >
                管理单位
              </el-button>
            </div>

            <div class="unit-buttons-section" v-if="foodUnits.length > 0">
              <!-- 单位按钮平铺 -->
              <div class="unit-buttons">
                <el-button
                  v-for="unit in foodUnits"
                  :key="unit.unit_id"
                  :type="selectedUnit?.unit_id === unit.unit_id ? 'primary' : 'default'"
                  size="small"
                  @click="handleUnitSelect(unit)"
                >
                  {{ unit.unit_name }}
                </el-button>
              </div>

              <!-- 数量和重量同一行 -->
              <div class="quantity-weight-row" v-if="selectedUnit">
                <div class="quantity-section">
                  <label class="row-label">数量</label>
                  <div class="quantity-input">
                    <el-input-number
                      v-model="unitQuantity"
                      :min="1"
                      :precision="0"
                      size="small"
                      @change="handleUnitQuantityChange"
                    />
                    <span class="quantity-unit">{{ selectedUnit.unit_name }}</span>
                  </div>
                </div>

                <div class="weight-section">
                  <label class="row-label">重量</label>
                  <div class="weight-display">
                    <span class="weight-value">{{ unitTotalWeight }}</span>
                    <span class="weight-unit">g</span>
                  </div>
                </div>
              </div>

              <!-- 可编辑腊养 -->
              <div class="editable-nutrition" v-if="selectedUnit">
                <div class="nutrition-grid-edit">
                  <div class="nutrition-edit-item">
                    <label>热量(kcal)</label>
                    <el-input-number
                      v-model="unitNutrition.calories"
                      :precision="1"
                      :min="0"
                      size="small"
                    />
                  </div>
                  <div class="nutrition-edit-item">
                    <label>蛋白质(g)</label>
                    <el-input-number
                      v-model="unitNutrition.protein"
                      :precision="1"
                      :min="0"
                      size="small"
                    />
                  </div>
                  <div class="nutrition-edit-item">
                    <label>碳水(g)</label>
                    <el-input-number
                      v-model="unitNutrition.carbs"
                      :precision="1"
                      :min="0"
                      size="small"
                    />
                  </div>
                  <div class="nutrition-edit-item">
                    <label>脂肪(g)</label>
                    <el-input-number
                      v-model="unitNutrition.fat"
                      :precision="1"
                      :min="0"
                      size="small"
                    />
                  </div>
                </div>
              </div>
            </div>

            <el-empty v-else description="暂无自定义单位，请添加" />
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button 
        type="primary" 
        @click="handleConfirm"
        :disabled="!selectedFood"
      >
        确定选择
      </el-button>
    </template>
  </el-dialog>

  <!-- 单位管理弹窗 -->
  <FoodUnitDialog
    v-model="showUnitDialog"
    v-if="selectedFood"
    :food-id="selectedFood.id || selectedFood.external_id"
    @update="loadFoodUnits"
  />
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { searchFoodOnline, getLocalFoods } from '@/api/food'
import { getFoodUnits, saveFoodUnitRecord } from '@/api/foodUnit'
import { ElMessage } from 'element-plus'
import FoodUnitDialog from './FoodUnitDialog.vue'

const props = defineProps({
  modelValue: Boolean
})

const emit = defineEmits(['update:modelValue', 'select'])

const dialogVisible = ref(false)
const selectedLibrary = ref('local')
const searchKeyword = ref('')
const loading = ref(false)
const searched = ref(false)
const foods = ref([])
const selectedFood = ref(null)
const portionAmount = ref(100)

// 其他单位相关
const showUnitDialog = ref(false)
const foodUnits = ref([])
const selectedUnit = ref(null)
const unitQuantity = ref(1)
const unitNutrition = ref({
  calories: 0,
  protein: 0,
  carbs: 0,
  fat: 0,
})

watch(() => props.modelValue, (val) => {
  console.log('[FoodSelector] modelValue changed:', val)
  dialogVisible.value = val
  if (val) {
    resetState()
    loadInitialFoods()
  }
})

watch(dialogVisible, (val) => {
  emit('update:modelValue', val)
})

// 监听库切换事件
watch(selectedLibrary, () => {
  // 切换库时，清空右侧食物信息
  selectedFood.value = null
  resetState()
  loadInitialFoods()
})

const resetState = () => {
  searchKeyword.value = ''
  // selectedFood.value = null  // 注释掉，让loadInitialFoods自动选中第一条
  portionAmount.value = 100
  foods.value = []
  searched.value = false
}

const loadInitialFoods = async () => {
  if (selectedLibrary.value === 'local') {
    try {
      loading.value = true
      const res = await getLocalFoods({ page: 1, page_size: 20, random: true })
      foods.value = res.items || []
      console.log('[FoodSelector] Loaded foods:', foods.value.length, 'items')
      searched.value = false
      
      // 如果有数据，默认选中第一条
      if (foods.value.length > 0) {
        selectedFood.value = foods.value[0]
        await loadFoodUnits()
      }
    } catch (error) {
      console.error('[FoodSelector] Load foods error:', error)
      ElMessage.error('加载食物库失败：' + error.message)
      // 作为非QA环境，添加一些模拟数据用于测试
      if (error.response?.status === 401 || error.response?.status === 403) {
        foods.value = [
          { id: 1, name: '鸡胸肉', calories: 165, protein: 31, carbs: 0, fat: 3.6, category: '肉类', image_url: '' },
          { id: 2, name: '米饭', calories: 130, protein: 2.7, carbs: 28, fat: 0.3, category: '主食', image_url: '' }
        ]
        // 有模拟数据时也默认选中第一条
        if (foods.value.length > 0) {
          selectedFood.value = foods.value[0]
          await loadFoodUnits()
        }
      }
    } finally {
      loading.value = false
    }
  } else {
    // 在线食物库初始化时不自动加载，等待用户搜索
    foods.value = []
    searched.value = false
  }
}

const handleSearch = async () => {
  if (!searchKeyword.value.trim()) {
    ElMessage.warning('请输入食物名称')
    return
  }

  loading.value = true
  searched.value = true

  try {
    if (selectedLibrary.value === 'local') {
      const res = await getLocalFoods({
        keyword: searchKeyword.value,
        page: 1,
        page_size: 50
      })
      foods.value = res.items || []
    } else {
      // 在线食物库
      const res = await searchFoodOnline(searchKeyword.value)
      foods.value = res.data || []
    }

    if (foods.value.length === 0) {
      ElMessage.info('未找到相关食物')
    }
  } catch (error) {
    ElMessage.error('搜索失败')
  } finally {
    loading.value = false
  }
}

const handleFoodSelect = () => {
  portionAmount.value = 100
  // 加载该食物的单位
  loadFoodUnits()
  // 重置其他单位相关状态
  selectedUnit.value = null
  unitQuantity.value = 1
  unitNutrition.value = {
    calories: 0,
    protein: 0,
    carbs: 0,
    fat: 0,
  }
}

const loadFoodUnits = async () => {
  if (!selectedFood.value) return
  
  try {
    // 区分是本地食物库还是在线食物库
    const sourceType = selectedFood.value.id ? 'local' : 'online'
    const foodId = selectedFood.value.id || selectedFood.value.external_id
    const data = await getFoodUnits(foodId, sourceType)
    foodUnits.value = data || []
  } catch (error) {
    console.error('加载单位失败:', error)
    foodUnits.value = []
  }
}

const handlePortionChange = () => {
  // 计算更新自动进行
}

const calculatedNutrition = computed(() => {
  if (!selectedFood.value) {
    return { calories: 0, protein: 0, carbs: 0, fat: 0 }
  }

  const ratio = portionAmount.value / 100
  return {
    calories: parseFloat((selectedFood.value.calories * ratio).toFixed(1)),
    protein: parseFloat((selectedFood.value.protein * ratio).toFixed(1)),
    carbs: parseFloat((selectedFood.value.carbs * ratio).toFixed(1)),
    fat: parseFloat((selectedFood.value.fat * ratio).toFixed(1))
  }
})

// 其他单位总重鮏
 const unitTotalWeight = computed(() => {
  if (!selectedUnit.value) return 0
  return selectedUnit.value.unit_weight * unitQuantity.value
})

const handleUnitChange = () => {
  if (!selectedUnit.value) return
  
  // 根据选择的单位重量计算腊养
  handleUnitQuantityChange()
}

const handleUnitSelect = (unit) => {
  // 第一次点击选中，第二次点击取消
  if (selectedUnit.value?.unit_id === unit.unit_id) {
    selectedUnit.value = null
    unitQuantity.value = 1
    unitNutrition.value = {
      calories: 0,
      protein: 0,
      carbs: 0,
      fat: 0,
    }
  } else {
    selectedUnit.value = unit
    unitQuantity.value = 1
    handleUnitQuantityChange()
  }
}

const handleUnitQuantityChange = () => {
  if (!selectedUnit.value || !selectedFood.value) return
  
  const totalWeight = unitTotalWeight.value
  const ratio = totalWeight / 100
  
  // 计算腊养
  unitNutrition.value = {
    calories: parseFloat((selectedFood.value.calories * ratio).toFixed(1)),
    protein: parseFloat((selectedFood.value.protein * ratio).toFixed(1)),
    carbs: parseFloat((selectedFood.value.carbs * ratio).toFixed(1)),
    fat: parseFloat((selectedFood.value.fat * ratio).toFixed(1)),
  }
}

const handleConfirm = async () => {
  if (!selectedFood.value) {
    ElMessage.warning('请选择食物')
    return
  }

  // 如果选择了其他单位，先保存单位记录到Redis
  if (selectedUnit.value) {
    try {
      // 区分是本地食物库还是在线食物库
      const sourceType = selectedFood.value.id ? 'local' : 'online'
      const foodId = selectedFood.value.id || selectedFood.value.external_id
      await saveFoodUnitRecord({
        food_id: foodId,
        unit_id: selectedUnit.value.unit_id,
        quantity: unitQuantity.value,
        total_weight: unitTotalWeight.value,
        source_type: sourceType,
        ...unitNutrition.value
      })
    } catch (error) {
      console.error('保存单位记录失败:', error)
      ElMessage.error('保存单位记录失败')
      return
    }

    // 返回其他单位的数据
    const result = {
      ...selectedFood.value,
      unit_mode: true,
      unit_id: selectedUnit.value.unit_id,
      unit_name: selectedUnit.value.unit_name,
      quantity: unitQuantity.value,
      portion: `${unitQuantity.value}${selectedUnit.value.unit_name}`,
      total_weight: unitTotalWeight.value,
      ...unitNutrition.value
    }
    console.log('[FoodSelector] Confirm with other unit:', result)
    emit('select', result)
  } else {
    // 普通克数模式
    const result = {
      ...selectedFood.value,
      unit_mode: false,
      portion: `${portionAmount.value}g`,
      ...calculatedNutrition.value
    }
    console.log('[FoodSelector] Confirm and emit select event:', result)
    emit('select', result)
  }

  handleClose()
}

const handleClose = () => {
  dialogVisible.value = false
}
</script>

<style scoped>
.food-selector-dialog {
  --el-dialog-max-height: 90vh;
}

.library-tabs {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.search-section {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.search-section :deep(.el-input) {
  flex: 1;
}

.main-container {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  min-height: 400px;
}

.left-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 400px;
}

.right-detail-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex-shrink: 0;
}

.detail-info-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.food-list-container {
  flex: 1;
  overflow-y: auto;
  padding-right: 8px;
  min-height: 350px;
}

.food-items {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.food-item-wrapper {
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  padding: 12px 10px;
  transition: all 0.3s;
  cursor: pointer;
  min-height: 100px;
  display: flex;
  align-items: center;
}

.food-item-wrapper:hover {
  background-color: #fafafa;
  border-color: #409eff;
}

.food-radio {
  width: 100%;
  margin: 0;
}

.food-radio :deep(.el-radio__label) {
  width: 100%;
  padding-left: 12px;
  margin: 0;
}

.food-item-content {
  display: flex;
  flex-direction: column;
  gap: 7px;
  width: 100%;
}

.food-basic {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.food-name {
  font-weight: 600;
  color: #333;
  font-size: 14px;
  flex: 1;
}

.food-calories {
  color: #ff6b6b;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
}

.food-nutrients {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.nutrient-badge {
  background-color: #f0f9ff;
  color: #0284c7;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  border: 1px solid #bae6fd;
}

.image-container {
  width: 100%;
  height: 300px;
  aspect-ratio: 1;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
  background: #fafafa;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0;
  flex-shrink: 0;
}

.food-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #999;
  text-align: center;
  padding: 20px;
}

.placeholder-icon {
  font-size: 48px;
}

.placeholder-text {
  font-size: 12px;
  color: #ccc;
}

.portion-section {
  background-color: transparent;
  padding: 0;
  border-radius: 0;
  margin-top: 0;
  width: 100%;
  margin-bottom: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.portion-title {
  display: inline-block;
  margin: 0 12px 0 0;
  font-size: 14px;
  color: #333;
  font-weight: 600;
  min-width: fit-content;
}

.portion-input {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 0;
  flex: 1;
}

.portion-label {
  display: none;
}

.portion-input :deep(.el-input-number) {
  flex: 1;
  height: 40px;
}

.portion-input :deep(.el-input-number__increase),
.portion-input :deep(.el-input-number__decrease) {
  width: 40px;
  height: 40px;
  line-height: 40px;
}

.portion-input :deep(.el-input-number__increase i),
.portion-input :deep(.el-input-number__decrease i) {
  font-size: 18px;
}

.portion-unit {
  font-size: 13px;
  color: #999;
  min-width: 20px;
}

.nutrition-display {
  background-color: transparent;
  padding: 0;
  border-radius: 0;
}

.nutrition-title {
  display: none;
}

.nutrition-grid {
  width: 100%;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.nutrition-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 8px;
  text-align: center;
  border: 1px solid #e5e7eb;
}

.nutrition-label {
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
}

.nutrition-value-unit {
  display: flex;
  align-items: baseline;
  gap: 3px;
  justify-content: center;
}

.nutrition-value {
  font-size: 16px;
  font-weight: 700;
  color: #ff6b6b;
}

.nutrition-unit {
  font-size: 11px;
  color: #999;
  margin-top: 0;
}

/* 其他单位样式 */
.other-unit-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-title {
  margin: 0;
  font-size: 14px;
  color: #333;
  font-weight: 600;
}

.unit-convert-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.unit-convert-section :deep(.el-form-item) {
  margin-bottom: 0;
}

.unit-convert-section :deep(.el-form-item__content) {
  line-height: normal;
}

.editable-nutrition {
  margin-top: 12px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}

.edit-label {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: #666;
  font-weight: 600;
}

.nutrition-grid-edit {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.nutrition-edit-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nutrition-edit-item label {
  font-size: 12px;
  color: #666;
}

.nutrition-edit-item :deep(.el-input-number) {
  width: 100%;
}

/* 单位按钮平铺样式 */
.unit-buttons-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.unit-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.unit-buttons :deep(.el-button) {
  flex-shrink: 0;
}

/* 数量和重量同一行样式 */
.quantity-weight-row {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.quantity-section,
.weight-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.row-label {
  font-size: 12px;
  color: #666;
  font-weight: 600;
}

.quantity-input {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 32px;
}

.quantity-input :deep(.el-input-number) {
  flex: 1;
  height: 100%;
}

.quantity-unit {
  font-size: 12px;
  color: #666;
  min-width: 40px;
}

.weight-display {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 8px;
  height: 32px;
  background: #f5f7fa;
  border-radius: 4px;
  box-sizing: border-box;
}

.weight-value {
  font-size: 16px;
  font-weight: 600;
  color: #ff6b6b;
}

.weight-unit {
  font-size: 12px;
  color: #999;
}
</style>
