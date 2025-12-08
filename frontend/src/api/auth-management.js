import request from '@/utils/request'

// 获取授权列表
export const getAuthList = (params) => {
  return request.get('/auth-management/', { params })
}

// 获取授权详情
export const getAuthDetail = (id) => {
  return request.get(`/auth-management/${id}`)
}

// 新增授权
export const createAuth = (data) => {
  return request.post('/auth-management/', data)
}

// 更新授权
export const updateAuth = (id, data) => {
  return request.put(`/auth-management/${id}`, data)
}

// 删除授权
export const deleteAuth = (id) => {
  return request.delete(`/auth-management/${id}`)
}

// 验证授权（不保存）
export const verifyAuth = (data) => {
  return request.post('/auth-management/verify', data)
}

// 验证并保存Token
export const verifyAndSaveToken = (id) => {
  return request.post(`/auth-management/${id}/verify-and-save`)
}

// 检查验证状态（轮询）
export const checkVerifyStatus = (id) => {
  return request.post(`/auth-management/${id}/check-verify-status`)
}
