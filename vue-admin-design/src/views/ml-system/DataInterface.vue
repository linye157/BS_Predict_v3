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
                    multiple
                    accept=".xlsx,.csv"
                  >
                    <el-button size="small" type="primary" icon="el-icon-upload">选择文件</el-button>
                    <div slot="tip" class="el-upload__tip">只能上传xlsx/csv文件</div>
                  </el-upload>
                  <el-button 
                    type="success" 
                    @click="uploadFiles"
                    :loading="loading.upload"
                    :disabled="uploadFiles.length === 0"
                    style="margin-top: 10px;"
                  >
                    上传数据
                  </el-button>
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
      }
    }
  },
  mounted() {
    this.getSystemStatus()
  },
  methods: {
    async getSystemStatus() {
      try {
        const response = await getSystemStatus()
        this.systemStatus = response
      } catch (error) {
        console.error('获取系统状态失败:', error)
      }
    },
    
    async loadDefaultData() {
      this.loading.loadDefault = true
      try {
        const response = await loadDefaultData()
        this.$message.success(response.message || '默认数据加载成功')
        await this.getSystemStatus()
      } catch (error) {
        console.error('加载默认数据失败:', error)
      } finally {
        this.loading.loadDefault = false
      }
    },
    
    handleFileChange(file, fileList) {
      this.uploadFiles = fileList
    },
    
    async uploadFiles() {
      if (this.uploadFiles.length === 0) {
        this.$message.warning('请选择要上传的文件')
        return
      }
      
      this.loading.upload = true
      try {
        const formData = new FormData()
        
        // 根据文件名判断是训练数据还是测试数据
        this.uploadFiles.forEach(fileObj => {
          const file = fileObj.raw
          const fileName = file.name.toLowerCase()
          if (fileName.includes('train')) {
            formData.append('train_file', file)
          } else if (fileName.includes('test')) {
            formData.append('test_file', file)
          } else {
            // 默认作为训练数据
            formData.append('train_file', file)
          }
        })
        
        const response = await uploadData(formData)
        this.$message.success(response.message || '数据上传成功')
        await this.getSystemStatus()
        this.$refs.upload.clearFiles()
        this.uploadFiles = []
      } catch (error) {
        console.error('上传数据失败:', error)
      } finally {
        this.loading.upload = false
      }
    },
    
    async getDataPreview() {
      this.loading.preview = true
      try {
        const response = await getDataPreview()
        this.dataPreview = response
      } catch (error) {
        console.error('获取数据预览失败:', error)
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
      try {
        const response = await preprocessData(this.preprocessForm)
        this.$message.success(response.message || '数据预处理完成')
        await this.getSystemStatus()
        await this.getDataPreview()
      } catch (error) {
        console.error('数据预处理失败:', error)
      } finally {
        this.loading.preprocess = false
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