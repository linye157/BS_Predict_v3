import request from '../request'

// 系统状态
export const getSystemStatus = () => {
  return request({
    url: '/api/system/status',
    method: 'get'
  })
}

// 数据处理相关API
export const loadDefaultData = () => {
  return request({
    url: '/api/data/load-default',
    method: 'post'
  })
}

export const uploadData = (formData) => {
  return request({
    url: '/api/data/upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const getDataPreview = () => {
  return request({
    url: '/api/data/preview',
    method: 'get'
  })
}

export const preprocessData = (params) => {
  return request({
    url: '/api/data/preprocess',
    method: 'post',
    data: params
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
}

export const trainModel = (params) => {
  return request({
    url: '/api/ml/train',
    method: 'post',
    data: params
  })
}

export const predictModel = (params) => {
  return request({
    url: '/api/ml/predict',
    method: 'post',
    data: params
  })
}

export const evaluateModel = (params) => {
  return request({
    url: '/api/ml/evaluate',
    method: 'post',
    data: params
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