import request from '@/utils/request'

/**
 * 搜索食物（在线）
 */
export function searchFoodOnline(keyword) {
  return request({
    url: '/food/search',
    method: 'get',
    params: { keyword }
  })
}

/**
 * 获取食物详情
 */
export function getFoodDetail(externalId) {
  return request({
    url: `/food/detail/${externalId}`,
    method: 'get'
  })
}

/**
 * 获取本地食物库列表
 */
export function getLocalFoods(params) {
  return request({
    url: '/food/local',
    method: 'get',
    params
  })
}

/**
 * 新增食物到本地库
 */
export function createLocalFood(data) {
  return request({
    url: '/food/local',
    method: 'post',
    data
  })
}

/**
 * 编辑本地食物
 */
export function updateLocalFood(id, data) {
  return request({
    url: `/food/local/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除本地食物
 */
export function deleteLocalFood(id) {
  return request({
    url: `/food/local/${id}`,
    method: 'delete'
  })
}

/**
 * 上传食物图片
 */
export function uploadFoodImage(file) {
  const formData = new FormData()
  formData.append('file', file)
  
  return request({
    url: '/food/upload-image',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}
