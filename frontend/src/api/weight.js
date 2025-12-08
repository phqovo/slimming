import request from '@/utils/request'

// 创建体重记录
export const createWeightRecord = (data) => {
  return request.post('/weight/', data)
}

// 获取体重记录列表
export const getWeightRecords = (params) => {
  return request.get('/weight/', { params })
}

// 获取指定日期的体重记录
export const getWeightRecordByDate = (date) => {
  return request.get('/weight/', { params: { record_date: date, limit: 1 } })
}

// 获取单条体重记录
export const getWeightRecord = (id) => {
  return request.get(`/weight/${id}`)
}

// 更新体重记录
export const updateWeightRecord = (id, data) => {
  return request.put(`/weight/${id}`, data)
}

// 删除体重记录
export const deleteWeightRecord = (id) => {
  return request.delete(`/weight/${id}`)
}

// 预测体重趋势
export const predictWeightTrend = (days) => {
  return request.post('/weight/predict', { days })
}
