import request from '../request'
import axios from 'axios'

// 创建axios实例，使用相对URL
const api = axios.create({
  baseURL: '', // 使用空字符串作为基础URL，依赖Vue代理
  timeout: 120000, // 2分钟超时
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// 系统状态
export const getSystemStatus = () => {
  return api({
    url: '/api/system/status',
    method: 'get'
  })
  .then(response => response.data)
  .catch(error => {
    console.error('获取系统状态失败:', error);
    return { success: false, message: error.message || '获取系统状态失败' };
  })
}

// 数据处理相关API
export const loadDefaultData = () => {
  return api({
    url: '/api/data/load-default',
    method: 'post'
  })
  .then(response => response.data)
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
  
  return api({
    url: '/api/data/upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  .then(response => response.data)
  .catch(error => {
    console.error('上传数据失败:', error);
    return { success: false, message: error.message || '上传数据失败' };
  })
}

export const getDataPreview = () => {
  return api({
    url: '/api/data/preview',
    method: 'get'
  })
  .then(response => response.data)
  .catch(error => {
    console.error('获取数据预览失败:', error);
    return { success: false, train_preview: { columns: [] } };
  })
}

export const preprocessData = (params) => {
  return api({
    url: '/api/data/preprocess',
    method: 'post',
    data: params
  })
  .then(response => response.data)
  .catch(error => {
    console.error('数据预处理失败:', error);
    return { success: false, message: error.message || '预处理失败' };
  })
}

export const downloadData = (dataType, fileFormat) => {
  return api({
    url: `/api/data/download/${dataType}/${fileFormat}`,
    method: 'get',
    responseType: 'blob'
  })
}

// 机器学习相关API
export const getAvailableModels = () => {
  return api({
    url: '/api/ml/models',
    method: 'get'
  })
  .then(response => response.data)
  .catch(error => {
    console.error('获取可用模型失败:', error);
    return { success: false, models: [] };
  })
}

export const trainModel = (params) => {
  console.log('发送训练请求，参数:', params);
  return api({
    url: '/api/ml/train',
    method: 'post',
    data: params
  })
  .then(response => {
    console.log('训练响应成功:', response.status);
    return response.data;
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
  return api({
    url: '/api/ml/predict',
    method: 'post',
    data: params
  })
  .then(response => response.data)
  .catch(error => {
    console.error('模型预测失败:', error);
    return { success: false, message: error.message || '预测失败' };
  })
}

export const evaluateModel = (params) => {
  return api({
    url: '/api/ml/evaluate',
    method: 'post',
    data: params
  })
  .then(response => response.data)
  .catch(error => {
    console.error('模型评估失败:', error);
    return { success: false, message: error.message || '评估失败' };
  })
}

// Stacking集成学习API
export const trainStackingModel = (params) => {
  return request({
    url: '/api/stacking/train',
    method: 'post',
    data: params
  })
}

// AutoML相关API
export const runAutoML = (params) => {
  return request({
    url: '/api/automl/run',
    method: 'post',
    data: params
  })
}

// 可视化相关API
export const generateDataVisualization = (params) => {
  return request({
    url: '/api/visualization/data',
    method: 'post',
    data: params
  })
}

export const generateModelVisualization = (params) => {
  return request({
    url: '/api/visualization/model',
    method: 'post',
    data: params
  })
}

// 报表相关API
export const generateReport = (params) => {
  return request({
    url: '/api/reports/generate',
    method: 'post',
    data: params
  })
}

export const getReportsList = () => {
  return request({
    url: '/api/reports/list',
    method: 'get'
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
} 