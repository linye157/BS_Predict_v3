import request from '../request'
// 移除直接创建的axios实例，改用统一的request
// import axios from 'axios'
// import { API_CONFIG } from '@/config/api'

// 移除独立的axios实例创建
// const api = axios.create({
//   baseURL: API_CONFIG.baseURL,
//   timeout: API_CONFIG.timeout.upload,
//   headers: {
//     'Content-Type': 'application/json',
//     'Accept': 'application/json'
//   }
// })

// 系统状态
export const getSystemStatus = () => {
  return request({
    url: '/api/system/status',
    method: 'get'
  })
  .catch(error => {
    console.error('获取系统状态失败:', error);
    return { success: false, message: error.message || '获取系统状态失败' };
  })
}

// 数据处理相关API
export const loadDefaultData = () => {
  return request({
    url: '/api/data/load-default',
    method: 'post'
  })
  .catch(error => {
    console.error('加载默认数据失败:', error);
    return { success: false, message: error.message || '加载默认数据失败' };
  })
}

export const uploadData = (formData) => {
  // 确保正确打印上传的文件信息以便调试
  for (let [key, value] of formData.entries()) {
    console.log(`${key}: ${value instanceof File ? value.name : value}`);
  }
  
  return request({
    url: '/api/data/upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  .catch(error => {
    console.error('上传数据失败:', error);
    return { success: false, message: error.message || '上传数据失败' };
  })
}

export const getDataPreview = () => {
  return request({
    url: '/api/data/preview',
    method: 'get'
  })
  .catch(error => {
    console.error('获取数据预览失败:', error);
    return { success: false, train_preview: { columns: [] } };
  })
}

export const preprocessData = (params) => {
  return request({
    url: '/api/data/preprocess',
    method: 'post',
    data: params
  })
  .catch(error => {
    console.error('数据预处理失败:', error);
    return { success: false, message: error.message || '预处理失败' };
  })
}

export const downloadData = (dataType, fileFormat) => {
  return request({
    url: `/api/data/download/${dataType}/${fileFormat}`,
    method: 'get',
    responseType: 'blob'
  })
}

// 机器学习相关API
export const getAvailableModels = () => {
  return request({
    url: '/api/ml/models',
    method: 'get'
  })
  .catch(error => {
    console.error('获取可用模型失败:', error);
    return { success: false, models: [] };
  })
}

export const trainModel = (params) => {
  console.log('发送训练请求，参数:', params);
  return request({
    url: '/api/ml/train',
    method: 'post',
    data: params,
    timeout: 600000  // 10分钟超时，适用于大数据集训练
  })
  .then(response => {
    console.log('训练响应成功:', response);
    return response;
  })
  .catch(error => {
    console.error('模型训练失败:', error);
    if (error.response) {
      // 服务器返回了错误状态码
      console.error('错误状态:', error.response.status);
      console.error('错误数据:', error.response.data);
      return { success: false, message: error.response.data.message || '服务器返回错误' };
    } else if (error.request) {
      // 请求已发出，但没有收到响应
      console.error('未收到响应:', error.request);
      return { success: false, message: '服务器未响应，请检查后端服务是否正常运行' };
    } else {
      // 请求配置出错
      return { success: false, message: error.message || '训练失败，请检查参数和数据' };
    }
  })
}

export const predictModel = (params) => {
  return request({
    url: '/api/ml/predict',
    method: 'post',
    data: params
  })
  .catch(error => {
    console.error('模型预测失败:', error);
    return { success: false, message: error.message || '预测失败' };
  })
}

export const evaluateModel = (params) => {
  return request({
    url: '/api/ml/evaluate',
    method: 'post',
    data: params
  })
  .catch(error => {
    console.error('模型评估失败:', error);
    return { success: false, message: error.message || '评估失败' };
  })
}

// Stacking集成学习API
export const getStackingModels = () => {
  return request({
    url: '/api/stacking/models',
    method: 'get'
  })
  .catch(error => {
    console.error('获取Stacking模型失败:', error);
    return { success: false, base_models: [], meta_models: [] };
  })
}

export const trainStackingModel = (params) => {
  return request({
    url: '/api/stacking/train',
    method: 'post',
    data: params,
    timeout: 600000  // 10分钟超时
  })
  .catch(error => {
    console.error('Stacking模型训练失败:', error);
    return { success: false, message: error.message || 'Stacking训练失败' };
  })
}

// AutoML相关API
export const runAutoML = (params) => {
  return request({
    url: '/api/automl/run',
    method: 'post',
    data: params,
    timeout: 600000  // 10分钟超时
  })
  .catch(error => {
    console.error('AutoML运行失败:', error);
    if (error.code === 'ECONNABORTED') {
      return { success: false, message: 'AutoML训练超时，请尝试减少模型数量或使用随机搜索' };
    }
    return { success: false, message: error.message || 'AutoML运行失败' };
  })
}

// 可视化相关API
export const generateDataVisualization = (params) => {
  return request({
    url: '/api/visualization/data',
    method: 'post',
    data: params
  })
  .catch(error => {
    console.error('生成数据可视化失败:', error);
    return { success: false, message: error.message || '生成数据可视化失败' };
  })
}

export const generateModelVisualization = (params) => {
  return request({
    url: '/api/visualization/model',
    method: 'post',
    data: params
  })
  .catch(error => {
    console.error('生成模型可视化失败:', error);
    return { success: false, message: error.message || '生成模型可视化失败' };
  })
}

// 报表相关API
export const generateReport = (params) => {
  return request({
    url: '/api/reports/generate',
    method: 'post',
    data: params
  })
  .catch(error => {
    console.error('生成报表失败:', error);
    return { success: false, message: error.message || '生成报表失败' };
  })
}

export const getReportsList = () => {
  return request({
    url: '/api/reports/list',
    method: 'get'
  })
  .catch(error => {
    console.error('获取报表列表失败:', error);
    return { success: false, reports: [] };
  })
}

export const downloadReport = (reportId, fileFormat) => {
  return request({
    url: `/api/reports/download/${reportId}/${fileFormat}`,
    method: 'get',
    responseType: 'blob'
  })
}

export const downloadReportFile = (reportId, fileFormat) => {
  return request({
    url: `/api/reports/download/${reportId}/${fileFormat}`,
    method: 'get',
    responseType: 'blob'
  })
}

export const deleteReport = (reportId) => {
  return request({
    url: `/api/reports/${reportId}`,
    method: 'delete'
  })
  .catch(error => {
    console.error('删除报表失败:', error);
    return { success: false, message: error.message || '删除报表失败' };
  })
}

// 模型管理相关API
export const getModelsList = () => {
  return request({
    url: '/api/models/list',
    method: 'get'
  })
  .catch(error => {
    console.error('获取模型列表失败:', error);
    return { success: false, models: [] };
  })
}

export const downloadModel = (modelId) => {
  return request({
    url: `/api/models/download/${modelId}`,
    method: 'get',
    responseType: 'blob'
  })
} 