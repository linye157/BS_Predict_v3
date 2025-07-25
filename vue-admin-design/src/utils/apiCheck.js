import axios from 'axios'

/**
 * 检查API服务是否可用
 * @param {string} baseURL - API基础地址
 * @param {number} timeout - 超时时间（毫秒）
 * @returns {Promise<boolean>} - 服务是否可用
 */
export const checkApiService = async (baseURL = 'http://202.118.28.237:5000', timeout = 5000) => {
  try {
    const response = await axios({
      url: `${baseURL}/api/health`,
      method: 'get',
      timeout
    })
    return response.status === 200
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
export const checkPort = async (port = 5000, host = '202.118.28.237') => {
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
 * @param {string} baseURL - API基础地址
 * @returns {Promise<object>} - 服务器状态信息
 */
export const getServerInfo = async (baseURL = 'http://202.118.28.237:5000') => {
  const isAvailable = await checkApiService(baseURL)
  
  return {
    isAvailable,
    baseURL,
    timestamp: new Date().toISOString(),
    message: isAvailable ? '服务器连接正常' : '无法连接到服务器'
  }
} 