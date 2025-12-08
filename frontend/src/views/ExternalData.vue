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
        <el-table-column prop="muscle_mass" label="肌肉量(kg)" width="110" />
        <el-table-column prop="bmr" label="基础代谢" width="100" />
        <el-table-column prop="body_score" label="身体评分" width="100" />
        <el-table-column prop="note" label="备注" min-width="150" show-overflow-tooltip />
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getExternalDataList } from '@/api/external-data'
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
</style>
