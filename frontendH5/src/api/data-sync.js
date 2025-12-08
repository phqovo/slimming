import request from '@/utils/request'

// 获取同步配置列表
export const getSyncConfigs = () => {
  return request.get('/data-sync/configs')
}

// 创建同步配置
export const createSyncConfig = (data) => {
  return request.post('/data-sync/configs', data)
}

// 更新同步配置
export const updateSyncConfig = (id, data) => {
  return request.put(`/data-sync/configs/${id}`, data)
}

// 删除同步配置
export const deleteSyncConfig = (id) => {
  return request.delete(`/data-sync/configs/${id}`)
}

// 手动同步数据
export const manualSync = (data) => {
  console.log('[API] manualSync called with data:', data)
  const promise = request.post('/data-sync/manual-sync', data)
  console.log('[API] manualSync request promise created')
  return promise
}

// 检查同步状态
export const checkSyncStatus = (data_source, data_type) => {
  return request.get('/data-sync/sync-status', {
    params: { data_source, data_type }
  })
}

// 获取同步日志
export const getSyncLogs = (params) => {
  return request.get('/data-sync/logs', { params })
}
