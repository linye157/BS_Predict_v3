import request from '../request'
// 不再直接使用axios和API_CONFIG，改用统一的request
// import axios from 'axios'
// import { API_BASE_URL, getApiUrl, API_CONFIG } from '@/config/api'

/**
 * 检查API服务是否可用
 * @param {number} timeout - 超时时间（毫秒）
 * @returns {Promise<boolean>} - 服务是否可用
 */
export const checkApiService = async (timeout = 5000) => {
  try {
    const response = await request({
      url: '/api/health',
      method: 'get',
      timeout
    })
    return response && (response.success !== false)
  } catch (error) {
    console.warn('API服务检查失败:', error.message)
    return false
  }
}

/**
 * 检查特定端口是否开放
 * @param {number} port - 端口号
 * @param {string} host - 主机地址
 * @returns {Promise<boolean>} - 端口是否开放
 */
export const checkPort = async (port = 5000, host = '127.0.0.1') => {
  try {
    const response = await fetch(`http://${host}:${port}`, {
      method: 'HEAD',
      mode: 'no-cors'
    })
    return true
  } catch (error) {
    return false
  }
}

/**
 * 获取服务器状态信息
 * @returns {Promise<object>} - 服务器状态信息
 */
export const getServerInfo = async () => {
  const isAvailable = await checkApiService()
  
  return {
    isAvailable,
    baseURL: 'proxy', // 通过代理访问
    timestamp: new Date().toISOString(),
    message: isAvailable ? '服务器连接正常' : '无法连接到服务器'
  }
} 