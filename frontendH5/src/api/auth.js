import request from '@/utils/request'

// 发送验证码
export const sendVerificationCode = (data) => {
  return request.post('/auth/send-code', data)
}

// 登录
export const login = (data) => {
  const deviceId = 'device_' + Math.random().toString(36).substring(2, 15) + Date.now().toString(36)
  return request.post('/auth/login', {
    ...data,
    device_id: deviceId
  })
}

// 退出登录
export const logout = () => {
  return request.post('/auth/logout')
}
