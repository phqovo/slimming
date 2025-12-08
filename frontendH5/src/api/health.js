import request from '@/utils/request'

// 运动记录API
export const createExerciseRecord = (data) => {
  return request.post('/exercise/', data)
}

export const getExerciseRecords = (params) => {
  return request.get('/exercise/', { params })
}

export const updateExerciseRecord = (id, data) => {
  return request.put(`/exercise/${id}`, data)
}

export const deleteExerciseRecord = (id) => {
  return request.delete(`/exercise/${id}`)
}

export const uploadExerciseImage = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/exercise/upload-image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 饮食记录API
export const createDietRecord = (data) => {
  return request.post('/diet/', data)
}

export const getDietRecords = (params) => {
  return request.get('/diet/', { params })
}

export const updateDietRecord = (id, data) => {
  return request.put(`/diet/${id}`, data)
}

export const deleteDietRecord = (id) => {
  return request.delete(`/diet/${id}`)
}

// 饮水记录API
export const createWaterRecord = (data) => {
  return request.post('/health/water', data)
}

export const getWaterRecords = (params) => {
  return request.get('/health/water', { params })
}

// 睡眠记录API
export const createSleepRecord = (data) => {
  return request.post('/health/sleep', data)
}

export const getSleepRecords = (params) => {
  return request.get('/health/sleep', { params })
}

export const updateSleepRecord = (id, data) => {
  return request.put(`/health/sleep/${id}`, data)
}
