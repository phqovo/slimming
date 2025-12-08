import axios from 'axios'
import { showToast } from 'vant'
import router from '../router'

// 根据环境设置 baseURL
const baseURL = import.meta.env.PROD 
  ? 'https://piheqi.com/health/api/v1'  // 生产环境：使用域名
  : '/health/api/v1'                    // 开发环境：使用代理

const request = axios.create({
  baseURL: baseURL,
  timeout: 30000
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    if (error.response) {
      const { status, data } = error.response
      
      if (status === 401) {
        showToast('登录已过期，请重新登录')
        localStorage.removeItem('token')
        router.push('/login')
      } else if (status === 403) {
        showToast('没有权限访问')
      } else if (status === 404) {
        showToast('请求的资源不存在')
      } else if (status === 500) {
        showToast(data?.message || '服务器错误')
      } else {
        showToast(data?.detail || data?.message || '请求失败')
      }
    } else {
      showToast('网络错误，请检查网络连接')
    }
    
    return Promise.reject(error)
  }
)

export default request
