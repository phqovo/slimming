<template>
  <div class="trend-container">
    <el-card class="rounded-card" shadow="never">
      <template #header>
        <div class="card-header">
          <h3>体重趋势分析</h3>
          <div class="header-actions">
            <el-button type="primary" @click="showAddDialog = true">
              <el-icon><Plus /></el-icon>
              添加记录
            </el-button>
          </div>
        </div>
      </template>

      <!-- 预测控制 -->
      <div class="predict-controls">
        <div class="predict-left">
          <span>预测未来：</span>
          <el-radio-group v-model="predictDays" @change="handlePredictDaysChange">
            <el-radio-button :label="7">7天</el-radio-button>
            <el-radio-button :label="30">30天</el-radio-button>
            <el-radio-button :label="90">90天</el-radio-button>
            <el-radio-button :label="-1">自定义</el-radio-button>
          </el-radio-group>
          <el-input-number
            v-if="predictDays === -1"
            v-model="customPredictDays"
            :min="1"
            :max="365"
            :step="1"
            size="small"
            placeholder="输入天数"
            style="width: 120px; margin-left: 12px"
          />
          <el-button 
            type="primary" 
            size="small" 
            @click="loadPrediction" 
            :loading="predicting"
            style="margin-left: 12px"
          >
            生成预测
          </el-button>
        </div>
        <div v-if="predictions.length > 0" class="predict-result-card">
          <div class="predict-result-content">
            <div class="predict-days">
              <span class="days-number">{{ actualPredictedDays }}</span>
              <span class="days-text">天后</span>
            </div>
            <div class="predict-weight">
              <span class="weight-label">体重预计</span>
              <span class="weight-value">{{ predictedWeight }}</span>
              <span class="weight-unit">{{ settingsStore.getWeightUnitText() }}</span>
            </div>
            <div v-if="weightChangePredict !== null" class="predict-change" :class="weightChangePredict >= 0 ? 'increase' : 'decrease'">
              <el-icon class="change-arrow" :class="weightChangePredict >= 0 ? 'arrow-up' : 'arrow-down'">
                <ArrowUp v-if="weightChangePredict >= 0" />
                <ArrowDown v-else />
              </el-icon>
              <span class="change-value">{{ Math.abs(weightChangePredict) }}</span>
              <span class="change-unit">{{ settingsStore.getWeightUnitText() }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 图表 -->
      <div class="chart-container">
        <div ref="chartRef" style="width: 100%; height: 500px;"></div>
      </div>

      <!-- 统计信息 -->
      <div class="stats-info">
        <el-row :gutter="24">
          <el-col :span="6">
            <div class="stat-card">
              <div class="stat-label">最高体重</div>
              <div class="stat-value">{{ maxWeight }} <span>{{ settingsStore.getWeightUnitText() }}</span></div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-card">
              <div class="stat-label">最低体重</div>
              <div class="stat-value">{{ minWeight }} <span>{{ settingsStore.getWeightUnitText() }}</span></div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-card">
              <div class="stat-label">当前体重</div>
              <div class="stat-value">{{ currentWeight }} <span>{{ settingsStore.getWeightUnitText() }}</span></div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-card">
              <div class="stat-label">体重变化</div>
              <div class="stat-value" :class="weightChange >= 0 ? 'positive' : 'negative'">
                {{ weightChange > 0 ? '+' : '' }}{{ weightChange }} <span>{{ settingsStore.getWeightUnitText() }}</span>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <!-- 历史记录列表 -->
    <el-card class="rounded-card history-card" shadow="never">
      <template #header>
        <h3>历史记录</h3>
      </template>
      
      <el-table :data="paginatedRecords" stripe style="width: 100%">
        <el-table-column prop="record_date" label="日期" width="120" />
        <el-table-column prop="morning_weight" :label="`早晨体重(${settingsStore.getWeightUnitText()})`" width="120">
          <template #default="{ row }">
            {{ row.morning_weight ? settingsStore.convertWeightToDisplay(row.morning_weight) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="evening_weight" :label="`睡前体重(${settingsStore.getWeightUnitText()})`" width="120">
          <template #default="{ row }">
            {{ row.evening_weight ? settingsStore.convertWeightToDisplay(row.evening_weight) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="weight" :label="`体重(${settingsStore.getWeightUnitText()})`" width="120">
          <template #default="{ row }">
            {{ settingsStore.convertWeightToDisplay(row.weight) }}
          </template>
        </el-table-column>
        <el-table-column prop="note" label="备注" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="danger" text size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadRecords"
          @current-change="loadRecords"
        />
      </div>
    </el-card>

    <!-- 对话框 -->
    <WeightDialog v-model="showAddDialog" @success="handleSuccess" />
    <EditWeightDialog v-model="showEditDialog" :record="currentRecord" @success="handleSuccess" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { getWeightRecords, predictWeightTrend, deleteWeightRecord } from '@/api/weight'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, ArrowUp, ArrowDown } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import WeightDialog from '@/components/WeightDialog.vue'
import EditWeightDialog from '@/components/EditWeightDialog.vue'

const settingsStore = useSettingsStore()
const chartRef = ref(null)
let chartInstance = null

const records = ref([]) // 用于图表展示的所有数据
const paginatedRecords = ref([]) // 用于表格分页展示的数据
const predictions = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const predictDays = ref(7)
const customPredictDays = ref(15) // 自定义天数默认值
const actualPredictedDays = ref(7) // 实际已生成预测的天数
const predicting = ref(false)

const showAddDialog = ref(false)
const showEditDialog = ref(false)
const currentRecord = ref(null)

// 统计数据（基于所有数据）
const maxWeight = computed(() => {
  if (!records.value.length) return 0
  const max = Math.max(...records.value.map(r => r.weight))
  return settingsStore.convertWeightToDisplay(max)
})

const minWeight = computed(() => {
  if (!records.value.length) return 0
  const min = Math.min(...records.value.map(r => r.weight))
  return settingsStore.convertWeightToDisplay(min)
})

const currentWeight = computed(() => {
  if (!records.value.length) return 0
  // 获取最近一天的体重
  const sorted = [...records.value].sort((a, b) => 
    new Date(b.record_date) - new Date(a.record_date)
  )
  return settingsStore.convertWeightToDisplay(sorted[0].weight)
})

// 预测结果统计
const predictedWeight = computed(() => {
  if (!predictions.value.length) return 0
  // 获取最后一天的预测体重
  const lastPrediction = predictions.value[predictions.value.length - 1]
  return settingsStore.convertWeightToDisplay(lastPrediction.predicted_weight)
})

const weightChangePredict = computed(() => {
  if (!predictions.value.length || !records.value.length) return null
  // 当前体重与预测体重的变化
  const sorted = [...records.value].sort((a, b) => 
    new Date(b.record_date) - new Date(a.record_date)
  )
  const currentW = settingsStore.convertWeightToDisplay(sorted[0].weight)
  const predictW = settingsStore.convertWeightToDisplay(predictions.value[predictions.value.length - 1].predicted_weight)
  const change = predictW - currentW
  return parseFloat(change.toFixed(2))
})

const weightChange = computed(() => {
  if (records.value.length < 2) return 0
  const sorted = [...records.value].sort((a, b) => 
    new Date(a.record_date) - new Date(b.record_date)
  )
  const first = sorted[0].weight
  const last = sorted[sorted.length - 1].weight
  const change = last - first
  // 转换为显示单位后计算变化（考虑正负号）
  const changeInDisplay = settingsStore.convertWeightToDisplay(last) - settingsStore.convertWeightToDisplay(first)
  // 处理浮点数精度问题，保留2位小数
  return parseFloat(changeInDisplay.toFixed(2))
})

// 加载记录
const loadRecords = async () => {
  try {
    // 获取所有数据用于图表展示
    const allData = await getWeightRecords({ all_records: true })
    records.value = allData || []
    total.value = allData?.length || 0
    
    // 获取当前页数据用于表格展示
    const skip = (currentPage.value - 1) * pageSize.value
    const pageData = await getWeightRecords({ skip, limit: pageSize.value })
    paginatedRecords.value = pageData || []
    
    await nextTick()
    renderChart()
  } catch (error) {
    console.error('加载记录失败:', error)
  }
}

// 处理预测天数变化
const handlePredictDaysChange = (value) => {
  if (value !== -1) {
    // 选择了预设天数，自动生成预测
    loadPrediction()
  }
}

// 加载预测
const loadPrediction = async () => {
  try {
    predicting.value = true
    
    // 确定实际预测天数
    const actualDays = predictDays.value === -1 ? customPredictDays.value : predictDays.value
    
    if (!actualDays || actualDays < 1) {
      ElMessage.warning('请输入有效的预测天数')
      return
    }
    
    const res = await predictWeightTrend(actualDays)
    console.log('预测响应:', res)
    predictions.value = res.data || []
    console.log('预测数据:', predictions.value)
    
    // 只有在成功生成预测后才更新实际预测天数
    actualPredictedDays.value = actualDays
    
    await nextTick()
    renderChart()
    
    ElMessage.success('预测生成成功')
  } catch (error) {
    console.error('预测失败:', error)
    ElMessage.error('预测失败，请确保有足够的历史数据')
  } finally {
    predicting.value = false
  }
}

// 渲染图表
const renderChart = () => {
  if (!chartRef.value) return

  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }

  // 准备历史数据（体重需要转换为显示单位）
  const sortedRecords = [...records.value].sort((a, b) => 
    new Date(a.record_date) - new Date(b.record_date)
  )
  
  const dates = sortedRecords.map(r => r.record_date)
  const weights = sortedRecords.map(r => parseFloat(settingsStore.convertWeightToDisplay(r.weight)))
  
  // 计算体重坐标轴范围
  const minWeightValue = Math.min(...weights)
  const maxWeightValue = Math.max(...weights)
  // 为了避免折线太平，调整范围
  const weightRange = maxWeightValue - minWeightValue
  const padding = weightRange * 0.1 // 上下各留10%的空间
  const yAxisMin = Math.floor((minWeightValue - padding) * 10) / 10
  const yAxisMax = Math.ceil((maxWeightValue + padding) * 10) / 10

  // 准备预测数据（体重需要转换为显示单位）
  const predictionDates = predictions.value.map(p => p.date)
  const predictionWeights = predictions.value.map(p => parseFloat(settingsStore.convertWeightToDisplay(p.predicted_weight)))
  const upperBounds = predictions.value.map(p => parseFloat(settingsStore.convertWeightToDisplay(p.confidence_interval_upper)))
  const lowerBounds = predictions.value.map(p => parseFloat(settingsStore.convertWeightToDisplay(p.confidence_interval_lower)))
  
  // 计算置信区间带宽（处理浮点数精度）
  const confidenceBands = upperBounds.map((upper, i) => {
    const lower = lowerBounds[i]
    const bandwidth = parseFloat((upper - lower).toFixed(2))
    return bandwidth
  })

  // 重新计算Y轴范围（需要包含预测数据）
  let finalYAxisMin = yAxisMin
  let finalYAxisMax = yAxisMax
  if (predictionWeights.length > 0) {
    const allWeights = [...weights, ...predictionWeights, ...upperBounds, ...lowerBounds]
    const minAll = Math.min(...allWeights)
    const maxAll = Math.max(...allWeights)
    const rangeAll = maxAll - minAll
    const paddingAll = rangeAll * 0.1
    finalYAxisMin = Math.floor((minAll - paddingAll) * 10) / 10
    finalYAxisMax = Math.ceil((maxAll + paddingAll) * 10) / 10
  }

  const option = {
    title: {
      text: '体重变化趋势',
      left: 'center',
      textStyle: {
        fontSize: 18,
        fontWeight: 600
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['体重', '预测体重', '置信区间'],
      top: 40
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: 80,
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: [...dates, ...predictionDates],
      axisLine: {
        lineStyle: {
          color: '#ccc'
        }
      }
    },
    yAxis: [
      {
        type: 'value',
        name: `体重(${settingsStore.getWeightUnitText()})`,
        position: 'left',
        min: finalYAxisMin,
        max: finalYAxisMax,
        axisLine: {
          lineStyle: {
            color: '#5470c6'
          }
        }
      }
    ],
    series: [
      {
        name: '体重',
        type: 'line',
        data: [...weights, ...Array(predictionDates.length).fill(null)],
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        itemStyle: {
          color: '#5470c6'
        },
        lineStyle: {
          width: 3
        }
      },

      {
        name: '预测体重',
        type: 'line',
        data: [...Array(dates.length).fill(null), ...predictionWeights],
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        itemStyle: {
          color: '#fac858'
        },
        lineStyle: {
          type: 'dashed',
          width: 2
        },
        yAxisIndex: 0
      },
      {
        name: '置信区间',
        type: 'line',
        data: [...Array(dates.length).fill(null), ...upperBounds],
        lineStyle: {
          opacity: 0
        },
        stack: 'confidence-band',
        symbol: 'none',
        yAxisIndex: 0
      },
      {
        name: '置信区间',
        type: 'line',
        data: [...Array(dates.length).fill(null), ...confidenceBands],
        lineStyle: {
          opacity: 0
        },
        areaStyle: {
          color: 'rgba(250, 200, 88, 0.2)'
        },
        stack: 'confidence-band',
        symbol: 'none',
        yAxisIndex: 0
      }
    ]
  }

  chartInstance.setOption(option)
}

// 编辑
const handleEdit = (row) => {
  currentRecord.value = row
  showEditDialog.value = true
}

// 删除
const handleDelete = (row) => {
  ElMessageBox.confirm('确定要删除这条记录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteWeightRecord(row.id)
      ElMessage.success('删除成功')
      loadRecords()
    } catch (error) {
      console.error('删除失败:', error)
    }
  }).catch(() => {})
}

// 成功回调
const handleSuccess = () => {
  loadRecords()
  predictions.value = []
}

onMounted(async () => {
  // 确保设置已加载完成
  if (!settingsStore.isLoaded) {
    await settingsStore.loadSettings()
  }
  
  loadRecords()
  
  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    chartInstance?.resize()
  })
})
</script>

<style scoped>
.trend-container {
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.predict-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 24px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
}

.predict-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.predict-result-card {
  background: linear-gradient(135deg, #e8eef7 0%, #f0edf9 100%);
  border-radius: 12px;
  padding: 12px 16px;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
  flex-shrink: 0;
  border: 1px solid rgba(102, 126, 234, 0.15);
}

.predict-result-content {
  display: flex;
  align-items: center;
  gap: 16px;
  color: #333;
}

.predict-days {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.days-number {
  font-size: 28px;
  font-weight: 700;
  line-height: 1;
  color: #667eea;
}

.days-text {
  font-size: 14px;
  color: #666;
}

.predict-weight {
  display: flex;
  align-items: center;
  gap: 8px;
  border-left: 1px solid rgba(102, 126, 234, 0.2);
  border-right: 1px solid rgba(102, 126, 234, 0.2);
  padding: 0 12px;
}

.weight-label {
  font-size: 12px;
  color: #999;
}

.weight-value {
  font-size: 22px;
  font-weight: 600;
  color: #667eea;
}

.weight-unit {
  font-size: 12px;
  color: #999;
}

.predict-change {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
}

.predict-change.increase {
  color: #f56c6c;
}

.predict-change.decrease {
  color: #67c23a;
}

.change-arrow {
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.change-arrow.arrow-up {
  color: #f56c6c;
}

.change-arrow.arrow-down {
  color: #67c23a;
}

.change-value {
  font-size: 18px;
}

.change-unit {
  font-size: 12px;
  color: #999;
}

.chart-container {
  margin-bottom: 24px;
}

.stats-info {
  padding: 24px;
  background: #f9fafb;
  border-radius: 12px;
}

.stat-card {
  text-align: center;
  padding: 16px;
  background: white;
  border-radius: 8px;
}

.stat-label {
  font-size: 14px;
  color: #999;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #333;
}

.stat-value span {
  font-size: 14px;
  font-weight: 400;
  color: #999;
  margin-left: 4px;
}

.stat-value.positive {
  color: #f56c6c;
}

.stat-value.negative {
  color: #67c23a;
}

.history-card {
  margin-top: 24px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
