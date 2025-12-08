<template>
  <div class="trend-page">
    <van-nav-bar title="数据趋势" />
    
    <!-- 时间范围选择 -->
    <van-dropdown-menu>
      <van-dropdown-item v-model="days" :options="dayOptions" @change="fetchData" />
    </van-dropdown-menu>

    <!-- 体重趋势图 -->
    <div class="chart-card">
      <div class="card-title">体重趋势</div>
      <div ref="weightChart" class="chart" style="height: 250px"></div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">当前体重</div>
        <div class="stat-value">{{ currentWeight || '--' }} <span class="unit">kg</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-label">目标体重</div>
        <div class="stat-value">{{ targetWeight || '--' }} <span class="unit">kg</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-label">已减重</div>
        <div class="stat-value" :class="weightLoss > 0 ? 'success' : ''">
          {{ weightLoss > 0 ? '-' : '' }}{{ Math.abs(weightLoss) }} <span class="unit">kg</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-label">距目标</div>
        <div class="stat-value">{{ remainWeight }} <span class="unit">kg</span></div>
      </div>
    </div>

    <!-- 热量趋势图 -->
    <div class="chart-card">
      <div class="card-title">热量趋势</div>
      <div ref="caloriesChart" class="chart" style="height: 250px"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { showToast } from 'vant'
import * as echarts from 'echarts'
import { getWeightTrend } from '@/api/weight'
import { getCaloriesTrend } from '@/api/home'

const days = ref(30)
const dayOptions = [
  { text: '最近7天', value: 7 },
  { text: '最近30天', value: 30 },
  { text: '最近90天', value: 90 }
]

const weightChart = ref(null)
const caloriesChart = ref(null)
const weightData = ref([])
const caloriesData = ref([])
const currentWeight = ref(null)
const targetWeight = ref(null)

// 计算已减重
const weightLoss = computed(() => {
  if (!weightData.value.length) return 0
  const first = weightData.value[0].weight
  const last = weightData.value[weightData.value.length - 1].weight
  return (first - last).toFixed(1)
})

// 距离目标
const remainWeight = computed(() => {
  if (!currentWeight.value || !targetWeight.value) return '--'
  return Math.abs(currentWeight.value - targetWeight.value).toFixed(1)
})

// 获取数据
const fetchData = async () => {
  try {
    // 获取体重趋势
    const weightRes = await getWeightTrend({ days: days.value })
    weightData.value = weightRes.data || []
    currentWeight.value = weightRes.current_weight
    targetWeight.value = weightRes.target_weight
    
    // 获取热量趋势
    const caloriesRes = await getCaloriesTrend({ days: days.value })
    caloriesData.value = caloriesRes.data || []
    
    // 绘制图表
    initWeightChart()
    initCaloriesChart()
  } catch (error) {
    showToast('获取数据失败')
  }
}

// 初始化体重趋势图
const initWeightChart = () => {
  if (!weightChart.value || !weightData.value.length) return
  
  const chart = echarts.init(weightChart.value)
  const dates = weightData.value.map(item => item.record_date)
  const weights = weightData.value.map(item => item.weight)
  
  const option = {
    grid: {
      left: '50',
      right: '20',
      top: '20',
      bottom: '30'
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        fontSize: 10,
        rotate: 30
      }
    },
    yAxis: {
      type: 'value',
      scale: true,
      axisLabel: {
        fontSize: 10
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
            offset: 0, color: 'rgba(102, 126, 234, 0.3)'
          }, {
            offset: 1, color: 'rgba(102, 126, 234, 0.05)'
          }]
        }
      }
    }]
  }
  
  chart.setOption(option)
}

// 初始化热量趋势图
const initCaloriesChart = () => {
  if (!caloriesChart.value || !caloriesData.value.length) return
  
  const chart = echarts.init(caloriesChart.value)
  const dates = caloriesData.value.map(item => item.date)
  const intake = caloriesData.value.map(item => item.intake)
  const consume = caloriesData.value.map(item => item.consume)
  
  const option = {
    grid: {
      left: '50',
      right: '20',
      top: '30',
      bottom: '30'
    },
    legend: {
      data: ['摄入', '消耗'],
      top: 0,
      textStyle: {
        fontSize: 11
      }
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        fontSize: 10,
        rotate: 30
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        fontSize: 10
      }
    },
    series: [
      {
        name: '摄入',
        data: intake,
        type: 'bar',
        itemStyle: {
          color: '#f5576c'
        }
      },
      {
        name: '消耗',
        data: consume,
        type: 'bar',
        itemStyle: {
          color: '#1989fa'
        }
      }
    ]
  }
  
  chart.setOption(option)
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.trend-page {
  min-height: 100vh;
  background: #f7f8fa;
  padding-bottom: 20px;
}

.chart-card {
  background: white;
  margin: 12px 16px;
  border-radius: 12px;
  padding: 16px;
}

.card-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 12px;
}

.chart {
  width: 100%;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin: 12px 16px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  text-align: center;
}

.stat-label {
  font-size: 13px;
  color: #969799;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #323233;
}

.stat-value.success {
  color: #07c160;
}

.unit {
  font-size: 14px;
  font-weight: normal;
  color: #969799;
}
</style>
