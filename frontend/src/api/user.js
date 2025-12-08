import request from '@/utils/request'

// 发送验证码
export const sendCode = (phone) => {
  return request.post('/auth/send-code', { phone })
}

// 获取或生成设备ID
const getDeviceId = () => {
  // 基于域名生成唯一key，确保本地和云端使用不同的device_id
  const storageKey = `device_id_${window.location.host}`
  
  let deviceId = localStorage.getItem(storageKey)
  if (!deviceId) {
    // 生成随机设备ID
    deviceId = 'device_' + Math.random().toString(36).substring(2, 15) + Date.now().toString(36)
    localStorage.setItem(storageKey, deviceId)
  }
  return deviceId
}

// 登录/注册
export const login = (phone, code) => {
  return request.post('/auth/login', { 
    phone, 
    code,
    device_id: getDeviceId()  // 传递设备ID
  })
}

// 退出登录
export const logout = () => {
  return request.post('/auth/logout')
}

// 获取当前用户信息
export const getCurrentUser = () => {
  return request.get('/user/me')
}

// 更新用户信息
export const updateUser = (data) => {
  return request.put('/user/me', data)
}

// 上传头像
export const uploadAvatar = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/user/upload-avatar', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 获取用户统计信息
export const getUserStats = () => {
  return request.get('/user/stats')
}

// 获取减肥进度信息
export const getWeightProgress = () => {
  return request.get('/user/progress')
}
