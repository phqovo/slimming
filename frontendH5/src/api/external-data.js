import request from '@/utils/request'

// 获取外部数据列表
export const getExternalDataList = (params) => {
  return request.get('/external-data/', { params })
}

// 获取最新的体重成分数据
export const getLatestWeightData = (params) => {
  return request.get('/external-data/latest-weight', { params })
}
