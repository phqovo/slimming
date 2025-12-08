import request from '@/utils/request'

// 创建饮食记录
export const addDietRecord = (data) => {
  return request.post('/diet/', data)
}

// 获取饮食记录列表
export const getDietRecords = (params) => {
  // 将 page 和 page_size 转换为 skip 和 limit
  const queryParams = { ...params }
  if (params.page && params.page_size) {
    queryParams.skip = (params.page - 1) * params.page_size
    queryParams.limit = params.page_size
    delete queryParams.page
    delete queryParams.page_size
  }
  return request.get('/diet/', { params: queryParams })
}

// 获取单条饮食记录
export const getDietRecord = (id) => {
  return request.get(`/diet/${id}`)
}

// 更新饮食记录
export const updateDietRecord = (id, data) => {
  return request.put(`/diet/${id}`, data)
}

// 删除饮食记录
export const deleteDietRecord = (id) => {
  return request.delete(`/diet/${id}`)
}

// 获取今日饮食摘要
export const getTodayDietSummary = () => {
  return request.get('/diet/today-summary')
}
