import request from '../request'
import axios from 'axios'

// 系统状态
export const getSystemStatus = () => {
  return axios({
    url: 'http://127.0.0.1:5000/api/system/status',
    method: 'get',
    timeout: 60000,
    headers: {
      'Content-Type': 'application/json'
    }
  })
}

// 数据处理相关API
export const loadDefaultData = () => {
  return axios({
    url: 'http://127.0.0.1:5000/api/data/load-default',
    method: 'post',
    timeout: 60000,
    headers: {
      'Content-Type': 'application/json'
    }
  })
}

export const uploadData = (formData) => {
  return axios({
    url: 'http://127.0.0.1:5000/api/data/upload',
    method: 'post',
    data: formData,
    timeout: 60000,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const getDataPreview = () => {
  return axios({
    url: 'http://127.0.0.1:5000/api/data/preview',
    method: 'get',
    timeout: 60000,
    headers: {
      'Content-Type': 'application/json'
    }
  })
}

export const preprocessData = (params) => {
  return axios({
    url: 'http://127.0.0.1:5000/api/data/preprocess',
    method: 'post',
    data: params,
    timeout: 60000,
    headers: {
      'Content-Type': 'application/json'
    }
  })
}

export const downloadData = (dataType, fileFormat) => {
  return axios({
    url: `http://127.0.0.1:5000/api/data/download/${dataType}/${fileFormat}`,
    method: 'get',
    responseType: 'blob',
    timeout: 60000
  })
}

// 机器学习相关API
export const getAvailableModels = () => {
  return axios({
    url: 'http://127.0.0.1:5000/api/ml/models',
    method: 'get',
    timeout: 60000,
    headers: {
      'Content-Type': 'application/json'
    }
  })
}

export const trainModel = (params) => {
  return axios({
    url: 'http://127.0.0.1:5000/api/ml/train',
    method: 'post',
    data: params,
    timeout: 60000,
    headers: {
      'Content-Type': 'application/json'
    }
  })
}

export const predictModel = (params) => {
  return axios({
    url: 'http://127.0.0.1:5000/api/ml/predict',
    method: 'post',
    data: params,
    timeout: 60000,
    headers: {
      'Content-Type': 'application/json'
    }
  })
}

export const evaluateModel = (params) => {
  return axios({
    url: 'http://127.0.0.1:5000/api/ml/evaluate',
    method: 'post',
    data: params,
    timeout: 60000,
    headers: {
      'Content-Type': 'application/json'
    }
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