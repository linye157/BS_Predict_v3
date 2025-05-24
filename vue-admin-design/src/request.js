import axios from 'axios'
import { Message } from 'element-ui'

// 创建axios实例
const service = axios.create({
  baseURL: '', // 使用空字符串作为基础URL，完全依赖Vue代理处理
  timeout: 60000, // 增加超时时间为60秒
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
      message = '网络连接超时，请检查网络或服务器状态'
    }
    
    Message({
      message: message,
      type: 'error',
      duration: 5 * 1000
    })
    
    return Promise.reject(error)
  }
)

export default service
