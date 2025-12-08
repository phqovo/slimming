import request from '@/utils/request'

// 获取用户设置
export const getUserSettings = () => {
  return request.get('/settings/')
}

// 更新用户设置
export const updateUserSettings = (data) => {
  return request.put('/settings/', data)
}
