<template>
  <div class="external-data-container">
    <div class="header">
      <h2>三方数据查询</h2>
    </div>

    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="数据来源">
          <el-select v-model="filterForm.data_source" placeholder="请选择数据来源" style="width: 150px">
            <el-option label="小米运动健康" value="xiaomi_sport" />
          </el-select>
        </el-form-item>
        <el-form-item label="数据类型">
          <el-select v-model="filterForm.data_type" placeholder="请选择数据类型" style="width: 150px" @change="handleDataTypeChange">
            <el-option label="体重记录" value="weight" />
            <el-option label="睡眠记录" value="sleep" />
            <el-option label="锻炼记录" value="exercise" />
            <el-option label="运动步数" value="steps" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 260px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchDataList">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-table
      v-loading="loading"
      :data="dataList"
      style="width: 100%; margin-top: 20px"
      @row-dblclick="handleRowDblClick"
    >
      <!-- 睡眠记录列 -->
      <template v-if="filterForm.data_type === 'sleep'">
        <el-table-column prop="sleep_date" label="日期" width="120" />
        <el-table-column label="睡眠时段" width="300">
          <template #default="{ row }">
            {{ formatTime(row.start_time) }} ~ {{ formatTime(row.end_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="total_duration" label="总时长" width="150">
          <template #default="{ row }">
            {{ formatDuration(row.total_duration) }}
          </template>
        </el-table-column>
        <el-table-column prop="deep_sleep" label="深睡" width="130">
          <template #default="{ row }">
            {{ formatDuration(row.deep_sleep) }}
          </template>
        </el-table-column>
        <el-table-column prop="light_sleep" label="浅睡" width="130">
          <template #default="{ row }">
            {{ formatDuration(row.light_sleep) }}
          </template>
        </el-table-column>
        <el-table-column prop="rem_sleep" label="REM睡眠" width="130">
          <template #default="{ row }">
            {{ formatDuration(row.rem_sleep) }}
          </template>
        </el-table-column>
        <el-table-column prop="sleep_score" label="睡眠评分" width="100" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="danger" size="small" link @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </template>

      <!-- 锻炼记录列 -->
      <template v-else-if="filterForm.data_type === 'exercise'">
        <el-table-column prop="exercise_date" label="日期" width="120" />
        <el-table-column label="运动时段" width="300">
          <template #default="{ row }">
            {{ formatTime(row.start_time) }} ~ {{ formatTime(row.end_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="exercise_type_cn" label="运动类型" width="120" />
        <el-table-column prop="duration" label="时长" width="130">
          <template #default="{ row }">
            {{ formatDuration(row.duration) }}
          </template>
        </el-table-column>
        <el-table-column prop="distance" label="距离(米)" width="110">
          <template #default="{ row }">
            {{ row.distance ? row.distance.toFixed(0) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="calories" label="卡路里" width="100" />
        <el-table-column prop="steps" label="步数" width="100" />
        <el-table-column prop="avg_heart_rate" label="平均心率" width="100" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="danger" size="small" link @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </template>

      <!-- 体重记录列 -->
      <template v-else-if="filterForm.data_type === 'weight'">
        <el-table-column prop="measure_date" label="测量日期" width="120" />
        <el-table-column prop="measure_time" label="测量时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.measure_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="weight" label="体重(kg)" width="100" />
        <el-table-column prop="bmi" label="BMI" width="80" />
        <el-table-column prop="body_fat" label="体脂率(%)" width="100" />
        <el-table-column prop="fat_mass" label="脂肪量(kg)" width="110">
          <template #default="{ row }">
            {{ row.fat_mass ? row.fat_mass.toFixed(2) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="muscle_mass" label="肌肉量(kg)" width="110" />
        <el-table-column prop="bmr" label="基础代谢" width="100" />
        <el-table-column prop="body_score" label="身体评分" width="100" />
        <el-table-column prop="note" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="danger" size="small" link @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </template>

      <!-- 运动步数列 -->
      <template v-else-if="filterForm.data_type === 'steps'">
        <el-table-column prop="step_date" label="日期" width="120" />
        <el-table-column prop="steps" label="步数" width="120" />
        <el-table-column prop="distance" label="距离(米)" width="120">
          <template #default="{ row }">
            {{ row.distance ? row.distance.toFixed(0) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="calories" label="卡路里" width="120" />
        <el-table-column prop="active_time" label="活跃时长" width="150">
          <template #default="{ row }">
            {{ formatDuration(row.active_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="danger" size="small" link @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </template>

      <el-table-column prop="data_source" label="数据来源" width="120">
        <template #default="{ row }">
          <el-tag v-if="row.data_source === 'xiaomi_sport'" type="success" size="small">小米运动健康</el-tag>
          <span v-else>{{ row.data_source }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="同步时间" width="180">
        <template #default="{ row }">
          {{ formatDateTime(row.created_at) }}
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchDataList"
        @current-change="fetchDataList"
      />
    </div>

    <!-- 体重详情弹窗 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="体重数据详情"
      width="800px"
      :close-on-click-modal="false"
    >
      <div v-loading="detailLoading" class="detail-container">
        <div v-if="weightDetail" class="detail-content">
          <!-- 测量信息 -->
          <div class="detail-section">
            <h3 class="section-title">📅 测量信息</h3>
            <div class="info-grid">
              <div class="info-item">
                <span class="label">测量日期</span>
                <span class="value">{{ weightDetail.measure_date }}</span>
              </div>
              <div class="info-item">
                <span class="label">测量时间</span>
                <span class="value">{{ formatTime(weightDetail.measure_time) }}</span>
              </div>
            </div>
          </div>

          <!-- 基础指标 -->
          <div class="detail-section">
            <h3 class="section-title">📊 基础指标</h3>
            <div class="info-grid">
              <div class="info-item">
                <span class="label">体重</span>
                <span class="value primary">{{ weightDetail.weight }} kg</span>
              </div>
              <div class="info-item">
                <span class="label">BMI</span>
                <span class="value">{{ weightDetail.bmi || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">体脂率</span>
                <span class="value">{{ weightDetail.body_fat ? weightDetail.body_fat + '%' : '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">脂肪量</span>
                <span class="value warning">{{ weightDetail.fat_mass ? weightDetail.fat_mass + ' kg' : '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">肌肉量</span>
                <span class="value">{{ weightDetail.muscle_mass ? weightDetail.muscle_mass + ' kg' : '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">骨量</span>
                <span class="value">{{ weightDetail.bone_mass ? weightDetail.bone_mass + ' kg' : '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">水分</span>
                <span class="value">{{ weightDetail.water ? weightDetail.water + '%' : '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">蛋白质</span>
                <span class="value">{{ weightDetail.protein ? weightDetail.protein + '%' : '-' }}</span>
              </div>
            </div>
          </div>

          <!-- 健康指标 -->
          <div class="detail-section">
            <h3 class="section-title">❤️ 健康指标</h3>
            <div class="info-grid">
              <div class="info-item">
                <span class="label">基础代谢</span>
                <span class="value">{{ weightDetail.bmr ? weightDetail.bmr + ' kcal' : '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">内脏脂肪等级</span>
                <span class="value">{{ weightDetail.visceral_fat || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">身体年龄</span>
                <span class="value">{{ weightDetail.body_age ? weightDetail.body_age + ' 岁' : '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">身体评分</span>
                <span class="value success">{{ weightDetail.body_score || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">心率</span>
                <span class="value">{{ weightDetail.heart_rate ? weightDetail.heart_rate + ' bpm' : '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">腰臀比</span>
                <span class="value">{{ weightDetail.whr || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">推荐卡路里</span>
                <span class="value">{{ weightDetail.recommended_calories_intake ? weightDetail.recommended_calories_intake + ' kcal' : '-' }}</span>
              </div>
            </div>
          </div>

          <!-- 四肢数据 -->
          <div v-if="hasLimbData" class="detail-section">
            <h3 class="section-title">🦵 四肢数据</h3>
            
            <!-- 左上肢 -->
            <div v-if="hasLeftUpperLimbData" class="limb-section">
              <h4 class="limb-title">左上肢</h4>
              <div class="info-grid">
                <div class="info-item">
                  <span class="label">脂肪量</span>
                  <span class="value">{{ weightDetail.left_upper_limb_fat_mass ? weightDetail.left_upper_limb_fat_mass + ' kg' : '-' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">脂肪等级</span>
                  <span class="value">{{ getRankText(weightDetail.left_upper_limb_fat_rank) }}</span>
                </div>
                <div class="info-item">
                  <span class="label">肌肉量</span>
                  <span class="value">{{ weightDetail.left_upper_limb_muscle_mass ? weightDetail.left_upper_limb_muscle_mass + ' kg' : '-' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">肌肉等级</span>
                  <span class="value">{{ getRankText(weightDetail.left_upper_limb_muscle_rank) }}</span>
                </div>
              </div>
            </div>

            <!-- 右上肢 -->
            <div v-if="hasRightUpperLimbData" class="limb-section">
              <h4 class="limb-title">右上肢</h4>
              <div class="info-grid">
                <div class="info-item">
                  <span class="label">脂肪量</span>
                  <span class="value">{{ weightDetail.right_upper_limb_fat_mass ? weightDetail.right_upper_limb_fat_mass + ' kg' : '-' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">脂肪等级</span>
                  <span class="value">{{ getRankText(weightDetail.right_upper_limb_fat_rank) }}</span>
                </div>
                <div class="info-item">
                  <span class="label">肌肉量</span>
                  <span class="value">{{ weightDetail.right_upper_limb_muscle_mass ? weightDetail.right_upper_limb_muscle_mass + ' kg' : '-' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">肌肉等级</span>
                  <span class="value">{{ getRankText(weightDetail.right_upper_limb_muscle_rank) }}</span>
                </div>
              </div>
            </div>

            <!-- 左下肢 -->
            <div v-if="hasLeftLowerLimbData" class="limb-section">
              <h4 class="limb-title">左下肢</h4>
              <div class="info-grid">
                <div class="info-item">
                  <span class="label">脂肪量</span>
                  <span class="value">{{ weightDetail.left_lower_limb_fat_mass ? weightDetail.left_lower_limb_fat_mass + ' kg' : '-' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">脂肪等级</span>
                  <span class="value">{{ getRankText(weightDetail.left_lower_limb_fat_rank) }}</span>
                </div>
                <div class="info-item">
                  <span class="label">肌肉量</span>
                  <span class="value">{{ weightDetail.left_lower_limb_muscle_mass ? weightDetail.left_lower_limb_muscle_mass + ' kg' : '-' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">肌肉等级</span>
                  <span class="value">{{ getRankText(weightDetail.left_lower_limb_muscle_rank) }}</span>
                </div>
              </div>
            </div>

            <!-- 右下肢 -->
            <div v-if="hasRightLowerLimbData" class="limb-section">
              <h4 class="limb-title">右下肢</h4>
              <div class="info-grid">
                <div class="info-item">
                  <span class="label">脂肪量</span>
                  <span class="value">{{ weightDetail.right_lower_limb_fat_mass ? weightDetail.right_lower_limb_fat_mass + ' kg' : '-' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">脂肪等级</span>
                  <span class="value">{{ getRankText(weightDetail.right_lower_limb_fat_rank) }}</span>
                </div>
                <div class="info-item">
                  <span class="label">肌肉量</span>
                  <span class="value">{{ weightDetail.right_lower_limb_muscle_mass ? weightDetail.right_lower_limb_muscle_mass + ' kg' : '-' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">肌肉等级</span>
                  <span class="value">{{ getRankText(weightDetail.right_lower_limb_muscle_rank) }}</span>
                </div>
              </div>
            </div>

            <!-- 躯干 -->
            <div v-if="hasTrunkData" class="limb-section">
              <h4 class="limb-title">躯干</h4>
              <div class="info-grid">
                <div class="info-item">
                  <span class="label">脂肪量</span>
                  <span class="value">{{ weightDetail.trunk_fat_mass ? weightDetail.trunk_fat_mass + ' kg' : '-' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">脂肪等级</span>
                  <span class="value">{{ getRankText(weightDetail.trunk_fat_rank) }}</span>
                </div>
                <div class="info-item">
                  <span class="label">肌肉量</span>
                  <span class="value">{{ weightDetail.trunk_muscle_mass ? weightDetail.trunk_muscle_mass + ' kg' : '-' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">肌肉等级</span>
                  <span class="value">{{ getRankText(weightDetail.trunk_muscle_rank) }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 备注 -->
          <div v-if="weightDetail.note" class="detail-section">
            <h3 class="section-title">📝 备注</h3>
            <div class="note-content">{{ weightDetail.note }}</div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getExternalDataList, getWeightDetail, deleteExternalRecord } from '@/api/external-data'
import dayjs from 'dayjs'

const loading = ref(false)
const dataList = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const dateRange = ref([])

const filterForm = ref({
  data_source: 'xiaomi_sport',
  data_type: 'weight'  // 默认展示体重记录
})

// 详情弹窗
const detailDialogVisible = ref(false)
const detailLoading = ref(false)
const weightDetail = ref(null)

// 格式化时间
const formatTime = (time) => {
  if (!time) return '-'
  return dayjs(time).format('HH:mm:ss')
}

// 格式化日期时间
const formatDateTime = (time) => {
  if (!time) return '-'
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

// 格式化分钟数为小时+分钟
const formatDuration = (minutes) => {
  if (!minutes || minutes === 0) return '-'
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  
  if (hours > 0 && mins > 0) {
    return `${hours}小时${mins}分钟`
  } else if (hours > 0) {
    return `${hours}小时`
  } else {
    return `${mins}分钟`
  }
}

// 获取数据列表
const fetchDataList = async () => {
  if (!filterForm.value.data_type) {
    ElMessage.warning('请选择数据类型')
    return
  }

  loading.value = true
  try {
    const params = {
      data_type: filterForm.value.data_type,
      data_source: filterForm.value.data_source,
      page: currentPage.value,
      page_size: pageSize.value
    }

    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }

    const res = await getExternalDataList(params)
    dataList.value = res.items
    total.value = res.total
  } catch (error) {
    ElMessage.error('获取数据失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 数据类型改变
const handleDataTypeChange = () => {
  currentPage.value = 1
  fetchDataList()
}

// 重置
const handleReset = () => {
  dateRange.value = []
  currentPage.value = 1
  fetchDataList()
}

// 双击行查看详情
const handleRowDblClick = (row) => {
  // 只有体重记录支持查看详情
  if (filterForm.value.data_type === 'weight') {
    fetchWeightDetail(row.id)
  }
}

// 获取体重详情
const fetchWeightDetail = async (recordId) => {
  detailLoading.value = true
  detailDialogVisible.value = true
  
  try {
    const res = await getWeightDetail(recordId)
    weightDetail.value = res.data
  } catch (error) {
    ElMessage.error('获取详情失败')
    console.error(error)
    detailDialogVisible.value = false
  } finally {
    detailLoading.value = false
  }
}

// 等级文本转换
const getRankText = (rank) => {
  if (rank === null || rank === undefined) return '-'
  const rankMap = {
    1: '偏低',
    2: '标准',
    3: '偏高'
  }
  return rankMap[rank] || rank
}

// 计算属性 - 是否有四肢数据
const hasLimbData = computed(() => {
  if (!weightDetail.value) return false
  return hasLeftUpperLimbData.value || hasRightUpperLimbData.value || 
         hasLeftLowerLimbData.value || hasRightLowerLimbData.value || 
         hasTrunkData.value
})

const hasLeftUpperLimbData = computed(() => {
  if (!weightDetail.value) return false
  return weightDetail.value.left_upper_limb_fat_mass || weightDetail.value.left_upper_limb_muscle_mass
})

const hasRightUpperLimbData = computed(() => {
  if (!weightDetail.value) return false
  return weightDetail.value.right_upper_limb_fat_mass || weightDetail.value.right_upper_limb_muscle_mass
})

const hasLeftLowerLimbData = computed(() => {
  if (!weightDetail.value) return false
  return weightDetail.value.left_lower_limb_fat_mass || weightDetail.value.left_lower_limb_muscle_mass
})

const hasRightLowerLimbData = computed(() => {
  if (!weightDetail.value) return false
  return weightDetail.value.right_lower_limb_fat_mass || weightDetail.value.right_lower_limb_muscle_mass
})

const hasTrunkData = computed(() => {
  if (!weightDetail.value) return false
  return weightDetail.value.trunk_fat_mass || weightDetail.value.trunk_muscle_mass
})

// 删除记录
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      '此操作将删除该记录，是否继续？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    const res = await deleteExternalRecord(filterForm.value.data_type, row.id)
    if (res.code === 200) {
      ElMessage.success('删除成功')
      fetchDataList()  // 重新加载数据
    } else {
      ElMessage.error(res.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error(error)
    }
  }
}

onMounted(() => {
  fetchDataList()
})
</script>

<style scoped>
.external-data-container {
  padding: 20px;
}

.header {
  margin-bottom: 20px;
}

.header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
}

.filter-card {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* 详情弹窗样式 */
.detail-container {
  max-height: 70vh;
  overflow-y: auto;
  padding: 10px;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-section {
  background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.section-title {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  padding-bottom: 8px;
  border-bottom: 2px solid #409eff;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e8e8e8;
  transition: all 0.3s ease;
}

.info-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
  transform: translateY(-2px);
}

.info-item .label {
  font-size: 12px;
  color: #909399;
}

.info-item .value {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.info-item .value.primary {
  color: #409eff;
  font-size: 18px;
}

.info-item .value.success {
  color: #67c23a;
}

.info-item .value.warning {
  color: #e6a23c;
}

.limb-section {
  margin-top: 16px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 8px;
  border-left: 3px solid #409eff;
}

.limb-title {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #606266;
}

.note-content {
  padding: 12px;
  background: white;
  border-radius: 8px;
  border-left: 3px solid #67c23a;
  color: #606266;
  line-height: 1.6;
}

/* 滚动条美化 */
.detail-container::-webkit-scrollbar {
  width: 6px;
}

.detail-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.detail-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.detail-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
