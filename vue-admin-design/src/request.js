import axios from 'axios'
import { Message } from 'element-ui'
import { API_CONFIG } from '@/config/api'

// 创建axios实例
const service = axios.create({
  // 不使用API_CONFIG.baseURL，让请求通过代理
  // baseURL: API_CONFIG.baseURL, 
  timeout: API_CONFIG.timeout.default, // 使用配置中的默认超时时间
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 在发送请求之前做些什么
    console.log('Request:', config.method?.toUpperCase(), config.url)
    if (config.data) {
      console.log('Request Data:', config.data)
    }
    
    // 对于训练相关的长时间请求，自动设置更长的超时时间
    if (config.url?.includes('/train') || config.url?.includes('/automl') || config.url?.includes('/stacking')) {
      if (!config.timeout || config.timeout < 300000) { // 如果超时时间小于5分钟
        config.timeout = 600000 // 设置为10分钟
        console.log('设置长时间请求超时:', config.timeout, 'ms')
      }
    }
    
    return config
  },
  error => {
    // 对请求错误做些什么
    console.error('Request Error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    // 对响应数据做点什么
    console.log('Response:', response.status, response.config.url)
    
    // 如果是文件下载，直接返回
    if (response.config.responseType === 'blob') {
      return response
    }
    
    const res = response.data
    
    // 统一处理成功响应
    if (res.success !== false) {
      return res
    } else {
      // 处理业务错误
      Message({
        message: res.message || '请求失败',
        type: 'error',
        duration: 5 * 1000
      })
      return Promise.reject(new Error(res.message || '请求失败'))
    }
  },
  error => {
    // 对响应错误做点什么
    console.error('Response Error:', error)
    
    let message = '网络错误'
    if (error.response) {
      // 服务器返回错误状态码
      const status = error.response.status
      switch (status) {
        case 400:
          message = '请求参数错误'
          break
        case 401:
          message = '未授权访问'
          break
        case 403:
          message = '拒绝访问'
          break
        case 404:
          message = '请求资源不存在'
          break
        case 500:
          message = '服务器内部错误'
          break
        default:
          message = `服务器错误 ${status}`
      }
      
      // 如果有响应数据中的错误信息，优先使用
      if (error.response.data && error.response.data.message) {
        message = error.response.data.message
      }
    } else if (error.request) {
      // 请求已发出，但没有收到响应
      if (error.code === 'ECONNABORTED') {
        message = '请求超时，服务器可能正在处理大量数据，请稍后重试'
      } else {
        message = '网络连接超时，请检查网络或服务器状态'
      }
    }
    
    // 只对非训练请求显示错误消息，训练请求的错误由组件自己处理
    if (!error.config?.url?.includes('/train') && !error.config?.url?.includes('/automl') && !error.config?.url?.includes('/stacking')) {
      Message({
        message: message,
        type: 'error',
        duration: 5 * 1000
      })
    }
    
    return Promise.reject(error)
  }
)

export default service
