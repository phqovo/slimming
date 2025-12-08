import request from '@/utils/request'

/**
 * 绑定手机号
 */
export function bindPhone(data) {
  return request({
    url: '/api/v1/user/bind/phone',
    method: 'post',
    data
  })
}

/**
 * 解绑账号
 */
export function unbindAccount(accountType) {
  return request({
    url: '/api/v1/user/unbind',
    method: 'post',
    data: {
      account_type: accountType
    }
  })
}

/**
 * 发送绑定手机号验证码
 */
export function sendBindSmsCode(phone) {
  return request({
    url: '/api/v1/auth/send-sms',
    method: 'post',
    data: {
      phone,
      scene: 'bind'  // 绑定场景
    }
  })
}
