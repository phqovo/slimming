import request from '@/utils/request'

// 获取每日汇总数据
export const getDailyHistory = (params = {}) => {
  return request.get('/history/daily-history', { params })
}

// 重算指定日期的汇总数据
export const recalculateDailyHistory = (recordDate) => {
  return request.post('/history/daily-history/recalculate', {}, { params: { record_date: recordDate } })
}

// 获取历史记录详情
export const getDailyHistoryDetail = (historyId) => {
  return request.get(`/history/daily-history/${historyId}`)
}

// 新增历史记录
export const createDailyHistory = (data) => {
  return request.post('/history/daily-history', data)
}

// 更新历史记录
export const updateDailyHistory = (historyId, data) => {
  return request.put(`/history/daily-history/${historyId}`, data)
}

// 删除历史记录
export const deleteDailyHistory = (historyId) => {
  return request.delete(`/history/daily-history/${historyId}`)
}
