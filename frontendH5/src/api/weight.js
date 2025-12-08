import request from '@/utils/request'

// 创建体重记录
export const createWeightRecord = (data) => {
  return request.post('/weight/', data)
}

// 获取体重记录列表
export const getWeightRecords = (params) => {
  // 将 page 和 page_size 转换为 skip 和 limit
  const queryParams = { ...params }
  if (params.page && params.page_size) {
    queryParams.skip = (params.page - 1) * params.page_size
    queryParams.limit = params.page_size
    delete queryParams.page
    delete queryParams.page_size
  }
  return request.get('/weight/', { params: queryParams })
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

// 添加体重记录
export const addWeightRecord = (data) => {
  return request.post('/weight/', data)
}

// 获取体重历史
export const getWeightHistory = (params) => {
  // 将 page 和 page_size 转换为 skip 和 limit
  const queryParams = { ...params }
  if (params.page && params.page_size) {
    queryParams.skip = (params.page - 1) * params.page_size
    queryParams.limit = params.page_size
    delete queryParams.page
    delete queryParams.page_size
  }
  return request.get('/weight/', { params: queryParams })
}

// 获取体重趋势
export const getWeightTrend = (params) => {
  return request.get('/weight/trend', { params })
}
