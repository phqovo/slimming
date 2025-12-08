import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

// 根据环境设置 baseURL
const baseURL = import.meta.env.PROD 
  ? 'https://piheqi.com/health/api/v1'  // 生产环境：使用域名
  : '/health/api/v1'                    // 开发环境：使用代理

const request = axios.create({
  baseURL: baseURL,
  timeout: 30000,
  // 自定义状态码验证，将 202 视为错误响应
  validateStatus: function (status) {
    // 202 状态码用于二次验证，应该被 reject
    if (status === 202) {
      return false
    }
    // 其他 2xx 状态码视为成功
    return status >= 200 && status < 300
  }
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
      
      // 202 状态码用于二次验证，不显示错误消息
      if (status === 202) {
        return Promise.reject(error)
      }
      
      if (status === 401) {
        ElMessage.error('登录已过期，请重新登录')
        localStorage.removeItem('token')
        router.push('/login')
      } else if (status === 403) {
        ElMessage.error('没有权限访问')
      } else if (status === 404) {
        ElMessage.error('请求的资源不存在')
      } else if (status === 500) {
        ElMessage.error(data?.message || '服务器错误')
      } else {
        ElMessage.error(data?.detail || data?.message || '请求失败')
      }
    } else {
      ElMessage.error('网络错误，请检查网络连接')
    }
    
    return Promise.reject(error)
  }
)

export default request
