import request from '@/utils/request'

// 获取外部数据列表
export const getExternalDataList = (params) => {
  return request.get('/external-data/', { params })
}

// 获取最新的体重成分数据
export const getLatestWeightData = (params) => {
  return request.get('/external-data/latest-weight', { params })
}

// 获取体重记录详情
export const getWeightDetail = (recordId) => {
  return request.get(`/external-data/weight/${recordId}`)
}

// 删除外部数据记录
export const deleteExternalRecord = (dataType, recordId) => {
  return request.delete(`/external-data/${dataType}/${recordId}`)
}
