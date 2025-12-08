import request from '@/utils/request'

/**
 * 获取QQ绑定URL
 */
export function getQQBindUrl() {
  return request({
    url: '/oauth/qq/bind-url',
    method: 'get'
  })
}

/**
 * 获取微信绑定URL
 */
export function getWechatBindUrl() {
  return request({
    url: '/oauth/wechat/bind-url',
    method: 'get'
  })
}
