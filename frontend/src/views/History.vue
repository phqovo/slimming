<template>
  <div class="history-container">
    <el-card class="rounded-card" shadow="never">
      <template #header>
        <div class="card-header">
          <h3>历史记录</h3>
          <div class="header-actions">
            <el-button type="primary" @click="handleCreate">新增记录</el-button>
            <el-button-group style="margin-left: 12px;">
              <el-button 
                :type="activeRange === 'month' ? 'primary' : 'default'"
                @click="setDateRange('month')"
              >
                本月
              </el-button>
              <el-button 
                :type="activeRange === 'three-months' ? 'primary' : 'default'"
                @click="setDateRange('three-months')"
              >
                近三月
              </el-button>
              <el-button 
                :type="activeRange === 'year' ? 'primary' : 'default'"
                @click="setDateRange('year')"
              >
                本年
              </el-button>
            </el-button-group>
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              @change="handleDateChange"
              style="width: 300px; margin-left: 12px;"
            />
          </div>
        </div>
      </template>

      <!-- 数据表格 -->
      <el-table :data="records" stripe style="width: 100%;" @row-dblclick="handleView" v-loading="loading">
        <el-table-column prop="record_date" label="日期" width="120" align="center" />
        <el-table-column prop="breakfast" label="早餐" min-width="120" />
        <el-table-column prop="lunch" label="中餐" min-width="120" />
        <el-table-column prop="dinner" label="晚餐" min-width="120" />
        <el-table-column prop="exercise" label="运动" min-width="150" />
        <el-table-column prop="morning_weight" label="早晨体重" width="100">
          <template #default="{ row }">
            {{ row.morning_weight ? settingsStore.convertWeightToDisplay(row.morning_weight) + ' ' + settingsStore.getWeightUnitText() : '--' }}
          </template>
        </el-table-column>
        <el-table-column prop="evening_weight" label="睡前体重" width="100">
          <template #default="{ row }">
            {{ row.evening_weight ? settingsStore.convertWeightToDisplay(row.evening_weight) + ' ' + settingsStore.getWeightUnitText() : '--' }}
          </template>
        </el-table-column>
        <el-table-column prop="water" label="饮水" width="80" />
        <el-table-column prop="note" label="备注" min-width="120" show-overflow-tooltip />
        <el-table-column label="操作" width="140" fixed="right" align="center">
          <template #default="{ row }">
            <div style="display: flex; justify-content: center; align-items: center; gap: 8px;">
              <el-button type="warning" size="small" @click="handleEdit(row)">编辑</el-button>
              <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadData"
          @current-change="loadData"
          background
        />
      </div>
    </el-card>

    <!-- 详情/编辑对话框 -->
    <HistoryDetailDialog
      v-model="dialogVisible"
      :history-id="selectedHistoryId"
      :mode="dialogMode"
      @success="handleDialogSuccess"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { getDailyHistory, deleteDailyHistory } from '@/api/daily'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import HistoryDetailDialog from '@/components/HistoryDetailDialog.vue'

const settingsStore = useSettingsStore()

const records = ref([])
const dateRange = ref([])
const activeRange = ref('month')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const dialogVisible = ref(false)
const selectedHistoryId = ref(null)
const dialogMode = ref('view') // view, edit, create
const loading = ref(false)

// 设置日期范围
const setDateRange = async (range) => {
  const today = dayjs()
  let startDate, endDate
  
  switch (range) {
    case 'month':
      // 本月
      startDate = today.startOf('month')
      endDate = today.endOf('month')
      break
    case 'three-months':
      // 近三月
      startDate = today.subtract(3, 'months').startOf('month')
      endDate = today.endOf('month')
      break
    case 'year':
      // 本年
      startDate = today.startOf('year')
      endDate = today.endOf('year')
      break
    default:
      startDate = today.startOf('month')
      endDate = today.endOf('month')
  }
  
  activeRange.value = range
  dateRange.value = [startDate.format('YYYY-MM-DD'), endDate.format('YYYY-MM-DD')]
  currentPage.value = 1
  
  // 等待数据加载完成
  await loadData()
}

// 加载数据
const loadData = async () => {
  try {
    loading.value = true
    
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    
    console.log('加载历史记录，参数:', params)
    
    const response = await getDailyHistory(params)
    
    console.log('获取到数据:', response)
    
    // 使用后端返回的分页数据
    records.value = response.items || []
    total.value = response.total || 0
    currentPage.value = response.page || 1
    pageSize.value = response.page_size || 20
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 处理日期变化
const handleDateChange = () => {
  activeRange.value = '' // 清除按钮选中状态
  currentPage.value = 1
  loadData()
}

// 新增记录
const handleCreate = () => {
  dialogMode.value = 'create'
  selectedHistoryId.value = null
  dialogVisible.value = true
}

// 查看详情
const handleView = (row) => {
  dialogMode.value = 'view'
  selectedHistoryId.value = row.id
  dialogVisible.value = true
}

// 编辑记录
const handleEdit = (row) => {
  dialogMode.value = 'edit'
  selectedHistoryId.value = row.id
  dialogVisible.value = true
}

// 删除记录
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除 ${row.record_date} 的历史记录吗？删除后将同时删除该日期的所有子记录（饮食、运动、体重、睡眠、饮水）！`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await deleteDailyHistory(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 对话框成功回调
const handleDialogSuccess = () => {
  loadData()
}

onMounted(async () => {
  // 确保设置已加载
  if (!settingsStore.isLoaded) {
    await settingsStore.loadSettings()
  }
  
  // 默认设置为本月
  setDateRange('month')
})
</script>

<style scoped>
.history-container {
  max-width: 1600px;
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

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
