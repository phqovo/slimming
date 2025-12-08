<template>
  <div class="nutrition-analysis">
    <div class="header-section">
      <h1 class="page-title">成分分析</h1>
      <el-date-picker
        v-model="selectedDate"
        type="date"
        placeholder="选择日期"
        :clearable="false"
        :disabledDate="disabledDate"
        @change="handleDateChange"
        style="width: 200px"
      />
    </div>
    
    <!-- 人物模型和营养概览 -->
    <div class="overview-section">
      <div class="model-container">
        <div class="human-model">
          <div class="head"></div>
          <div class="body">
            <div class="organ organ-protein" title="蛋白质"></div>
            <div class="organ organ-carbs" title="碳水化合物"></div>
            <div class="organ organ-fat" title="脂肪"></div>
          </div>
          <div class="legs">
            <div class="leg"></div>
            <div class="leg"></div>
          </div>
        </div>
      </div>
      
      <div class="nutrition-summary">
        <h2>{{ isToday ? '今日' : selectedDateText }}营养摄入</h2>
        <div class="summary-stats">
          <div class="stat-item">
            <div class="stat-value">{{ summary.total_calories }}<span class="unit">千卡</span></div>
            <div class="stat-label">总热量</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ summary.total_protein }}<span class="unit">g</span></div>
            <div class="stat-label">蛋白质</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ summary.total_carbs }}<span class="unit">g</span></div>
            <div class="stat-label">碳水</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ summary.total_fat }}<span class="unit">g</span></div>
            <div class="stat-label">脂肪</div>
          </div>
        </div>
        
        <!-- 热量缺口信息 -->
        <div class="calories-info">
          <div class="info-row">
            <span class="info-label">基础代谢：</span>
            <span class="info-value">{{ summary.bmr }} 千卡</span>
          </div>
          <div class="info-row">
            <span class="info-label">运动消耗：</span>
            <span class="info-value">{{ summary.exercise_calories }} 千卡</span>
          </div>
          <div class="info-row">
            <span class="info-label">总能量消耗（TDEE）：</span>
            <span class="info-value">{{ summary.tdee }} 千卡</span>
          </div>
          <div class="info-row">
            <span class="info-label">饮食摄入：</span>
            <span class="info-value">{{ summary.total_calories }} 千卡</span>
          </div>
          <div class="info-row">
            <span class="info-label">推荐热量缺口：</span>
            <span class="info-value">{{ summary.calorie_deficit }} 千卡</span>
          </div>
          <div class="info-row">
            <span class="info-label">推荐摄入：</span>
            <span class="info-value">{{ summary.recommended_intake }} 千卡</span>
          </div>
          <div class="info-row highlight">
            <span class="info-label">{{ caloriesRemainingLabel }}</span>
            <span class="info-value" :class="getCaloriesRemainingClass">
              {{ caloriesRemainingValue }} 千卡
            </span>
          </div>
        </div>
        
        <div class="macro-chart">
          <div class="chart-container">
            <div class="chart-segment protein" :style="{ width: summary.protein_ratio + '%' }"></div>
            <div class="chart-segment carbs" :style="{ width: summary.carbs_ratio + '%' }"></div>
            <div class="chart-segment fat" :style="{ width: summary.fat_ratio + '%' }"></div>
          </div>
          <div class="chart-legend">
            <div class="legend-item">
              <div class="legend-color protein"></div>
              <span>蛋白质 {{ summary.protein_ratio }}%</span>
            </div>
            <div class="legend-item">
              <div class="legend-color carbs"></div>
              <span>碳水化合物 {{ summary.carbs_ratio }}%</span>
            </div>
            <div class="legend-item">
              <div class="legend-color fat"></div>
              <span>脂肪 {{ summary.fat_ratio }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 详细营养成分 -->
    <div class="detail-section">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="营养摄入" name="intake">
          <div class="intake-grid">
            <div class="intake-card" v-for="item in nutritionData" :key="item.name">
              <div class="intake-header">
                <h3>{{ item.name }}</h3>
                <div class="intake-amount">{{ item.current }}/{{ item.target }}{{ item.unit }}</div>
              </div>
              <div class="intake-progress">
                <el-progress 
                  :percentage="Math.min(100, Math.round((item.current / item.target) * 100))" 
                  :stroke-width="12"
                  :color="getProgressColor(item.current, item.target)"
                />
              </div>
              <div class="intake-footer">
                <span :class="getStatusLabel(item.current, item.target)">
                  {{ getStatusText(item.current, item.target) }}
                </span>
              </div>
            </div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="热量分布" name="distribution">
          <div class="distribution-chart">
            <div class="chart-wrapper">
              <canvas ref="distributionChart"></canvas>
            </div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="营养建议" name="recommendation">
          <div class="recommendation-content">
            <div class="recommendation-card" v-for="tip in recommendations" :key="tip.title">
              <h3>{{ tip.title }}</h3>
              <p>{{ tip.content }}</p>
              <div class="tip-tag" :class="tip.type">{{ tip.type === 'good' ? '✓' : '!' }}</div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { Chart, registerables } from 'chart.js'
import { getNutritionAnalysis } from '@/api/nutrition'
import { ElMessage } from 'element-plus'

Chart.register(...registerables)

export default {
  name: 'NutritionAnalysis',
  setup() {
    const selectedDate = ref(new Date())
    const nutritionData = ref([])
    const recommendations = ref([])
    const summary = ref({
      total_calories: 0,
      exercise_calories: 0,
      calories_remaining: 0,
      bmr: 0,
      tdee: 0,
      recommended_intake: 0,
      calorie_deficit: 500,
      protein_ratio: 0,
      carbs_ratio: 0,
      fat_ratio: 0,
      total_protein: 0,
      total_carbs: 0,
      total_fat: 0
    })
    
    const activeTab = ref('intake')
    const distributionChart = ref(null)
    const loading = ref(false)
    
    // 是否是今天
    const isToday = computed(() => {
      const today = new Date()
      const selected = new Date(selectedDate.value)
      return today.toDateString() === selected.toDateString()
    })
    
    // 选中日期文本
    const selectedDateText = computed(() => {
      return selectedDate.value.toLocaleDateString('zh-CN', { month: 'long', day: 'numeric' })
    })
    
    // 热量剩余样式
    const getCaloriesRemainingClass = computed(() => {
      if (summary.value.calories_remaining > 0) return 'positive'
      if (summary.value.calories_remaining < 0) return 'negative'
      return ''
    })
    
    // 热量剩余文案
    const caloriesRemainingLabel = computed(() => {
      return summary.value.calories_remaining >= 0 ? '还能摄入：' : '已超出：'
    })
    
    // 热量剩余数值（显示绝对值）
    const caloriesRemainingValue = computed(() => {
      return Math.abs(summary.value.calories_remaining)
    })
    
    // 计算进度条颜色
    const getProgressColor = (current, target) => {
      const percentage = (current / target) * 100
      if (percentage < 50) return '#f56c6c'
      if (percentage < 80) return '#e6a23c'
      if (percentage <= 100) return '#67c23a'
      return '#409eff'
    }
    
    // 获取状态文本
    const getStatusText = (current, target) => {
      const percentage = (current / target) * 100
      if (percentage < 50) return '不足'
      if (percentage < 80) return '接近目标'
      if (percentage <= 100) return '达标'
      return '超标'
    }
    
    // 获取状态标签类名
    const getStatusLabel = (current, target) => {
      const percentage = (current / target) * 100
      if (percentage < 50) return 'status-low'
      if (percentage < 80) return 'status-medium'
      if (percentage <= 100) return 'status-good'
      return 'status-over'
    }
    
    // 禁用未来日期
    const disabledDate = (time) => {
      return time.getTime() > Date.now()
    }
    
    // 格式化日期（使用本地时区，避免时区问题）
    const formatDate = (date) => {
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    }
    
    // 加载营养分析数据
    const loadNutritionData = async () => {
      loading.value = true
      try {
        const dateStr = formatDate(selectedDate.value)
        const response = await getNutritionAnalysis({ analysis_date: dateStr })
        
        summary.value = response.summary
        nutritionData.value = response.nutrition_data
        recommendations.value = response.recommendations
        
        // 重新渲染图表
        setTimeout(() => initChart(), 100)
      } catch (error) {
        console.error('加载营养分析失败:', error)
        ElMessage.error('加载营养分析失败')
      } finally {
        loading.value = false
      }
    }
    
    // 日期变化
    const handleDateChange = () => {
      loadNutritionData()
    }
    
    // 初始化图表
    let chartInstance = null
    const initChart = () => {
      if (!distributionChart.value) return
      
      // 销毁旧图表
      if (chartInstance) {
        chartInstance.destroy()
      }
      
      const ctx = distributionChart.value.getContext('2d')
      chartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['蛋白质', '碳水化合物', '脂肪'],
          datasets: [{
            data: [summary.value.protein_ratio, summary.value.carbs_ratio, summary.value.fat_ratio],
            backgroundColor: [
              '#409eff',
              '#67c23a',
              '#e6a23c'
            ],
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'right',
              labels: {
                padding: 20,
                usePointStyle: true,
                pointStyle: 'circle'
              }
            }
          },
          cutout: '70%'
        }
      })
    }
    
    onMounted(() => {
      loadNutritionData()
    })
    
    return {
      selectedDate,
      isToday,
      selectedDateText,
      summary,
      nutritionData,
      recommendations,
      activeTab,
      distributionChart,
      loading,
      disabledDate,
      getCaloriesRemainingClass,
      caloriesRemainingLabel,
      caloriesRemainingValue,
      handleDateChange,
      getProgressColor,
      getStatusText,
      getStatusLabel
    }
  }
}
</script>

<style scoped>
.nutrition-analysis {
  padding: 20px;
  min-height: calc(100vh - 120px);
  background-color: #f5f7fa;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
  color: #303133;
}

.overview-section {
  display: flex;
  gap: 30px;
  margin-bottom: 30px;
  background: linear-gradient(to bottom, #f8f9ff 0%, #ffffff 100%);
  border-radius: 16px;
  padding: 30px;
  color: #303133;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.model-container {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

.human-model {
  position: relative;
  width: 120px;
  height: 300px;
}

.head {
  width: 60px;
  height: 60px;
  background: #ffd700;
  border-radius: 50%;
  margin: 0 auto 10px;
}

.body {
  width: 100px;
  height: 120px;
  background: #ffd700;
  margin: 0 auto;
  position: relative;
  border-radius: 10px;
}

.organ {
  position: absolute;
  border-radius: 50%;
  opacity: 0.8;
}

.organ-protein {
  width: 30px;
  height: 30px;
  background: #409eff;
  top: 20px;
  left: 20px;
}

.organ-carbs {
  width: 40px;
  height: 40px;
  background: #67c23a;
  top: 50px;
  right: 15px;
}

.organ-fat {
  width: 35px;
  height: 35px;
  background: #e6a23c;
  bottom: 20px;
  left: 30px;
}

.legs {
  display: flex;
  justify-content: space-around;
  width: 100px;
  margin: 10px auto 0;
}

.leg {
  width: 20px;
  height: 80px;
  background: #ffd700;
  border-radius: 5px;
}

.nutrition-summary {
  flex: 2;
}

.nutrition-summary h2 {
  font-size: 20px;
  margin-bottom: 20px;
  color: #303133;
  font-weight: 600;
}

/* 热量缺口信息 */
.calories-info {
  background: #f5f7fa;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid #e4e7ed;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-size: 14px;
  color: #606266;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-row.highlight {
  padding-top: 10px;
  margin-top: 10px;
  border-top: 1px solid #e4e7ed;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.info-label {
  opacity: 0.9;
}

.info-value {
  font-weight: 600;
}

.info-value.positive {
  color: #67c23a;
}

.info-value.negative {
  color: #f56c6c;
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
  margin-bottom: 25px;
}

.stat-item {
  text-align: center;
  padding: 15px;
  background: rgba(245, 247, 250, 0.5);
  border-radius: 12px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 5px;
  color: #303133;
}

.unit {
  font-size: 14px;
  color: #909399;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.macro-chart {
  background: #f5f7fa;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e4e7ed;
}

.chart-container {
  height: 20px;
  background: #e4e7ed;
  border-radius: 10px;
  display: flex;
  overflow: hidden;
  margin-bottom: 15px;
}

.chart-segment {
  height: 100%;
}

.chart-segment.protein {
  background: #409eff;
}

.chart-segment.carbs {
  background: #67c23a;
}

.chart-segment.fat {
  background: #e6a23c;
}

.chart-legend {
  display: flex;
  justify-content: space-around;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-color.protein {
  background: #409eff;
}

.legend-color.carbs {
  background: #67c23a;
}

.legend-color.fat {
  background: #e6a23c;
}

.detail-section {
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  padding: 20px;
}

.intake-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.intake-card {
  border: 1px solid #ebeef5;
  border-radius: 16px;
  padding: 20px;
  transition: all 0.3s;
}

.intake-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
}

.intake-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.intake-header h3 {
  font-size: 16px;
  font-weight: 500;
  margin: 0;
  color: #303133;
}

.intake-amount {
  font-size: 14px;
  color: #909399;
}

.intake-progress {
  margin-bottom: 15px;
}

.intake-footer {
  text-align: right;
}

.status-low {
  color: #f56c6c;
  font-weight: 500;
}

.status-medium {
  color: #e6a23c;
  font-weight: 500;
}

.status-good {
  color: #67c23a;
  font-weight: 500;
}

.status-over {
  color: #409eff;
  font-weight: 500;
}

.distribution-chart {
  height: 400px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.chart-wrapper {
  width: 300px;
  height: 300px;
}

.recommendation-content {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.recommendation-card {
  border: 1px solid #ebeef5;
  border-radius: 16px;
  padding: 20px;
  position: relative;
  background: #f9f9f9;
}

.recommendation-card h3 {
  font-size: 16px;
  margin-bottom: 10px;
  color: #303133;
}

.recommendation-card p {
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
  margin-bottom: 20px;
}

.tip-tag {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: white;
}

.tip-tag.good {
  background: #67c23a;
}

.tip-tag.warning {
  background: #e6a23c;
}
</style>