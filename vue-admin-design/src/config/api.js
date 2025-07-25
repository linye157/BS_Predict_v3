/**
 * API配置文件
 * 用于集中管理后端服务器地址和相关配置
 */

// 后端服务器基础地址
// export const API_BASE_URL = 'http://202.118.28.237:5000'
export const API_BASE_URL = 'http://127.0.0.1:5000'

// API相关配置
export const API_CONFIG = {
  // 基础URL
  baseURL: API_BASE_URL,
  
  // 超时时间配置
  timeout: {
    default: 60000,      // 默认60秒
    upload: 120000,      // 上传2分钟
    training: 600000,    // 训练10分钟
    automl: 600000       // AutoML 10分钟
  },
  
  // 端点配置
  endpoints: {
    health: '/api/health',
    system: {
      status: '/api/system/status'
    },
    data: {
      loadDefault: '/api/data/load-default',
      upload: '/api/data/upload',
      preview: '/api/data/preview',
      preprocess: '/api/data/preprocess',
      download: '/api/data/download'
    },
    ml: {
      models: '/api/ml/models',
      train: '/api/ml/train',
      predict: '/api/ml/predict',
      evaluate: '/api/ml/evaluate'
    },
    stacking: {
      models: '/api/stacking/models',
      train: '/api/stacking/train'
    },
    automl: {
      run: '/api/automl/run'
    },
    visualization: {
      data: '/api/visualization/data',
      model: '/api/visualization/model'
    },
    reports: {
      generate: '/api/reports/generate',
      list: '/api/reports/list',
      download: '/api/reports/download',
      delete: '/api/reports'
    },
    models: {
      list: '/api/models/list',
      download: '/api/models/download'
    }
  }
}

// 便捷方法：获取完整的API URL
export const getApiUrl = (endpoint) => {
  return `${API_BASE_URL}${endpoint}`
}

// 便捷方法：获取健康检查URL
export const getHealthCheckUrl = () => {
  return getApiUrl(API_CONFIG.endpoints.health)
}

export default API_CONFIG 