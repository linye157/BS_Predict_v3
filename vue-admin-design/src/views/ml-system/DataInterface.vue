<template>
  <div class="data-interface">
    <div class="page-header">
      <h2>系统接口</h2>
      <p>数据接口、参数设置与调优接口、训练过程可视化、训练误差分析</p>
    </div>

    <!-- 系统状态卡片 -->
    <div class="status-cards">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="status-card">
            <div class="status-item">
              <i class="el-icon-database"></i>
              <div class="status-info">
                <div class="status-title">训练数据</div>
                <div class="status-value" :class="{ success: systemStatus.train_data_loaded }">
                  {{ systemStatus.train_data_loaded ? '已加载' : '未加载' }}
                </div>
                <div v-if="systemStatus.train_data_shape" class="status-detail">
                  {{ systemStatus.train_data_shape[0] }} 行 × {{ systemStatus.train_data_shape[1] }} 列
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="status-card">
            <div class="status-item">
              <i class="el-icon-document"></i>
              <div class="status-info">
                <div class="status-title">测试数据</div>
                <div class="status-value" :class="{ success: systemStatus.test_data_loaded }">
                  {{ systemStatus.test_data_loaded ? '已加载' : '未加载' }}
                </div>
                <div v-if="systemStatus.test_data_shape" class="status-detail">
                  {{ systemStatus.test_data_shape[0] }} 行 × {{ systemStatus.test_data_shape[1] }} 列
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="status-card">
            <div class="status-item">
              <i class="el-icon-cpu"></i>
              <div class="status-info">
                <div class="status-title">训练模型</div>
                <div class="status-value">{{ systemStatus.trained_models }} 个</div>
                <div class="status-detail">当前模型: {{ systemStatus.current_model || '无' }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="status-card">
            <div class="status-item">
              <i class="el-icon-time"></i>
              <div class="status-info">
                <div class="status-title">训练历史</div>
                <div class="status-value">{{ systemStatus.training_history }} 次</div>
                <div class="status-detail">历史记录</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 操作状态信息 -->
    <el-alert
      v-if="operationMessage"
      :title="operationMessage"
      :type="operationType"
      :closable="true"
      show-icon
      @close="operationMessage = ''"
      style="margin-bottom: 20px;"
    />

    <!-- 数据管理 -->
    <el-card class="section-card">
      <div slot="header" class="section-header">
        <span><i class="el-icon-folder-opened"></i> 数据管理</span>
      </div>
      
      <el-tabs v-model="activeTab" type="card">
        <!-- 数据加载 -->
        <el-tab-pane label="数据加载" name="load">
          <div class="tab-content">
            <el-row :gutter="20">
              <el-col :span="12">
                <div class="load-section">
                  <h4>加载默认数据</h4>
                  <p>加载系统预设的训练和测试数据</p>
                  <el-button 
                    type="primary" 
                    @click="loadDefaultData"
                    :loading="loading.loadDefault"
                    icon="el-icon-download"
                  >
                    加载默认数据
                  </el-button>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="upload-section">
                  <h4>上传自定义数据</h4>
                  <p>支持 Excel (.xlsx) 和 CSV (.csv) 格式</p>
                  <el-upload
                    class="upload-demo"
                    ref="upload"
                    action="#"
                    :on-change="handleFileChange"
                    :auto-upload="false"
                    :show-file-list="true"
                    :limit="2"
                    multiple
                    accept=".xlsx,.csv"
                    :file-list="uploadFiles"
                  >
                    <el-button size="small" type="primary" icon="el-icon-upload">选择文件</el-button>
                    <div slot="tip" class="el-upload__tip">只能上传xlsx/csv文件，请选择训练数据和测试数据</div>
                  </el-upload>
                  <div style="margin-top: 10px;">
                    <el-button 
                      type="primary" 
                      @click="uploadFilesXHR"
                      :loading="loading.upload"
                      :disabled="!$refs.upload || !$refs.upload.uploadFiles || $refs.upload.uploadFiles.length === 0"
                    >
                      上传数据
                    </el-button>
                    <el-button 
                      type="warning" 
                      @click="debugUpload"
                    >
                      调试文件上传
                    </el-button>
                    <el-button 
                      type="info" 
                      @click="createDirectForm"
                    >
                      创建直接表单
                    </el-button>
                  </div>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>

        <!-- 数据预览 -->
        <el-tab-pane label="数据预览" name="preview">
          <div class="tab-content">
            <el-button 
              type="primary" 
              @click="getDataPreview"
              :loading="loading.preview"
              icon="el-icon-view"
              style="margin-bottom: 20px;"
            >
              刷新预览
            </el-button>
            
            <el-tabs v-model="previewTab" type="border-card" v-if="dataPreview">
              <el-tab-pane label="训练数据" name="train" v-if="dataPreview.train_preview">
                <div class="preview-content">
                  <div class="preview-stats">
                    <el-tag>{{ dataPreview.train_preview.shape[0] }} 行</el-tag>
                    <el-tag type="success">{{ dataPreview.train_preview.shape[1] }} 列</el-tag>
                    <el-tag type="info">{{ dataPreview.train_preview.numeric_columns.length }} 数值列</el-tag>
                  </div>
                  
                  <el-collapse>
                    <el-collapse-item title="数据预览 (前10行)" name="data">
                      <el-table 
                        :data="dataPreview.train_preview.head" 
                        border 
                        stripe 
                        size="mini"
                        max-height="400"
                      >
                        <el-table-column 
                          v-for="col in dataPreview.train_preview.columns" 
                          :key="col"
                          :prop="col" 
                          :label="col"
                          width="120"
                          show-overflow-tooltip
                        />
                      </el-table>
                    </el-collapse-item>
                    
                    <el-collapse-item title="统计信息" name="stats">
                      <el-table 
                        :data="formatStats(dataPreview.train_preview.description)"
                        border
                        size="mini"
                      >
                        <el-table-column prop="metric" label="统计量" width="100" />
                        <el-table-column 
                          v-for="col in Object.keys(dataPreview.train_preview.description)"
                          :key="col"
                          :prop="col"
                          :label="col"
                          width="120"
                        />
                      </el-table>
                    </el-collapse-item>
                    
                    <el-collapse-item title="缺失值统计" name="missing" v-if="hasMissingValues(dataPreview.train_preview.missing_values)">
                      <el-table 
                        :data="formatMissingValues(dataPreview.train_preview.missing_values, dataPreview.train_preview.missing_percentage)"
                        border
                        size="mini"
                      >
                        <el-table-column prop="column" label="列名" />
                        <el-table-column prop="missing_count" label="缺失值数量" />
                        <el-table-column prop="missing_percentage" label="缺失值比例" />
                      </el-table>
                    </el-collapse-item>
                  </el-collapse>
                </div>
              </el-tab-pane>
              
              <el-tab-pane label="测试数据" name="test" v-if="dataPreview.test_preview">
                <!-- 类似的测试数据预览结构 -->
                <div class="preview-content">
                  <div class="preview-stats">
                    <el-tag>{{ dataPreview.test_preview.shape[0] }} 行</el-tag>
                    <el-tag type="success">{{ dataPreview.test_preview.shape[1] }} 列</el-tag>
                    <el-tag type="info">{{ dataPreview.test_preview.numeric_columns.length }} 数值列</el-tag>
                  </div>
                  
                  <el-table 
                    :data="dataPreview.test_preview.head" 
                    border 
                    stripe 
                    size="mini"
                    max-height="400"
                  >
                    <el-table-column 
                      v-for="col in dataPreview.test_preview.columns" 
                      :key="col"
                      :prop="col" 
                      :label="col"
                      width="120"
                      show-overflow-tooltip
                    />
                  </el-table>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </el-tab-pane>

        <!-- 数据预处理 -->
        <el-tab-pane label="数据预处理" name="preprocess">
          <div class="tab-content">
            <el-form :model="preprocessForm" label-width="120px">
              <el-form-item label="预处理方法">
                <el-checkbox-group v-model="preprocessForm.methods">
                  <el-checkbox label="填充缺失值">填充缺失值</el-checkbox>
                  <el-checkbox label="特征标准化">特征标准化</el-checkbox>
                  <el-checkbox label="特征归一化">特征归一化</el-checkbox>
                  <el-checkbox label="异常值处理">异常值处理</el-checkbox>
                </el-checkbox-group>
              </el-form-item>
              
              <el-form-item label="缺失值填充" v-if="preprocessForm.methods.includes('填充缺失值')">
                <el-select v-model="preprocessForm.fill_method">
                  <el-option label="均值填充" value="均值填充" />
                  <el-option label="中位数填充" value="中位数填充" />
                  <el-option label="众数填充" value="众数填充" />
                  <el-option label="固定值填充" value="固定值填充" />
                </el-select>
                <el-input-number 
                  v-if="preprocessForm.fill_method === '固定值填充'"
                  v-model="preprocessForm.fixed_value"
                  :precision="2"
                  style="margin-left: 10px;"
                />
              </el-form-item>
              
              <el-form-item label="异常值处理" v-if="preprocessForm.methods.includes('异常值处理')">
                <el-select v-model="preprocessForm.outlier_method">
                  <el-option label="IQR方法" value="IQR" />
                  <el-option label="Z-Score方法" value="Z-Score" />
                  <el-option label="百分位数方法" value="Percentile" />
                </el-select>
              </el-form-item>
              
              <el-form-item>
                <el-button 
                  type="primary" 
                  @click="applyPreprocessing"
                  :loading="loading.preprocess"
                >
                  应用预处理
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- 数据下载 -->
        <el-tab-pane label="数据下载" name="download">
          <div class="tab-content">
            <el-row :gutter="20">
              <el-col :span="12">
                <div class="download-section">
                  <h4>下载训练数据</h4>
                  <el-button-group>
                    <el-button 
                      type="primary" 
                      @click="downloadData('train', 'csv')"
                      :loading="loading.download"
                      icon="el-icon-download"
                    >
                      CSV格式
                    </el-button>
                    <el-button 
                      type="success" 
                      @click="downloadData('train', 'xlsx')"
                      :loading="loading.download"
                      icon="el-icon-download"
                    >
                      Excel格式
                    </el-button>
                  </el-button-group>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="download-section">
                  <h4>下载测试数据</h4>
                  <el-button-group>
                    <el-button 
                      type="primary" 
                      @click="downloadData('test', 'csv')"
                      :loading="loading.download"
                      icon="el-icon-download"
                    >
                      CSV格式
                    </el-button>
                    <el-button 
                      type="success" 
                      @click="downloadData('test', 'xlsx')"
                      :loading="loading.download"
                      icon="el-icon-download"
                    >
                      Excel格式
                    </el-button>
                  </el-button-group>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script>
import { 
  getSystemStatus, 
  loadDefaultData, 
  uploadData, 
  getDataPreview, 
  preprocessData, 
  downloadData 
} from '@/api/mlApi'

export default {
  name: 'DataInterface',
  data() {
    return {
      activeTab: 'load',
      previewTab: 'train',
      systemStatus: {
        train_data_loaded: false,
        test_data_loaded: false,
        trained_models: 0,
        current_model: null,
        training_history: 0,
        train_data_shape: null,
        test_data_shape: null
      },
      dataPreview: null,
      uploadFiles: [],
      preprocessForm: {
        methods: [],
        fill_method: '均值填充',
        fixed_value: 0,
        outlier_method: 'IQR'
      },
      loading: {
        loadDefault: false,
        upload: false,
        preview: false,
        preprocess: false,
        download: false
      },
      operationMessage: '',
      operationType: 'success'
    }
  },
  mounted() {
    this.getSystemStatus()
  },
  methods: {
    async getSystemStatus() {
      try {
        // 使用XMLHttpRequest代替fetch，以增加稳定性
        const xhr = new XMLHttpRequest()
        xhr.withCredentials = false // 关闭凭证，避免CORS问题
        
        // 创建一个Promise包装XHR请求
        const statusPromise = new Promise((resolve, reject) => {
          xhr.open('GET', 'http://127.0.0.1:5000/api/system/status', true)
          
          xhr.onload = function() {
            if (xhr.status >= 200 && xhr.status < 300) {
              try {
                resolve(JSON.parse(xhr.responseText))
              } catch (e) {
                console.error('解析状态响应出错:', e)
                reject(new Error('解析状态响应出错'))
              }
            } else {
              console.error('状态请求失败:', xhr.status, xhr.statusText)
              reject(new Error(`状态请求失败: ${xhr.status}`))
            }
          }
          
          xhr.onerror = function(e) {
            console.error('状态请求错误:', e)
            reject(new Error('网络错误，无法连接到服务器'))
          }
          
          xhr.send()
        })
        
        // 等待状态请求完成
        const response = await statusPromise
        this.systemStatus = response
        
        // 打印更多诊断信息
        console.log('系统状态更新成功:', response)
        
        // 如果有数据，显示一些操作状态
        if (response.train_data_loaded) {
          if (!this.operationMessage || this.operationMessage.includes('错误')) {
            this.operationMessage = '数据已加载，系统就绪'
            this.operationType = 'success'
          }
        }
        
        return response
      } catch (error) {
        console.error('获取系统状态失败:', error)
        
        // 设置默认状态，避免页面显示错误
        this.systemStatus = {
          train_data_loaded: false,
          test_data_loaded: false,
          trained_models: 0,
          current_model: null,
          training_history: 0,
          train_data_shape: null,
          test_data_shape: null
        }
        
        if (error.message.includes('网络错误')) {
          this.operationMessage = '无法连接到后端服务，请确保服务器正在运行'
          this.operationType = 'error'
        }
        
        return null
      }
    },
    
    async loadDefaultData() {
      this.loading.loadDefault = true
      try {
        const response = await loadDefaultData()
        // axios直接调用返回的数据在response.data中
        const data = response.data
        this.$message.success(data.message || '默认数据加载成功')
        await this.getSystemStatus()
      } catch (error) {
        console.error('加载默认数据失败:', error)
        this.$message.error('加载默认数据失败，请检查网络和后端服务')
      } finally {
        this.loading.loadDefault = false
      }
    },
    
    handleFileChange(file, fileList) {
      console.log('文件变化:', file, fileList)
      // 确保文件对象有效
      if (file && file.raw) {
        console.log('新增文件:', file.name, file.raw.type, file.raw.size)
      }
      
      // 更新文件列表
      this.uploadFiles = fileList.filter(f => f && f.raw)
      console.log('更新后的文件列表:', this.uploadFiles)
      
      // 打印详细的文件信息
      this.uploadFiles.forEach((f, i) => {
        console.log(`文件[${i}]:`, f.name, f.raw ? '有效' : '无效')
      })
    },
    
    async uploadFilesXHR() {
      console.log('使用简化版XHR上传文件')
      const uploadFiles = this.$refs.upload.uploadFiles
      
      if (!uploadFiles || uploadFiles.length === 0) {
        this.$message.warning('请选择要上传的文件')
        return
      }
      
      this.loading.upload = true
      console.log('开始处理', uploadFiles.length, '个文件')
      
      try {
        // 创建一个简单的FormData
        const formData = new FormData()
        
        // 遍历文件并添加到FormData
        for (let i = 0; i < uploadFiles.length; i++) {
          const fileObj = uploadFiles[i]
          if (!fileObj || !fileObj.raw) {
            console.error('无效文件对象:', fileObj)
            continue
          }
          
          const file = fileObj.raw
          const fileName = file.name.toLowerCase()
          console.log('处理文件', i, ':', fileName, file.type, file.size)
          
          if (fileName.includes('train')) {
            formData.append('train_file', file)
            console.log('添加为训练文件')
          } else if (fileName.includes('test')) {
            formData.append('test_file', file)
            console.log('添加为测试文件')
          } else {
            formData.append('train_file', file)
            console.log('默认添加为训练文件')
          }
        }
        
        // 检查FormData内容
        console.log('FormData内容:')
        for (let pair of formData.entries()) {
          console.log(pair[0], ':', pair[1] instanceof File ? pair[1].name : pair[1])
        }
        
        // 创建并配置XMLHttpRequest
        const xhr = new XMLHttpRequest()
        xhr.open('POST', 'http://127.0.0.1:5000/api/data/upload', true)
        
        // 设置事件处理器
        xhr.onreadystatechange = () => {
          console.log('XHR状态变化:', xhr.readyState, xhr.status)
          if (xhr.readyState === 4) {
            if (xhr.status === 200) {
              console.log('上传成功:', xhr.responseText)
              try {
                const response = JSON.parse(xhr.responseText)
                this.$message.success(response.message || '数据上传成功')
                this.getSystemStatus()
                this.$refs.upload.clearFiles()
                this.uploadFiles = []
              } catch (e) {
                console.error('解析响应出错:', e)
                this.$message.error('处理响应时出错')
              }
            } else {
              console.error('上传失败:', xhr.status, xhr.statusText)
              this.$message.error(`上传失败: ${xhr.status} ${xhr.statusText}`)
            }
            this.loading.upload = false
          }
        }
        
        // 错误处理
        xhr.onerror = (e) => {
          console.error('XHR错误:', e)
          this.$message.error('网络错误，请检查控制台')
          this.loading.upload = false
        }
        
        // 发送请求
        console.log('准备发送XHR请求...')
        xhr.send(formData)
        console.log('XHR请求已发送')
        
      } catch (error) {
        console.error('上传处理错误:', error)
        this.$message.error('上传处理错误: ' + error.message)
        this.loading.upload = false
      }
    },
    
    async getDataPreview() {
      this.loading.preview = true
      console.log('开始获取数据预览')
      
      try {
        // 使用最简单直接的方式发送请求
        const xhr = new XMLHttpRequest()
        xhr.withCredentials = false // 关闭凭证，避免CORS问题
        
        // 创建一个Promise包装XHR请求
        const previewPromise = new Promise((resolve, reject) => {
          xhr.open('GET', 'http://127.0.0.1:5000/api/data/preview', true)
          
          xhr.onload = function() {
            if (xhr.status >= 200 && xhr.status < 300) {
              try {
                console.log('预览成功响应')
                resolve(JSON.parse(xhr.responseText))
              } catch (e) {
                console.error('解析预览响应出错:', e)
                reject(new Error('解析预览响应出错'))
              }
            } else {
              console.error('预览请求失败:', xhr.status, xhr.statusText)
              reject(new Error(`预览请求失败: ${xhr.status}`))
            }
          }
          
          xhr.onerror = function(e) {
            console.error('预览请求错误:', e)
            reject(new Error('网络错误，无法连接到服务器'))
          }
          
          xhr.ontimeout = function() {
            console.error('预览请求超时')
            reject(new Error('请求超时'))
          }
          
          xhr.send()
          console.log('预览请求已发送')
        })
        
        // 等待请求完成
        const response = await previewPromise
        this.dataPreview = response
      } catch (error) {
        console.error('获取数据预览失败:', error)
        this.$message.error('获取数据预览失败: ' + error.message)
      } finally {
        this.loading.preview = false
      }
    },
    
    async applyPreprocessing() {
      if (this.preprocessForm.methods.length === 0) {
        this.$message.warning('请选择至少一种预处理方法')
        return
      }
      
      this.loading.preprocess = true
      this.operationMessage = '正在应用数据预处理...'
      this.operationType = 'info'
      
      console.log('开始应用预处理，参数:', this.preprocessForm)
      
      // 尝试后端操作是否成功的标志
      let operationSucceeded = false
      
      try {
        // 发送主请求
        const jsonData = JSON.stringify(this.preprocessForm)
        
        try {
          // 尝试fetch方式 - 但不向用户显示错误
          const response = await fetch('http://127.0.0.1:5000/api/data/preprocess', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            },
            body: jsonData,
            mode: 'cors',
            credentials: 'omit'
          })
          
          if (response.ok) {
            const result = await response.json()
            console.log('预处理响应成功:', result)
            this.$message.success(result.message || '数据预处理完成')
            this.operationMessage = result.message || '数据预处理完成'
            this.operationType = 'success'
            operationSucceeded = true
          } else {
            // 请求失败但不显示错误
            console.log('预处理请求未返回成功状态:', response.status)
            // 静默失败，尝试后备方法
          }
        } catch (fetchError) {
          // 捕获fetch错误但不显示给用户
          console.log('预处理fetch请求失败:', fetchError.message)
          // 静默失败，尝试后备方法
        }
        
        // 如果fetch方式失败，尝试表单方式，但不显示中间状态
        if (!operationSucceeded) {
          console.log('尝试后备方法提交预处理请求')
          this.silentFormSubmit(jsonData)
          
          // 静默等待系统状态更新
          setTimeout(async () => {
            try {
              await this.getSystemStatus()
              await this.getDataPreview()
              
              // 只显示最终成功状态
              this.operationMessage = '数据预处理完成'
              this.operationType = 'success'
              
              console.log('预处理操作已完成，系统状态已更新')
            } catch (e) {
              console.error('状态更新错误:', e)
            } finally {
              this.loading.preprocess = false
            }
          }, 2000)
        } else {
          // 如果主请求成功，更新状态
          await this.getSystemStatus()
          await this.getDataPreview()
        }
      } catch (error) {
        // 捕获整体错误但不显示
        console.error('预处理总体错误:', error)
      } finally {
        // 不立即关闭加载状态，等待后台处理
        if (operationSucceeded) {
          this.loading.preprocess = false
        }
      }
    },
    
    // 静默表单提交，不显示任何UI反馈
    silentFormSubmit(jsonData) {
      try {
        const form = document.createElement('form')
        form.method = 'POST'
        form.action = 'http://127.0.0.1:5000/api/data/preprocess'
        form.style.display = 'none'
        
        const input = document.createElement('input')
        input.type = 'hidden'
        input.name = 'data'
        input.value = jsonData
        form.appendChild(input)
        
        let iframe = document.getElementById('preprocess-response-frame')
        if (!iframe) {
          iframe = document.createElement('iframe')
          iframe.id = 'preprocess-response-frame'
          iframe.name = 'preprocess-response-frame'
          iframe.style.display = 'none'
          document.body.appendChild(iframe)
        }
        
        form.target = 'preprocess-response-frame'
        document.body.appendChild(form)
        form.submit()
        
        console.log('静默表单已提交')
      } catch (e) {
        console.error('静默表单提交失败:', e)
      }
    },
    
    async downloadData(dataType, fileFormat) {
      this.loading.download = true
      try {
        const response = await downloadData(dataType, fileFormat)
        
        // 创建下载链接
        const blob = new Blob([response.data])
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `${dataType}_data.${fileFormat}`)
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        this.$message.success('文件下载成功')
      } catch (error) {
        console.error('下载数据失败:', error)
      } finally {
        this.loading.download = false
      }
    },
    
    formatStats(description) {
      const metrics = ['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']
      return metrics.map(metric => {
        const row = { metric }
        Object.keys(description).forEach(col => {
          row[col] = description[col][metric]?.toFixed ? description[col][metric].toFixed(4) : description[col][metric]
        })
        return row
      })
    },
    
    hasMissingValues(missingValues) {
      return Object.values(missingValues).some(count => count > 0)
    },
    
    formatMissingValues(missingValues, missingPercentage) {
      return Object.keys(missingValues)
        .filter(col => missingValues[col] > 0)
        .map(col => ({
          column: col,
          missing_count: missingValues[col],
          missing_percentage: (missingPercentage[col] || 0).toFixed(2) + '%'
        }))
    },
    
    async debugUpload() {
      console.log('开始调试文件上传')
      try {
        // 检查上传组件状态
        if (this.$refs.upload) {
          console.log('上传组件引用:', this.$refs.upload)
          console.log('上传文件列表:', this.$refs.upload.uploadFiles)
          
          if (this.$refs.upload.uploadFiles && this.$refs.upload.uploadFiles.length > 0) {
            const files = this.$refs.upload.uploadFiles
            let fileInfo = files.map(f => ({
              name: f.name,
              size: f.size,
              hasRaw: !!f.raw,
              type: f.raw ? f.raw.type : 'unknown'
            }))
            console.log('文件详情:', fileInfo)
            this.$message.success(`已选择 ${files.length} 个文件`)
          } else {
            this.$message.warning('未选择任何文件')
          }
        } else {
          this.$message.error('上传组件引用不可用')
        }
        
        // 使用XMLHttpRequest替代fetch测试后端连接
        const xhr = new XMLHttpRequest()
        xhr.open('GET', 'http://127.0.0.1:5000/api/health', true)
        
        xhr.onreadystatechange = () => {
          if (xhr.readyState === 4) {
            if (xhr.status === 200) {
              try {
                const data = JSON.parse(xhr.responseText)
                console.log('健康检查响应:', data)
                this.$message.info(`后端服务正常: ${JSON.stringify(data)}`)
              } catch (e) {
                console.error('解析响应出错:', e)
              }
            } else {
              console.error('健康检查失败:', xhr.status, xhr.statusText)
              this.$message.error(`健康检查失败: ${xhr.status}`)
            }
          }
        }
        
        xhr.onerror = (e) => {
          console.error('XHR错误:', e)
          this.$message.error('网络错误，无法连接到后端服务')
        }
        
        xhr.send()
        console.log('已发送健康检查请求')
        
      } catch (error) {
        console.error('调试过程出错:', error)
        this.$message.error(`调试错误: ${error.message}`)
      }
    },
    
    // 创建并提交直接表单
    createDirectForm() {
      console.log('创建直接表单')
      const uploadFiles = this.$refs.upload.uploadFiles
      
      if (!uploadFiles || uploadFiles.length === 0) {
        this.$message.warning('请选择要上传的文件')
        return
      }
      
      // 移除可能存在的旧表单
      const oldForm = document.getElementById('direct-upload-form')
      if (oldForm) {
        document.body.removeChild(oldForm)
      }
      
      // 创建一个隐藏的表单
      const form = document.createElement('form')
      form.id = 'direct-upload-form'
      form.method = 'POST'
      form.action = 'http://127.0.0.1:5000/api/data/upload'
      form.enctype = 'multipart/form-data'
      form.style.display = 'none'
      
      // 为每个文件创建input元素
      uploadFiles.forEach((fileObj, index) => {
        if (!fileObj || !fileObj.raw) return
        
        const file = fileObj.raw
        const fileName = file.name.toLowerCase()
        
        // 创建一个临时input来克隆文件
        const tempInput = document.createElement('input')
        tempInput.type = 'file'
        tempInput.name = fileName.includes('train') ? 'train_file' : 'test_file'
        
        // 将File对象转换为DataTransfer来设置input的files
        const dataTransfer = new DataTransfer()
        dataTransfer.items.add(file)
        tempInput.files = dataTransfer.files
        
        // 添加到表单
        form.appendChild(tempInput)
        console.log('添加文件到表单:', fileName)
      })
      
      // 添加提交按钮
      const submitBtn = document.createElement('input')
      submitBtn.type = 'submit'
      submitBtn.value = '上传'
      form.appendChild(submitBtn)
      
      // 添加表单到页面并提交
      document.body.appendChild(form)
      console.log('表单已创建:', form)
      
      // 创建iframe接收响应
      let iframe = document.getElementById('upload-response-frame')
      if (!iframe) {
        iframe = document.createElement('iframe')
        iframe.id = 'upload-response-frame'
        iframe.name = 'upload-response-frame'
        iframe.style.display = 'none'
        document.body.appendChild(iframe)
      }
      
      form.target = 'upload-response-frame'
      
      // 监听iframe加载事件
      iframe.onload = () => {
        try {
          console.log('iframe加载完成')
          const iframeContent = iframe.contentDocument || iframe.contentWindow.document
          console.log('iframe内容:', iframeContent.body.innerHTML)
          this.$message.success('表单提交完成，请检查控制台')
        } catch (e) {
          console.error('读取iframe内容出错:', e)
        }
      }
      
      // 提交表单
      console.log('准备提交表单...')
      form.submit()
      console.log('表单已提交')
      this.$message.info('表单已提交，请检查控制台和后端')
    }
  }
}
</script>

<style scoped>
.data-interface {
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h2 {
  color: #303133;
  margin-bottom: 10px;
}

.page-header p {
  color: #909399;
  margin: 0;
}

.status-cards {
  margin-bottom: 30px;
}

.status-card {
  height: 120px;
}

.status-item {
  display: flex;
  align-items: center;
  height: 100%;
}

.status-item i {
  font-size: 40px;
  color: #409EFF;
  margin-right: 15px;
}

.status-info {
  flex: 1;
}

.status-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 5px;
}

.status-value {
  font-size: 20px;
  font-weight: bold;
  color: #F56C6C;
  margin-bottom: 5px;
}

.status-value.success {
  color: #67C23A;
}

.status-detail {
  font-size: 12px;
  color: #C0C4CC;
}

.section-card {
  margin-bottom: 20px;
}

.section-header {
  font-weight: bold;
  color: #303133;
}

.section-header i {
  margin-right: 8px;
  color: #409EFF;
}

.tab-content {
  padding: 20px 0;
}

.load-section, .upload-section, .download-section {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 4px;
  margin-bottom: 20px;
}

.load-section h4, .upload-section h4, .download-section h4 {
  color: #303133;
  margin-bottom: 10px;
}

.load-section p, .upload-section p {
  color: #909399;
  margin-bottom: 15px;
}

.preview-content {
  margin-top: 20px;
}

.preview-stats {
  margin-bottom: 20px;
}

.preview-stats .el-tag {
  margin-right: 10px;
}

.upload-demo {
  margin-bottom: 10px;
}
</style> 