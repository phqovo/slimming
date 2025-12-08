import request from '@/utils/request'

// 创建食物单位
export const createFoodUnit = (foodId, unitData) => {
  return request.post('/api/v1/food-units/units', {
    ...unitData,
    food_id: foodId
  })
}

// 获取食物的所有单位
export const getFoodUnits = (foodId, sourceType = 'local') => {
  return request.get(`/api/v1/food-units/units/${foodId}?source_type=${sourceType}`)
}

// 更新食物单位
export const updateFoodUnit = (foodId, unitId, unitData) => {
  return request.put(`/api/v1/food-units/units/${foodId}/${unitId}`, unitData)
}

// 删除食物单位
export const deleteFoodUnit = (foodId, unitId) => {
  return request.delete(`/api/v1/food-units/units/${foodId}/${unitId}`)
}

// 保存食物单位转换记录
export const saveFoodUnitRecord = (recordData) => {
  return request.post('/api/v1/food-units/records', recordData)
}

// 获取食物的所有单位转换记录
export const getFoodUnitRecords = (foodId, sourceType = 'local') => {
  return request.get(`/api/v1/food-units/records/${foodId}?source_type=${sourceType}`)
}

// 删除食物单位转换记录
export const deleteFoodUnitRecord = (foodId, recordId) => {
  return request.delete(`/api/v1/food-units/records/${foodId}/${recordId}`)
}
