import request from '@/utils/request'

// 获取营养分析数据
export const getNutritionAnalysis = (params) => {
  return request.get('/nutrition/nutrition-analysis', { params })
}
