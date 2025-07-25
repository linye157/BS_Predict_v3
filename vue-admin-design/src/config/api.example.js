/**
 * API配置示例文件
 * 复制此文件为 api.js 并根据实际环境修改配置
 */

// ================================
// 不同环境的配置示例
// ================================

// 开发环境配置
// export const API_BASE_URL = 'http://localhost:5000'

// 测试环境配置  
// export const API_BASE_URL = 'http://192.168.1.100:5000'

// 生产环境配置
// export const API_BASE_URL = 'https://your-production-domain.com:5000'

// 当前配置（请根据实际情况修改）
export const API_BASE_URL = 'http://202.118.28.237:5000'
// export const API_BASE_URL = 'http://127.0.0.1:5000'
// ================================
// 高级配置：根据环境变量自动切换
// ================================

// 方法1：根据当前域名自动判断环境
/*
const getCurrentEnvironment = () => {
  const hostname = window.location.hostname
  
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'development'
  } else if (hostname.includes('test') || hostname.includes('staging')) {
    return 'testing'
  } else {
    return 'production'
  }
}

const environmentConfig = {
  development: 'http://localhost:5000',
  testing: 'http://test-server:5000',
  production: 'https://api.yourdomain.com'
}

export const API_BASE_URL = environmentConfig[getCurrentEnvironment()]
*/

// 方法2：使用Vue CLI环境变量
/*
export const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:5000'

// 在项目根目录创建以下文件：
// .env.development
// VUE_APP_API_BASE_URL=http://localhost:5000

// .env.testing  
// VUE_APP_API_BASE_URL=http://test-server:5000

// .env.production
// VUE_APP_API_BASE_URL=https://api.yourdomain.com
*/

// API相关配置
export const API_CONFIG = {
  // 基础URL
  baseURL: API_BASE_URL,
  
  // 超时时间配置（毫秒）
  timeout: {
    default: 60000,      // 默认60秒
    upload: 120000,      // 上传2分钟
    training: 600000,    // 训练10分钟
    automl: 600000       // AutoML 10分钟
  },
  
  // API端点配置
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