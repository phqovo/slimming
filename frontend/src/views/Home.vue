<template>
  <div class="home-container">
    <!-- 欢迎卡片 -->
    <el-card class="welcome-card rounded-card" shadow="never">
      <div class="welcome-content">
        <div class="welcome-text">
          <h2>你好，{{ userStore.userInfo?.nickname }}！</h2>
          <p>{{ greeting }}</p>
          <!-- 个人信息提示 -->
          <div v-if="hasIncompleteProfile" class="profile-tip">
            您还没有设置完整的个人信息，
            <el-button 
              link 
              type="primary" 
              @click="navigateToProfile"
            >
              点击设置
            </el-button>
          </div>
        </div>
        <div class="stats-summary">
          <div class="stat-item">
            <div class="stat-label">当前体重</div>
            <div class="stat-value">
              {{ displayCurrentWeight }} <span>{{ settingsStore.getWeightUnitText() }}</span>
            </div>
            <!-- 体重变化箭头（移到下方） -->
            <div v-if="progress.weight_change !== null && progress.weight_change !== undefined" class="weight-change">
              <el-icon v-if="progress.weight_change < 0" class="change-icon down">
                <bottom />
              </el-icon>
              <el-icon v-else-if="progress.weight_change > 0" class="change-icon up">
                <top />
              </el-icon>
              <span :class="['change-text', progress.weight_change < 0 ? 'down' : 'up']">
                {{ Math.abs(settingsStore.convertWeightToDisplay(Math.abs(progress.weight_change))) }}
                {{ settingsStore.getWeightUnitText() }}
              </span>
            </div>
          </div>
          <div class="stat-item">
            <div class="stat-label">目标体重</div>
            <div class="stat-value">{{ displayTargetWeight }} <span>{{ settingsStore.getWeightUnitText() }}</span></div>
          </div>
          <div class="stat-item">
            <div class="stat-label">BMI</div>
            <div class="stat-value">{{ stats.bmi || '--' }}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">基础代谢</div>
            <div class="stat-value">{{ stats.bmr || '--' }} <span>kcal</span></div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 激励信息 -->
    <el-card v-if="encouragementMessage" class="encouragement-card rounded-card" shadow="never">
      <div class="encouragement-content">
        <el-icon class="trophy-icon"><trophy /></el-icon>
        <div class="encouragement-text">
          {{ encouragementMessage }}
        </div>
      </div>
    </el-card>

    <!-- 快捷操作 -->
    <div class="quick-actions">
      <el-button type="primary" :icon="TrendCharts" @click="showWeightDialog = true" round>
        记录体重
      </el-button>
      <el-button type="success" :icon="Trophy" @click="showExerciseDialog = true" round>
        运动打卡
      </el-button>
      <el-button type="warning" :icon="Apple" @click="showDietDialog = true" round>
        饮食记录
      </el-button>
    </div>

    <!-- 今日数据 -->
    <el-row :gutter="24" class="today-data">
      <!-- 饮食记录 -->
      <el-col :span="12">
        <el-card class="data-card rounded-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span><el-icon><Apple /></el-icon> 今日饮食</span>
              <el-button text type="primary" @click="showDietDialog = true">添加</el-button>
            </div>
          </template>
          <div class="diet-content">
            <div class="meal-section" v-for="mealType in mealTypes" :key="mealType.value">
              <div class="meal-header">
                <div class="meal-header-left">
                  <span class="meal-icon">{{ mealType.icon }}</span>
                  <span class="meal-name">{{ mealType.label }}</span>
                  <span class="meal-count" v-if="todayDiet[mealType.value]?.length">
                    {{ todayDiet[mealType.value].length }} 项
                  </span>
                </div>
                <el-button 
                  text 
                  size="small" 
                  type="primary"
                  @click="addMeal(mealType.value)"
                >
                  添加
                </el-button>
              </div>
              <div class="meal-list" v-if="todayDiet[mealType.value]?.length">
                <div 
                  class="meal-food-item" 
                  v-for="item in todayDiet[mealType.value]" 
                  :key="item.id"
                >
                  <span class="food-name">{{ item.food_name }}</span>
                  <span v-if="item.portion" class="portion">{{ item.portion }}</span>
                  <span class="calories">{{ item.calories }} kcal</span>
                </div>
              </div>
              <div class="empty-meal" v-else>暂无记录</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 运动记录 -->
      <el-col :span="12">
        <el-card class="data-card rounded-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span><el-icon><Trophy /></el-icon> 今日运动</span>
              <el-button text type="primary" @click="showExerciseDialog = true">添加</el-button>
            </div>
          </template>
          <div class="exercise-content">
            <div class="exercise-list" v-if="todayExercise.length">
              <div class="exercise-item" v-for="item in todayExercise" :key="item.id">
                <div class="exercise-info">
                  <div class="exercise-type">{{ item.exercise_type }}</div>
                  <div class="exercise-detail">
                    {{ item.duration }}分钟 · {{ item.calories }}千卡
                  </div>
                </div>
                <el-image 
                  v-if="item.image_url" 
                  :src="item.image_url" 
                  fit="cover" 
                  class="exercise-image"
                />
              </div>
            </div>
            <el-empty v-else description="暂无运动记录" :image-size="100" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 健康数据 -->
    <el-row :gutter="24">
      <!-- 饮水记录 -->
      <el-col :span="12">
        <el-card class="data-card rounded-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span><el-icon><Coffee /></el-icon> 今日饮水</span>
            </div>
          </template>
          <div class="water-content">
            <div class="water-progress">
              <el-progress 
                type="circle" 
                :percentage="waterPercentage" 
                :width="120"
                :stroke-width="12"
                color="#409eff"
              >
                <template #default>
                  <div class="progress-text">
                    <div class="amount">{{ totalWater }}</div>
                    <div class="unit">ml</div>
                  </div>
                </template>
              </el-progress>
            </div>
            <div class="water-actions">
              <el-button @click="addWater(200)" size="small">+200ml</el-button>
              <el-button @click="addWater(500)" size="small">+500ml</el-button>
              <el-button @click="showWaterDialog = true" size="small">自定义</el-button>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 睡眠记录 -->
      <el-col :span="12">
        <el-card class="data-card rounded-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span><el-icon><Moon /></el-icon> 昨夜睡眠</span>
              <el-button text type="primary" @click="showSleepDialog = true">
                {{ todaySleep ? '编辑' : '添加' }}
              </el-button>
            </div>
          </template>
          <div class="sleep-content">
            <div v-if="todaySleep" class="sleep-info">
              <div class="sleep-duration">
                <div class="duration-value">{{ formatSleepDuration(todaySleep.duration) }}</div>
                <div class="duration-unit">小时</div>
              </div>
              <div class="sleep-time-range" v-if="todaySleep.sleep_time && todaySleep.wake_time">
                <div class="time-item">
                  <span class="time-label">入睡</span>
                  <span class="time-value">{{ formatSleepTime(todaySleep.sleep_time) }}</span>
                </div>
                <div class="time-separator">~</div>
                <div class="time-item">
                  <span class="time-label">醒来</span>
                  <span class="time-value">{{ formatSleepTime(todaySleep.wake_time) }}</span>
                </div>
              </div>
              <div class="sleep-quality" v-if="todaySleep.quality">
                <el-tag :type="getSleepQualityType(todaySleep.quality)" size="large">
                  {{ getSleepQualityText(todaySleep.quality) }}
                </el-tag>
              </div>
            </div>
            <el-empty v-else description="暂无睡眠记录" :image-size="100" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 对话框 -->
    <WeightDialog v-model="showWeightDialog" @success="loadData" />
    <ExerciseDialog v-model="showExerciseDialog" @success="loadTodayExercise" />
    <DietDialog 
      ref="dietDialogRef"
      v-model="showDietDialog" 
      :meal-type="selectedMealType" 
      @success="loadTodayDiet"
      @open-food-selector="showFoodSelector = true"
    />
    <WaterDialog v-model="showWaterDialog" @success="loadTodayWater" />
    <SleepDialog v-model="showSleepDialog" :record="todaySleep" @success="loadTodaySleep" />
    <!-- 食物选择器 - 放在最上层，不会被嵌入其他dialog -->
    <FoodSelector 
      v-model="showFoodSelector" 
      @select="(food) => { handleFoodSelected(food); showFoodSelector = false }"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useSettingsStore } from '@/stores/settings'
import { getUserStats, getWeightProgress } from '@/api/user'
import { getExerciseRecords, getDietRecords } from '@/api/health'
import { getWaterRecords, getSleepRecords, createWaterRecord } from '@/api/health'
import { ElMessage } from 'element-plus'
import { TrendCharts, Trophy, Apple, Coffee, Moon, Top, Bottom } from '@element-plus/icons-vue'
import WeightDialog from '@/components/WeightDialog.vue'
import ExerciseDialog from '@/components/ExerciseDialog.vue'
import DietDialog from '@/components/DietDialog.vue'
import WaterDialog from '@/components/WaterDialog.vue'
import SleepDialog from '@/components/SleepDialog.vue'
import FoodSelector from '@/components/FoodSelector.vue'
import dayjs from 'dayjs'

const userStore = useUserStore()
const settingsStore = useSettingsStore()
const router = useRouter()
const dietDialogRef = ref(null)

const stats = ref({})
const progress = ref({})  // 新增：进度信息
const todayExercise = ref([])
const todayDiet = ref({})
const totalWater = ref(0)
const todaySleep = ref(null)

const showWeightDialog = ref(false)
const showExerciseDialog = ref(false)
const showDietDialog = ref(false)
const showFoodSelector = ref(false)
const showWaterDialog = ref(false)
const showSleepDialog = ref(false)
const selectedMealType = ref('')

const mealTypes = [
  { label: '早餐', value: 'breakfast', icon: '🌅' },
  { label: '午餐', value: 'lunch', icon: '🌞' },
  { label: '晚餐', value: 'dinner', icon: '🌙' },
  { label: '加餐', value: 'snack', icon: '🍎' }
]

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return '早上好！新的一天开始了'
  if (hour < 18) return '下午好！继续加油'
  return '晚上好！今天辛苦了'
})

const waterPercentage = computed(() => {
  const target = 2000 // 目标饮水量2000ml
  return Math.min(Math.round((totalWater.value / target) * 100), 100)
})

// 体重显示（根据单位转换）
const displayCurrentWeight = computed(() => {
  if (!stats.value.current_weight) return '--'
  return settingsStore.convertWeightToDisplay(stats.value.current_weight)
})

const displayTargetWeight = computed(() => {
  if (!stats.value.target_weight) return '--'
  return settingsStore.convertWeightToDisplay(stats.value.target_weight)
})

// 检查个人信息是否完整
const hasIncompleteProfile = computed(() => {
  const user = userStore.userInfo
  // 判断是否不完整：其中任何一个变量为空值
  return (
    !user ||
    !user.nickname ||
    !user.gender ||
    !user.age ||
    !user.height ||
    !user.current_weight ||
    !user.target_weight
  )
})

// 激励信息
const encouragementMessage = computed(() => {
  if (!progress.value || progress.value.weight_lost === null || progress.value.weight_lost === undefined) {
    return ''
  }
  
  const weightLost = progress.value.weight_lost
  const weightToGoal = progress.value.weight_to_goal
  const daysElapsed = progress.value.days_elapsed || 0
  
  // 转换为显示单位
  const displayWeightLost = settingsStore.convertWeightToDisplay(Math.abs(weightLost))
  const displayWeightToGoal = weightToGoal ? settingsStore.convertWeightToDisplay(Math.abs(weightToGoal)) : 0
  const unit = settingsStore.getWeightUnitText()
  
  if (weightLost > 0) {
    // 减重成功
    if (weightToGoal && weightToGoal <= 0) {
      return `🎉 太棒啦！你已经达成目标，成功减去 ${displayWeightLost} ${unit}，耗时 ${daysElapsed} 天！`
    } else if (weightToGoal) {
      return `👏 太棒啦！你已经减去 ${displayWeightLost} ${unit}，耗时 ${daysElapsed} 天，距离目标还有 ${displayWeightToGoal} ${unit}！`
    } else {
      return `💪 加油！你已经减去 ${displayWeightLost} ${unit}，耗时 ${daysElapsed} 天，继续加油！`
    }
  } else if (weightLost < 0) {
    // 体重增加
    return `⚠️ 注意！相比最初体重增加了 ${displayWeightLost} ${unit}，别气馁，从现在开始努力！`
  } else {
    // 体重未变化
    if (daysElapsed > 7) {
      return `🤔 体重 ${daysElapsed} 天没有变化，试试调整饮食和运动计划吧！`
    } else {
      return `👍 保持当前状态，坚持就是胜利！`
    }
  }
})

// 加载统计数据
const loadStats = async () => {
  try {
    const res = await getUserStats()
    stats.value = res.data
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

// 加载进度信息
const loadProgress = async () => {
  try {
    const res = await getWeightProgress()
    progress.value = res.data
  } catch (error) {
    console.error('加载进度信息失败:', error)
  }
}

// 加载今日运动
const loadTodayExercise = async () => {
  try {
    const today = dayjs().format('YYYY-MM-DD')
    const data = await getExerciseRecords({ record_date: today })
    todayExercise.value = data || []
  } catch (error) {
    console.error('加载运动记录失败:', error)
  }
}

// 加载今日饮食
const loadTodayDiet = async () => {
  try {
    const today = dayjs().format('YYYY-MM-DD')
    const data = await getDietRecords({ record_date: today })
    
    // 按餐次分组
    const grouped = {
      breakfast: [],
      lunch: [],
      dinner: [],
      snack: []
    }
    
    data?.forEach(item => {
      if (grouped[item.meal_type]) {
        grouped[item.meal_type].push(item)
      }
    })
    
    todayDiet.value = grouped
  } catch (error) {
    console.error('加载饮食记录失败:', error)
  }
}

// 加载今日饮水
const loadTodayWater = async () => {
  try {
    const today = dayjs().format('YYYY-MM-DD')
    const data = await getWaterRecords({ record_date: today })
    totalWater.value = data?.reduce((sum, item) => sum + item.amount, 0) || 0
  } catch (error) {
    console.error('加载饮水记录失败:', error)
  }
}

// 加载今日睡眠
const loadTodaySleep = async () => {
  try {
    const today = dayjs().format('YYYY-MM-DD')
    const data = await getSleepRecords({ record_date: today, limit: 1 })
    todaySleep.value = data?.[0] || null
  } catch (error) {
    console.error('加载睡眠记录失败:', error)
  }
}

// 添加饮水
const addWater = async (amount) => {
  try {
    await createWaterRecord({
      amount,
      record_date: dayjs().format('YYYY-MM-DD')
    })
    ElMessage.success(`已添加${amount}ml饮水`)
    loadTodayWater()
  } catch (error) {
    console.error('添加饮水失败:', error)
  }
}

// 添加餐次
const addMeal = (mealType) => {
  selectedMealType.value = mealType
  showDietDialog.value = true
}

// 处理食物选择器的回显
const handleFoodSelected = (selectedFood) => {
  console.log('[Home] Food selected:', selectedFood)
  // 将食物数据传递给 DietDialog 的函数
  if (dietDialogRef.value) {
    dietDialogRef.value.handleFoodSelected(selectedFood)
  }
}

// 获取睡眠质量类型
const getSleepQualityType = (quality) => {
  const map = {
    excellent: 'success',
    good: '',
    fair: 'warning',
    poor: 'danger'
  }
  return map[quality] || ''
}

// 获取睡眠质量文本
const getSleepQualityText = (quality) => {
  const map = {
    excellent: '优秀',
    good: '良好',
    fair: '一般',
    poor: '较差'
  }
  return map[quality] || quality
}

// 格式化睡眠时长（保疙2位小数）
const formatSleepDuration = (duration) => {
  if (!duration) return '0.00'
  return parseFloat(duration).toFixed(2)
}

// 格式化睡眠时间（显示时:分）
const formatSleepTime = (timeStr) => {
  if (!timeStr) return '--'
  return dayjs(timeStr).format('HH:mm')
}

// 个人信息设置导航
const navigateToProfile = () => {
  router.push('/profile')
}

// 加载所有数据
const loadData = async () => {
  // 确保设置已加载完成
  if (!settingsStore.isLoaded) {
    await settingsStore.loadSettings()
  }
  
  loadStats()
  loadProgress()  // 新增：加载进度信息
  loadTodayExercise()
  loadTodayDiet()
  loadTodayWater()
  loadTodaySleep()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.home-container {
  max-width: 1400px;
  margin: 0 auto;
}

.welcome-card {
  margin-bottom: 24px;
}

.welcome-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-text h2 {
  font-size: 24px;
  margin-bottom: 8px;
  color: #333;
}

.welcome-text p {
  font-size: 14px;
  color: #999;
}

/* 个人信息提示 */
.profile-tip {
  margin-top: 12px;
  padding: 12px 16px;
  background-color: #fff7e6;
  border-left: 4px solid #ff9800;
  border-radius: 4px;
  font-size: 14px;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
}

.stats-summary {
  display: flex;
  gap: 48px;
}

.stat-item {
  text-align: center;
}

.stat-label {
  font-size: 13px;
  color: #999;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #333;
}

.stat-value span {
  font-size: 14px;
  font-weight: 400;
  color: #999;
  margin-left: 4px;
}

/* 体重变化样式（移到下方） */
.weight-change {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 8px;
  font-size: 13px;
  gap: 4px;
}

.change-icon {
  font-size: 16px;
}

.change-icon.down {
  color: #67c23a;
}

.change-icon.up {
  color: #f56c6c;
}

.change-text {
  font-weight: 500;
}

.change-text.down {
  color: #67c23a;
}

.change-text.up {
  color: #f56c6c;
}

/* 激励卡片（柔和的渐变色） */
.encouragement-card {
  margin-bottom: 24px;
  background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
  border: 1px solid #e8eaf6;
}

.encouragement-content {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 0;
}

.trophy-icon {
  font-size: 42px;
  color: #ff9800;
}

.encouragement-text {
  flex: 1;
  font-size: 16px;
  font-weight: 500;
  color: #5e35b1;
  line-height: 1.6;
}

.quick-actions {
  margin-bottom: 24px;
  display: flex;
  gap: 16px;
}

.today-data {
  margin-bottom: 24px;
}

.data-card {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
}

.card-header span {
  display: flex;
  align-items: center;
  gap: 8px;
}

.diet-content {
  min-height: 400px;
}

.meal-section {
  margin-bottom: 20px;
}

.meal-section:last-child {
  margin-bottom: 0;
}

.meal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);
  border-radius: 8px;
  margin-bottom: 10px;
}

.meal-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.meal-icon {
  font-size: 20px;
}

.meal-name {
  font-weight: 600;
  color: #333;
  font-size: 15px;
}

.meal-count {
  font-size: 12px;
  color: #667eea;
  background: white;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 500;
}

.meal-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 0 4px;
}

.meal-food-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: white;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.meal-food-item:hover {
  background: #fafbff;
  border-color: #667eea;
  transform: translateX(2px);
}

.meal-food-item .food-name {
  flex: 1;
  color: #333;
  font-weight: 500;
}

.meal-food-item .portion {
  color: #999;
  font-size: 12px;
  padding: 2px 8px;
  background: #f5f5f5;
  border-radius: 4px;
}

.meal-food-item .calories {
  color: #667eea;
  font-weight: 600;
  font-size: 13px;
}

.empty-meal {
  padding: 12px 16px;
  color: #ccc;
  font-size: 13px;
  text-align: center;
  background: #fafafa;
  border-radius: 6px;
  border: 1px dashed #e0e0e0;
}

.exercise-content {
  min-height: 400px;
}

.exercise-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.exercise-item {
  display: flex;
  justify-content: space-between;
  padding: 12px;
  background: #f9fafb;
  border-radius: 12px;
}

.exercise-info {
  flex: 1;
}

.exercise-type {
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.exercise-detail {
  font-size: 13px;
  color: #999;
}

.exercise-image {
  width: 80px;
  height: 80px;
  border-radius: 8px;
}

.water-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
  padding: 20px 0;
}

.progress-text {
  text-align: center;
}

.progress-text .amount {
  font-size: 32px;
  font-weight: 600;
  color: #409eff;
}

.progress-text .unit {
  font-size: 14px;
  color: #999;
}

.water-actions {
  display: flex;
  gap: 12px;
}

.sleep-content {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px 0;
  min-height: 200px;
}

.sleep-info {
  text-align: center;
  width: 100%;
}

.sleep-duration {
  margin-bottom: 16px;
}

.duration-value {
  font-size: 48px;
  font-weight: 600;
  color: #333;
}

.duration-unit {
  font-size: 14px;
  color: #999;
  margin-top: 8px;
}

.sleep-time-range {
  display: inline-flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin: 16px auto;
  padding: 10px 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.time-item {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.time-label {
  font-size: 12px;
  color: #909399;
}

.time-value {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.time-separator {
  font-size: 14px;
  color: #909399;
  padding: 0 4px;
}

.sleep-quality {
  margin-top: 12px;
}
</style>
