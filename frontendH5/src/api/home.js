import request from '@/utils/request'

// 获取今日概览数据
export const getTodayDashboard = () => {
  return request.get('/home/dashboard')
}

// 获取热量趋势
export const getCaloriesTrend = (params) => {
  return request.get('/home/calories-trend', { params })
}

// 获取今日摘要
export const getTodaySummary = () => {
  return request.get('/home/today')
}
