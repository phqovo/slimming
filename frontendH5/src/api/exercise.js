import request from '@/utils/request'

// 创建运动记录
export const addExerciseRecord = (data) => {
  return request.post('/exercise/', data)
}

// 获取运动记录列表
export const getExerciseRecords = (params) => {
  // 将 page 和 page_size 转换为 skip 和 limit
  const queryParams = { ...params }
  if (params.page && params.page_size) {
    queryParams.skip = (params.page - 1) * params.page_size
    queryParams.limit = params.page_size
    delete queryParams.page
    delete queryParams.page_size
  }
  return request.get('/exercise/', { params: queryParams })
}

// 获取单条运动记录
export const getExerciseRecord = (id) => {
  return request.get(`/exercise/${id}`)
}

// 更新运动记录
export const updateExerciseRecord = (id, data) => {
  return request.put(`/exercise/${id}`, data)
}

// 删除运动记录
export const deleteExerciseRecord = (id) => {
  return request.delete(`/exercise/${id}`)
}

// 获取今日运动摘要
export const getTodayExerciseSummary = () => {
  return request.get('/exercise/today-summary')
}
