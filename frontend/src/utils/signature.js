/**
 * 吉客云 API 签名生成工具
 */

import CryptoJS from 'crypto-js'

/**
 * 生成签名
 * @param {Object} params - 业务参数
 * @param {String} accessToken - Access Token
 * @param {String} timestamp - 时间戳（毫秒），不传则自动生成
 * @returns {Object} 包含签名的完整参数
 */
export function generateSign(params = {}, accessToken = '', timestamp = null) {
  const appkey = 'jackyun_web_browser_2024'
  const secret = '72EyvujHoQWmjfKqsl168SaVycZARQvt'

  // 生成时间戳
  if (!timestamp) {
    timestamp = Date.now().toString()
  }

  // 构建参数对象列表
  const paramObjects = []

  // 添加固定参数
  paramObjects.push({ key: 'appkey', value: appkey })
  paramObjects.push({ key: 'timestamp', value: timestamp })
  paramObjects.push({ key: 'access_token', value: accessToken })

  // 添加业务参数（空值和 null 不参与签名）
  for (const key in params) {
    const value = params[key]
    if (value !== null && value !== '') {
      // 对象转 JSON 字符串
      let strValue
      if (typeof value === 'object') {
        strValue = JSON.stringify(value)
      } else {
        strValue = String(value)
      }
      paramObjects.push({ key, value: strValue })
    }
  }

  // 按 key 的 ASCII 排序
  paramObjects.sort((a, b) => {
    return a.key.localeCompare(b.key)
  })

  // 构建签名字符串: secret + key1value1 + key2value2 + ... + secret
  let signStr = secret
  for (const obj of paramObjects) {
    signStr += obj.key + obj.value
  }
  signStr += secret

  // MD5 加密并转大写
  const sign = CryptoJS.MD5(signStr).toString().toUpperCase()

  return {
    timestamp,
    access_token: accessToken,
    appkey,
    sign,
    ...params
  }
}

/**
 * 生成查询字符串
 * @param {Object} params - 业务参数
 * @param {String} accessToken - Access Token
 * @param {String} timestamp - 时间戳
 * @returns {String} URL 查询字符串
 */
export function generateQueryString(params = {}, accessToken = '', timestamp = null) {
  const signedParams = generateSign(params, accessToken, timestamp)
  
  const queryParts = []
  for (const key in signedParams) {
    queryParts.push(`${encodeURIComponent(key)}=${encodeURIComponent(signedParams[key])}`)
  }
  
  return queryParts.join('&')
}
