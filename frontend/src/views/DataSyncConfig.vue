<template>
  <div class="data-sync-container">
    <div class="header">
      <h2>数据拉取配置</h2>
      <div>
        <el-button type="default" :icon="Setting" @click="showAutoSyncSettings">设置</el-button>
        <el-button type="primary" @click="showLogDialog">查看同步日志</el-button>
      </div>
    </div>

    <!-- 数据来源选择 -->
    <el-card class="source-selector">
      <div class="source-selection">
        <span class="label">数据来源：</span>
        <el-select v-model="currentSource" placeholder="请选择数据来源" style="width: 200px">
          <el-option label="小米运动健康" value="xiaomi_sport" />
        </el-select>
        <el-tag type="info" size="small" style="margin-left: 10px">当前仅支持小米运动健康</el-tag>
        <el-tag v-if="!isAuthorized" type="danger" size="small" style="margin-left: 10px">
          <el-icon><WarningFilled /></el-icon>
          未检测到数据源授权配置
        </el-tag>
        <el-tag v-else type="success" size="small" style="margin-left: 10px">
          <el-icon><SuccessFilled /></el-icon>
          授权已验证
        </el-tag>
      </div>
    </el-card>

    <!-- 数据类型配置卡片 -->
    <el-row :gutter="20">
      <el-col :span="12" v-for="type in dataTypes" :key="type.value">
        <el-card class="config-card" :class="{ 'syncing': isSyncing(type.value) }">
          <template #header>
            <div class="card-header">
              <span class="type-name">{{ type.label }}</span>
              <el-tag v-if="isSyncing(type.value)" type="warning" size="small">同步中...</el-tag>
            </div>
          </template>

          <div class="config-content">
            <!-- 手动同步按钮 -->
            <div class="manual-sync">
              <el-button 
                type="primary" 
                :loading="isSyncing(type.value)"
                :disabled="isSyncing(type.value)"
                @click="handleManualSync(type.value)"
              >
                {{ isSyncing(type.value) ? '拉取中...' : '立即拉取' }}
              </el-button>
              <el-select 
                v-model="syncDays[type.value]" 
                placeholder="同步范围" 
                style="width: 140px; margin-left: 10px"
              >
                <el-option label="全部数据" value="0" />
                <el-option label="昨天数据" value="-1" />
                <el-option label="最近1天" value="1" />
                <el-option label="最近7天" value="7" />
                <el-option label="最近15天" value="15" />
                <el-option label="最近30天" value="30" />
                <el-option label="最近60天" value="60" />
                <el-option label="最近90天" value="90" />
                <el-option label="最近180天" value="180" />
                <el-option label="最近1年" value="365" />
              </el-select>
            </div>

            <!-- 定时任务配置 -->
            <div class="auto-sync">
              <el-divider />
              <div class="auto-sync-header">
                <span>自动拉取</span>
                <el-switch 
                  v-model="configs[type.value].enabled" 
                  @change="handleConfigChange(type.value)"
                  :disabled="updatingConfig[type.value]"
                />
              </div>
              
              <div v-if="configs[type.value].enabled" style="margin-top: 15px">
                <!-- 调度类型选择 -->
                <div class="schedule-type-config" style="margin-bottom: 15px">
                  <span style="margin-right: 10px">调度模式：</span>
                  <el-radio-group 
                    v-model="configs[type.value].schedule_type" 
                    @change="handleScheduleTypeChange(type.value)"
                    :disabled="updatingConfig[type.value]"
                  >
                    <el-radio label="interval">间隔执行</el-radio>
                    <el-radio label="cron">每天定时</el-radio>
                  </el-radio-group>
                </div>

                <!-- 间隔执行配置 -->
                <div class="interval-config" v-if="configs[type.value].schedule_type === 'interval'">
                  <span>拉取间隔：</span>
                  <el-select 
                    v-model="configs[type.value].interval_seconds" 
                    placeholder="选择间隔"
                    style="width: 150px"
                    @change="handleConfigChange(type.value)"
                    :disabled="updatingConfig[type.value]"
                  >
                    <el-option label="每5秒" :value="5" />
                    <el-option label="每10秒" :value="10" />
                    <el-option label="每30秒" :value="30" />
                    <el-option label="每1分钟" :value="60" />
                    <el-option label="每5分钟" :value="300" />
                    <el-option label="每10分钟" :value="600" />
                    <el-option label="每30分钟" :value="1800" />
                    <el-option label="每1小时" :value="3600" />
                    <el-option label="每6小时" :value="21600" />
                    <el-option label="每12小时" :value="43200" />
                    <el-option label="每天" :value="86400" />
                  </el-select>
                </div>

                <!-- 每天定时配置 -->
                <div class="cron-config" v-if="configs[type.value].schedule_type === 'cron'">
                  <span>执行时间：</span>
                  <el-time-select
                    v-model="configs[type.value].cronTimeStr"
                    placeholder="选择时间"
                    start="00:00"
                    step="00:01"
                    end="23:59"
                    style="width: 150px"
                    @change="handleCronTimeChange(type.value)"
                    :disabled="updatingConfig[type.value]"
                  />
                  <span style="margin-left: 10px; color: #909399; font-size: 12px">每天此时间执行</span>
                </div>
              </div>

              <div class="last-sync" v-if="configs[type.value].last_sync_time">
                <span>最后拉取：{{ formatDateTime(configs[type.value].last_sync_time) }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 同步日志弹窗 -->
    <el-dialog 
      v-model="logDialogVisible" 
      title="同步日志" 
      width="80%"
      :close-on-click-modal="false"
    >
      <div class="log-filters">
        <el-form :inline="true" :model="logFilters">
          <el-form-item label="数据来源">
            <el-select v-model="logFilters.data_source" placeholder="全部" clearable style="width: 150px">
              <el-option label="小米运动健康" value="xiaomi_sport" />
            </el-select>
          </el-form-item>
          <el-form-item label="数据类型">
            <el-select v-model="logFilters.data_type" placeholder="全部" clearable style="width: 150px">
              <el-option label="体重记录" value="weight" />
              <el-option label="睡眠记录" value="sleep" />
              <el-option label="锻炼记录" value="exercise" />
              <el-option label="运动步数" value="steps" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="logFilters.status" placeholder="全部" clearable style="width: 120px">
              <el-option label="运行中" value="running" />
              <el-option label="成功" value="success" />
              <el-option label="失败" value="failed" />
            </el-select>
          </el-form-item>
          <el-form-item label="时间范围">
            <el-date-picker
              v-model="logDateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
              style="width: 260px"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="fetchLogs">查询</el-button>
            <el-button @click="resetLogFilters">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-table :data="logs" style="width: 100%" v-loading="loadingLogs">
        <el-table-column prop="data_source" label="数据来源" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.data_source === 'xiaomi_sport'" type="success" size="small">小米运动健康</el-tag>
            <span v-else>{{ row.data_source }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="data_type" label="数据类型" width="120">
          <template #default="{ row }">
            {{ getDataTypeLabel(row.data_type) }}
          </template>
        </el-table-column>
        <el-table-column prop="sync_type" label="同步类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.sync_type === 'manual' ? 'primary' : 'info'" size="small">
              {{ row.sync_type === 'manual' ? '手动' : '自动' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag 
              :type="row.status === 'success' ? 'success' : (row.status === 'failed' ? 'danger' : 'warning')" 
              size="small"
            >
              {{ row.status === 'success' ? '成功' : (row.status === 'failed' ? '失败' : '运行中') }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="开始时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.start_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="耗时" width="100">
          <template #default="{ row }">
            {{ row.duration ? (row.duration / 1000).toFixed(2) + 's' : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="data_count" label="数据条数" width="100" />
        <el-table-column prop="error_message" label="错误信息" min-width="200" show-overflow-tooltip />
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="logPage"
          v-model:page-size="logPageSize"
          :total="logTotal"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchLogs"
          @current-change="fetchLogs"
        />
      </div>
    </el-dialog>

    <!-- 自动同步设置弹窗 -->
    <el-dialog 
      v-model="autoSyncSettingsVisible" 
      title="自动同步设置" 
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form label-width="150px">
        <el-form-item label="自动同步到本系统">
          <el-switch v-model="autoSyncSettings.auto_sync_to_local" />
          <div style="color: #909399; font-size: 12px; margin-top: 5px">
            开启后，拉取数据时会自动将选中的数据类型同步到本系统
          </div>
        </el-form-item>

        <el-form-item label="同步数据类型" v-if="autoSyncSettings.auto_sync_to_local">
          <el-checkbox-group v-model="autoSyncDataTypes">
            <el-checkbox label="weight">体重数据</el-checkbox>
            <el-checkbox label="sleep">睡眠数据</el-checkbox>
            <el-checkbox label="exercise">锻炼数据</el-checkbox>
          </el-checkbox-group>
          <div style="color: #909399; font-size: 12px; margin-top: 5px">
            勾选的数据类型将自动同步到本地库，避免重复
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="autoSyncSettingsVisible = false">取消</el-button>
          <el-button type="primary" @click="saveAutoSyncSettings" :loading="savingAutoSyncSettings">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { WarningFilled, SuccessFilled, Setting } from '@element-plus/icons-vue'
import { 
  getSyncConfigs, 
  createSyncConfig, 
  updateSyncConfig,
  manualSync,
  checkSyncStatus,
  getSyncLogs
} from '@/api/data-sync'
import { getUserSettings, updateUserSettings } from '@/api/settings.js'
import { getAuthList } from '@/api/auth-management'
import dayjs from 'dayjs'

const dataTypes = [
  { label: '体重记录', value: 'weight' },
  { label: '睡眠记录', value: 'sleep' },
  { label: '锻炼记录', value: 'exercise' },
  { label: '运动步数', value: 'steps' }
]

const configs = reactive({
  sleep: { id: null, enabled: false, schedule_type: 'interval', interval_seconds: 3600, cron_hour: null, cron_minute: 0, cronTimeStr: '08:00', sync_days: 30, sync_yesterday: false, last_sync_time: null },
  exercise: { id: null, enabled: false, schedule_type: 'interval', interval_seconds: 3600, cron_hour: null, cron_minute: 0, cronTimeStr: '08:00', sync_days: 30, sync_yesterday: false, last_sync_time: null },
  weight: { id: null, enabled: false, schedule_type: 'interval', interval_seconds: 3600, cron_hour: null, cron_minute: 0, cronTimeStr: '08:00', sync_days: 30, sync_yesterday: false, last_sync_time: null },
  steps: { id: null, enabled: false, schedule_type: 'interval', interval_seconds: 60, cron_hour: null, cron_minute: 0, cronTimeStr: '08:00', sync_days: 7, sync_yesterday: false, last_sync_time: null }
})

const syncDays = reactive({
  sleep: '30',
  exercise: '30',
  weight: '30',
  steps: '7'
})

const syncingStatus = reactive({
  sleep: false,
  exercise: false,
  weight: false,
  steps: false
})

const updatingConfig = reactive({
  sleep: false,
  exercise: false,
  weight: false,
  steps: false
})

const logDialogVisible = ref(false)
const loadingLogs = ref(false)
const logs = ref([])
const logPage = ref(1)
const logPageSize = ref(20)
const logTotal = ref(0)
const logDateRange = ref([])
const currentSource = ref('xiaomi_sport')
const isAuthorized = ref(false)  // 授权状态

const logFilters = reactive({
  data_source: '',
  data_type: '',
  status: ''
})

// 自动同步设置
const autoSyncSettingsVisible = ref(false)
const savingAutoSyncSettings = ref(false)
const autoSyncSettings = reactive({
  auto_sync_to_local: false,
  sync_weight: false,
  sync_sleep: false,
  sync_exercise: false
})
const autoSyncDataTypes = ref([])

let statusCheckInterval = null

// 格式化日期时间
const formatDateTime = (time) => {
  if (!time) return '-'
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

// 获取数据类型标签
const getDataTypeLabel = (type) => {
  const item = dataTypes.find(t => t.value === type)
  return item ? item.label : type
}

// 检查是否正在同步
const isSyncing = (dataType) => {
  return syncingStatus[dataType]
}

// 处理cron时间变化
const handleCronTimeChange = (dataType) => {
  const timeStr = configs[dataType].cronTimeStr
  if (timeStr) {
    const [hour, minute] = timeStr.split(':')
    configs[dataType].cron_hour = parseInt(hour)
    configs[dataType].cron_minute = parseInt(minute)
    handleConfigChange(dataType)
  }
}

// 处理调度类型变化
const handleScheduleTypeChange = (dataType) => {
  const config = configs[dataType]
  // 如果切换到定时模式，确保有默认的cron时间
  if (config.schedule_type === 'cron') {
    if (config.cron_hour === null || config.cron_hour === undefined) {
      // 设置默认时间为 08:00
      config.cron_hour = 8
      config.cron_minute = 0
      config.cronTimeStr = '08:00'
    }
  }
  handleConfigChange(dataType)
}

// 检查授权状态
const checkAuthStatus = async () => {
  try {
    const res = await getAuthList({ 
      auth_type: currentSource.value,
      page: 1,
      page_size: 1
    })
    
    // 检查是否有已验证的授权配置
    if (res.items && res.items.length > 0) {
      const auth = res.items[0]
      isAuthorized.value = auth.status === 1 // status = 1 表示已验证
    } else {
      isAuthorized.value = false
    }
  } catch (error) {
    console.error('检查授权状态失败:', error)
    isAuthorized.value = false
  }
}

// 加载配置
const loadConfigs = async () => {
  try {
    const res = await getSyncConfigs()
    res.forEach(config => {
      if (configs[config.data_type]) {
        // 将cron时间转换为字符串格式
        const cronTimeStr = (config.cron_hour !== null && config.cron_hour !== undefined) 
          ? `${String(config.cron_hour).padStart(2, '0')}:${String(config.cron_minute || 0).padStart(2, '0')}`
          : '08:00'
        
        // 处理前端展示：sync_yesterday=true 时显示为 '-1'（字符串）
        let displayDays = String(config.sync_days || 30)
        if (config.sync_yesterday) {
          displayDays = '-1'
        }
        
        configs[config.data_type] = {
          id: config.id,
          enabled: config.enabled,
          schedule_type: config.schedule_type || 'interval',
          interval_seconds: config.interval_seconds,
          cron_hour: config.cron_hour,
          cron_minute: config.cron_minute || 0,
          cronTimeStr: cronTimeStr,
          sync_days: config.sync_days || 30,
          sync_yesterday: config.sync_yesterday || false,
          last_sync_time: config.last_sync_time
        }
        
        syncDays[config.data_type] = displayDays
      }
    })
  } catch (error) {
    console.error('加载配置失败:', error)
  }
}

// 配置变更处理
const handleConfigChange = async (dataType) => {
  // 检查授权状态
  if (!isAuthorized.value) {
    ElMessage.warning('未检测到数据源授权配置，请先在授权管理中配置并验证')
    // 恢复配置
    await loadConfigs()
    return
  }
  
  const config = configs[dataType]
  updatingConfig[dataType] = true
  
  try {
    // 处理同步范围：-1 表示昨天数据
    const selectedDays = parseInt(syncDays[dataType])
    const isSyncYesterday = selectedDays === -1
    const actualDays = isSyncYesterday ? 1 : selectedDays
    
    const configData = {
      enabled: config.enabled,
      schedule_type: config.schedule_type,
      interval_seconds: config.interval_seconds,
      cron_hour: config.cron_hour,
      cron_minute: config.cron_minute,
      sync_days: actualDays,
      sync_yesterday: isSyncYesterday
    }
    
    if (config.id) {
      // 更新配置
      await updateSyncConfig(config.id, configData)
      ElMessage.success('配置已更新')
    } else {
      // 创建配置
      const res = await createSyncConfig({
        data_source: currentSource.value,
        data_type: dataType,
        ...configData
      })
      config.id = res.id
      ElMessage.success('配置已创建')
    }
  } catch (error) {
    ElMessage.error('配置更新失败')
    console.error(error)
    // 恢复配置
    await loadConfigs()
  } finally {
    updatingConfig[dataType] = false
  }
}

// 手动同步
const handleManualSync = async (dataType) => {
  // 检查授权状态
  if (!isAuthorized.value) {
    ElMessage.warning('未检测到数据源授权配置，请先在授权管理中配置并验证')
    return
  }
  
  console.log('点击同步按钮，dataType:', dataType)
  console.log('当前数据来源:', currentSource.value)
  console.log('同步天数:', syncDays[dataType])
  
  try {
    const syncPayload = {
      data_source: currentSource.value,
      data_type: dataType,
      days: parseInt(syncDays[dataType])
    }
    console.log('发送同步请求，payload:', syncPayload)
    
    const result = await manualSync(syncPayload)
    console.log('同步响应:', result)
    
    ElMessage.success('同步任务已启动，请稍后查看同步日志')
    
    // 开始检查同步状态
    syncingStatus[dataType] = true
  } catch (error) {
    console.error('同步错误:', error)
    if (error.response?.status === 409) {
      ElMessage.warning('该数据类型正在同步中，请稍后再试')
    } else {
      ElMessage.error('同步启动失败')
    }
    console.error(error)
  }
}

// 检查所有同步状态
const checkAllSyncStatus = async () => {
  // 只检查正在同步的类型，减少不必要的请求
  const syncingTypes = dataTypes.filter(type => syncingStatus[type.value])
  
  // 如果没有正在同步的任务，不需要轮询
  if (syncingTypes.length === 0) {
    return
  }
  
  for (const type of syncingTypes) {
    try {
      const res = await checkSyncStatus(currentSource.value, type.value)
      syncingStatus[type.value] = res.is_syncing
      
      // 如果同步完成，刷新配置以更新最后同步时间
      if (!res.is_syncing) {
        await loadConfigs()
      }
    } catch (error) {
      console.error('检查同步状态失败:', error)
      // 如果检查失败，也认为同步已完成
      syncingStatus[type.value] = false
    }
  }
}

// 显示日志对话框
const showLogDialog = () => {
  logDialogVisible.value = true
  fetchLogs()
}

// 获取日志
const fetchLogs = async () => {
  loadingLogs.value = true
  try {
    const params = {
      page: logPage.value,
      page_size: logPageSize.value
    }
    
    if (logFilters.data_source) params.data_source = logFilters.data_source
    if (logFilters.data_type) params.data_type = logFilters.data_type
    if (logFilters.status) params.status = logFilters.status
    if (logDateRange.value && logDateRange.value.length === 2) {
      params.start_date = logDateRange.value[0]
      params.end_date = logDateRange.value[1]
    }
    
    const res = await getSyncLogs(params)
    logs.value = res.items
    logTotal.value = res.total
  } catch (error) {
    ElMessage.error('获取日志失败')
    console.error(error)
  } finally {
    loadingLogs.value = false
  }
}

// 重置日志筛选
const resetLogFilters = () => {
  logFilters.data_source = ''
  logFilters.data_type = ''
  logFilters.status = ''
  logDateRange.value = []
  logPage.value = 1
  fetchLogs()
}

// 显示自动同步设置
const showAutoSyncSettings = async () => {
  try {
    const settings = await getUserSettings()
    autoSyncSettings.auto_sync_to_local = settings.auto_sync_to_local
    autoSyncSettings.sync_weight = settings.sync_weight
    autoSyncSettings.sync_sleep = settings.sync_sleep
    autoSyncSettings.sync_exercise = settings.sync_exercise

    const types = []
    if (settings.sync_weight) types.push('weight')
    if (settings.sync_sleep) types.push('sleep')
    if (settings.sync_exercise) types.push('exercise')
    autoSyncDataTypes.value = types

    autoSyncSettingsVisible.value = true
  } catch (e) {
    ElMessage.error('加载设置失败')
  }
}

// 保存自动同步设置
const saveAutoSyncSettings = async () => {
  try {
    savingAutoSyncSettings.value = true

    const payload = {
      auto_sync_to_local: autoSyncSettings.auto_sync_to_local,
      sync_weight: autoSyncDataTypes.value.includes('weight'),
      sync_sleep: autoSyncDataTypes.value.includes('sleep'),
      sync_exercise: autoSyncDataTypes.value.includes('exercise'),
    }

    await updateUserSettings(payload)

    ElMessage.success('保存成功')
    autoSyncSettingsVisible.value = false
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    savingAutoSyncSettings.value = false
  }
}

onMounted(async () => {
  // 先检查授权状态
  await checkAuthStatus()
  
  await loadConfigs()
  
  // 首次加载时检查一次所有状态
  for (const type of dataTypes) {
    try {
      const res = await checkSyncStatus(currentSource.value, type.value)
      syncingStatus[type.value] = res.is_syncing
    } catch (error) {
      console.error('检查同步状态失败:', error)
    }
  }
  
  // 启动定时检查，但只检查正在同步的任务
  statusCheckInterval = setInterval(checkAllSyncStatus, 5000)
})

onUnmounted(() => {
  // 清理定时器
  if (statusCheckInterval) {
    clearInterval(statusCheckInterval)
    statusCheckInterval = null
  }
  
  // 重置状态
  Object.keys(syncingStatus).forEach(key => {
    syncingStatus[key] = false
  })
})
</script>

<style scoped>
.data-sync-container {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
}

.source-selector {
  margin-bottom: 20px;
}

.source-selection {
  display: flex;
  align-items: center;
}

.source-selection .label {
  font-weight: 500;
  margin-right: 10px;
}

.config-card {
  margin-bottom: 20px;
}

.config-card.syncing {
  border-color: #E6A23C;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.type-name {
  font-weight: 500;
  font-size: 16px;
}

.config-content {
  padding: 10px 0;
}

.manual-sync {
  display: flex;
  align-items: center;
}

.auto-sync-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.interval-config {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  gap: 10px;
}

.last-sync {
  margin-top: 10px;
  font-size: 12px;
  color: #909399;
}

.log-filters {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
