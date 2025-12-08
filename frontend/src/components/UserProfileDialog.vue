<template>
  <el-dialog
    v-model="dialogVisible"
    :title="profileData?.user_info?.nickname || '用户详情'"
    width="90%"
    :before-close="handleClose"
    class="user-profile-dialog"
  >
    <div v-loading="loading" class="profile-container">
      <template v-if="profileData">
        <!-- 用户信息卡片 -->
        <div class="user-card">
          <el-avatar :size="100" :src="profileData.user_info.avatar || defaultAvatar" class="avatar" />
          <div class="user-details">
            <h2 class="username">{{ profileData.user_info.nickname || '用户' }}</h2>
            <div class="user-stats-grid">
              <div class="stat-box">
                <div class="stat-label">年龄</div>
                <div class="stat-value">{{ profileData.user_info.age || '-' }}</div>
              </div>
              <div class="stat-box">
                <div class="stat-label">性别</div>
                <div class="stat-value">{{ profileData.user_info.gender === 'male' ? '男' : profileData.user_info.gender === 'female' ? '女' : '-' }}</div>
              </div>
              <div class="stat-box">
                <div class="stat-label">身高</div>
                <div class="stat-value">{{ profileData.user_info.height || '-' }}<span class="unit">cm</span></div>
              </div>
              <div class="stat-box">
                <div class="stat-label">初始体重</div>
                <div class="stat-value">{{ displayInitialWeight }}<span class="unit">{{ weightUnitText }}</span></div>
              </div>
              <div class="stat-box">
                <div class="stat-label">当前体重</div>
                <div class="stat-value highlight">{{ displayCurrentWeight }}<span class="unit">{{ weightUnitText }}</span></div>
              </div>
              <div class="stat-box">
                <div class="stat-label">目标体重</div>
                <div class="stat-value">{{ displayTargetWeight }}<span class="unit">{{ weightUnitText }}</span></div>
              </div>
              <div class="stat-box">
                <div class="stat-label">BMI</div>
                <div class="stat-value">{{ profileData.user_info.bmi ? profileData.user_info.bmi.toFixed(1) : '-' }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 减重进度卡片 -->
        <div class="progress-card" v-if="profileData.weight_progress">
          <div class="progress-item">
            <el-icon class="progress-icon" color="#667eea"><TrendCharts /></el-icon>
            <div class="progress-content">
              <div class="progress-label">已减重</div>
              <div class="progress-value">{{ profileData.weight_progress.weight_lost }}<span class="unit">斤</span></div>
            </div>
          </div>
          <div class="progress-item">
            <el-icon class="progress-icon" color="#764ba2"><Calendar /></el-icon>
            <div class="progress-content">
              <div class="progress-label">坚持天数</div>
              <div class="progress-value">{{ profileData.weight_progress.days_elapsed }}<span class="unit">天</span></div>
            </div>
          </div>
        </div>

        <!-- Tab 切换区域 -->
        <el-tabs v-model="activeTab" class="profile-tabs">
          <!-- 体重趋势 -->
          <el-tab-pane label="体重趋势" name="weight">
            <div class="chart-container" v-if="profileData.weight_data && profileData.weight_data.length > 0">
              <div ref="weightChartRef" style="width: 100%; height: 400px;"></div>
            </div>
            <el-empty v-else description="暂无体重数据" />
          </el-tab-pane>

          <!-- 饮食记录 -->
          <el-tab-pane label="饮食记录" name="diet">
            <div class="records-list" v-if="profileData.diet_records && profileData.diet_records.length > 0">
              <div class="record-item-day" v-for="dayRecord in profileData.diet_records" :key="dayRecord.date">
                <div class="day-header">
                  <span class="date">📅 {{ dayRecord.date }}</span>
                  <div class="day-summary">
                    <span class="meal-count">🍽️ {{ dayRecord.meal_count }} 餐</span>
                    <span class="total-calories">🔥 {{ dayRecord.total_calories }} kcal</span>
                  </div>
                </div>
                <div class="meals-detail">
                  <!-- 按餐次分组展示 -->
                  <div class="meal-group" v-for="mealGroup in dayRecord.meals" :key="mealGroup.meal_type">
                    <div class="meal-group-header">
                      <el-tag :type="getMealTypeTag(mealGroup.meal_type)" size="small">{{ getMealTypeName(mealGroup.meal_type) }}</el-tag>
                      <span class="meal-calories">🔥 {{ mealGroup.meal_calories.toFixed(1) }} kcal</span>
                    </div>
                    <div class="meal-foods">
                      <div class="food-item" v-for="(food, index) in mealGroup.foods" :key="index">
                        <span class="food-name">{{ food.food_name }}</span>
                        <span class="portion" v-if="food.portion">{{ food.portion }}</span>
                        <span class="calories">{{ food.calories }} kcal</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <el-empty v-else description="暂无饮食记录" />
          </el-tab-pane>

          <!-- 锻炼记录 -->
          <el-tab-pane label="锻炼记录" name="exercise">
            <div class="records-list" v-if="profileData.exercise_records && profileData.exercise_records.length > 0">
              <div class="record-item-day" v-for="dayRecord in profileData.exercise_records" :key="dayRecord.date">
                <div class="day-header">
                  <span class="date">📅 {{ dayRecord.date }}</span>
                  <div class="day-summary">
                    <span class="exercise-count">🏋️ {{ dayRecord.exercise_count }} 项</span>
                    <span class="total-duration">⏱️ {{ dayRecord.total_duration }} 分钟</span>
                    <span class="total-calories">🔥 {{ dayRecord.total_calories }} kcal</span>
                  </div>
                </div>
                <div class="exercises-detail">
                  <div class="exercise-item" v-for="(exercise, index) in dayRecord.exercises" :key="index">
                    <el-tag type="success" size="small">{{ exercise.exercise_type }}</el-tag>
                    <span class="duration">{{ exercise.duration }} 分钟</span>
                    <span class="calories">{{ exercise.calories }} kcal</span>
                    <span class="distance" v-if="exercise.distance > 0">{{ formatDistance(exercise.distance) }}</span>
                  </div>
                </div>
              </div>
            </div>
            <el-empty v-else description="暂无锻炼记录" />
          </el-tab-pane>
        </el-tabs>
      </template>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, watch, nextTick, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { TrendCharts, Calendar, Timer } from '@element-plus/icons-vue'
import request from '@/utils/request'
import * as echarts from 'echarts'
import { useSettingsStore } from '@/stores/settings'

const settingsStore = useSettingsStore()

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  userId: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['update:modelValue'])

const dialogVisible = ref(false)
const loading = ref(false)
const profileData = ref(null)
const activeTab = ref('weight')
const weightChartRef = ref(null)
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

let chartInstance = null

// 计算属性：转换后的体重显示
const displayInitialWeight = computed(() => {
  if (!profileData.value?.user_info?.initial_weight) return '-'
  return settingsStore.convertWeightToDisplay(profileData.value.user_info.initial_weight)
})

const displayCurrentWeight = computed(() => {
  if (!profileData.value?.user_info?.current_weight) return '-'
  return settingsStore.convertWeightToDisplay(profileData.value.user_info.current_weight)
})

const displayTargetWeight = computed(() => {
  if (!profileData.value?.user_info?.target_weight) return '-'
  return settingsStore.convertWeightToDisplay(profileData.value.user_info.target_weight)
})

const weightUnitText = computed(() => {
  return settingsStore.getWeightUnitText()
})

watch(() => props.modelValue, (val) => {
  dialogVisible.value = val
  if (val && props.userId) {
    fetchUserProfile()
  }
})

watch(dialogVisible, (val) => {
  emit('update:modelValue', val)
  if (!val) {
    // 关闭时清理图表
    if (chartInstance) {
      chartInstance.dispose()
      chartInstance = null
    }
  }
})

watch(activeTab, (val) => {
  if (val === 'weight' && profileData.value?.weight_data?.length > 0) {
    nextTick(() => {
      initWeightChart()
    })
  }
})

const fetchUserProfile = async () => {
  loading.value = true
  try {
    const response = await request.get(`/user/profile/${props.userId}`)
    profileData.value = response.data
    
    // 加载完成后，如果当前在体重标签，初始化图表
    if (activeTab.value === 'weight' && response.data.weight_data?.length > 0) {
      nextTick(() => {
        initWeightChart()
      })
    }
  } catch (error) {
    if (error.response?.status === 403) {
      ElMessage.error('该用户未公开数据，无法查看详情')
    } else {
      ElMessage.error('获取用户详情失败')
    }
    console.error(error)
    handleClose()
  } finally {
    loading.value = false
  }
}

const initWeightChart = () => {
  if (!weightChartRef.value || !profileData.value?.weight_data) return
  
  // 销毁旧实例
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  chartInstance = echarts.init(weightChartRef.value)
  
  const dates = profileData.value.weight_data.map(item => item.date)
  // 根据用户设置的单位转换体重数据
  const weights = profileData.value.weight_data.map(item => {
    const kgWeight = item.weight
    return settingsStore.weightUnit === 'jin' ? (kgWeight * 2) : kgWeight
  })
  
  const unitText = settingsStore.getWeightUnitText()
  
  const option = {
    title: {
      text: '最近30天体重变化',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 600
      }
    },
    tooltip: {
      trigger: 'axis',
      formatter: `{b}<br/>体重: {c} ${unitText}`
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: `体重(${unitText})`,
      scale: true,  // 不从0开始，根据数据范围自动缩放
      axisLabel: {
        formatter: `{value} ${unitText}`
      }
    },
    series: [{
      data: weights,
      type: 'line',
      smooth: true,
      itemStyle: {
        color: '#667eea'
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [{
            offset: 0,
            color: 'rgba(102, 126, 234, 0.3)'
          }, {
            offset: 1,
            color: 'rgba(102, 126, 234, 0.05)'
          }]
        }
      }
    }],
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    }
  }
  
  chartInstance.setOption(option)
}

const handleClose = () => {
  dialogVisible.value = false
}

const getMealTypeName = (type) => {
  const map = {
    breakfast: '早餐',
    lunch: '午餐',
    dinner: '晚餐',
    snack: '加餐'
  }
  return map[type] || type
}

const getMealTypeTag = (type) => {
  const map = {
    breakfast: 'warning',
    lunch: 'success',
    dinner: 'danger',
    snack: 'info'
  }
  return map[type] || ''
}

// 格式化距离显示：后端返回的是公里（km）
const formatDistance = (distanceInKm) => {
  if (!distanceInKm || distanceInKm === 0) return '0km'
  
  // 直接显示公里，保留2位小数
  return `${distanceInKm.toFixed(2)}km`
}
</script>

<style scoped>
.user-profile-dialog :deep(.el-dialog__body) {
  padding: 20px;
  max-height: 70vh;
  overflow-y: auto;
}

.profile-container {
  min-height: 400px;
}

/* 用户信息卡片 */
.user-card {
  display: flex;
  align-items: center;
  gap: 30px;
  padding: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  color: white;
  margin-bottom: 20px;
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
}

.user-card .avatar {
  border: 4px solid white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.user-details {
  flex: 1;
}

.username {
  font-size: 28px;
  font-weight: bold;
  margin: 0 0 20px 0;
}

.user-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 15px;
}

.stat-box {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  padding: 12px;
  border-radius: 12px;
  text-align: center;
}

.stat-label {
  font-size: 12px;
  opacity: 0.9;
  margin-bottom: 6px;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
}

.stat-value.highlight {
  color: #ffd700;
}

.stat-value .unit {
  font-size: 12px;
  margin-left: 4px;
  opacity: 0.8;
}

/* 减重进度卡片 */
.progress-card {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.progress-item {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background: white;
  border-radius: 16px;
  border: 2px solid #f0f0f0;
  transition: all 0.3s ease;
}

.progress-item:hover {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
  transform: translateY(-2px);
}

.progress-icon {
  font-size: 40px;
}

.progress-content {
  flex: 1;
}

.progress-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 6px;
}

.progress-value {
  font-size: 32px;
  font-weight: bold;
  color: #333;
}

.progress-value .unit {
  font-size: 16px;
  margin-left: 4px;
  color: #999;
}

/* Tab 样式 */
.profile-tabs {
  margin-top: 20px;
}

.profile-tabs :deep(.el-tabs__header) {
  margin-bottom: 20px;
}

.chart-container {
  padding: 20px;
  background: white;
  border-radius: 16px;
  border: 2px solid #f0f0f0;
}

/* 记录列表 */
.records-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 按天聚合的记录项 */
.record-item-day {
  padding: 16px;
  background: white;
  border-radius: 12px;
  border: 2px solid #f0f0f0;
  transition: all 0.3s ease;
}

.record-item-day:hover {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
}

.day-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 12px;
  margin-bottom: 12px;
  border-bottom: 2px solid #f0f0f0;
}

.day-header .date {
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

.day-summary {
  display: flex;
  gap: 15px;
  font-size: 13px;
}

.meal-count,
.exercise-count,
.total-duration {
  color: #666;
}

.total-calories {
  color: #667eea;
  font-weight: 600;
}

/* 饮食明细 */
.meals-detail {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.meal-group {
  background: #f8f9ff;
  border-radius: 8px;
  padding: 10px;
}

.meal-group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  padding-bottom: 6px;
  border-bottom: 1px dashed #e0e0e0;
}

.meal-calories {
  font-size: 13px;
  color: #667eea;
  font-weight: 600;
}

.meal-foods {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.food-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 10px;
  background: white;
  border-radius: 6px;
  font-size: 14px;
}

.food-item .food-name {
  flex: 1;
  font-weight: 500;
  color: #333;
}

.food-item .portion {
  font-size: 12px;
  color: #999;
  padding: 2px 8px;
  background: #f0f0f0;
  border-radius: 4px;
}

.food-item .calories {
  color: #667eea;
  font-weight: 600;
  font-size: 13px;
}

/* 锻炼明细 */
.exercises-detail {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.exercise-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: #f0fdf4;
  border-radius: 8px;
  font-size: 14px;
}

.exercise-item .duration,
.exercise-item .distance {
  color: #666;
}

.exercise-item .calories {
  color: #10b981;
  font-weight: 600;
}

/* 旧样式保留（兼容） */
.record-item {
  padding: 16px;
  background: white;
  border-radius: 12px;
  border: 2px solid #f0f0f0;
  transition: all 0.3s ease;
}

.record-item:hover {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.record-date {
  font-size: 12px;
  color: #999;
}

.record-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.food-name,
.exercise-info {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  display: flex;
  align-items: center;
  gap: 6px;
}

.calories {
  font-size: 14px;
  font-weight: bold;
  color: #667eea;
}

.record-note {
  font-size: 12px;
  color: #666;
  padding-top: 8px;
  border-top: 1px dashed #f0f0f0;
}

/* 响应式 */
@media (max-width: 768px) {
  .user-card {
    flex-direction: column;
    text-align: center;
  }
  
  .user-stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .progress-card {
    flex-direction: column;
  }
}
</style>
