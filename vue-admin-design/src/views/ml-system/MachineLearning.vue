<template>
  <div class="machine-learning">
    <div class="page-header">
      <h2>机器学习</h2>
      <p>线性(LR)模型、随机森林(RF)模型、GBR模型、XGBR模型、支持向量机(SVR)模型、人工神经网络(ANN)模型</p>
    </div>

    <!-- 模型选择和配置 -->
    <el-card class="section-card">
      <div slot="header" class="section-header">
        <span><i class="el-icon-cpu"></i> 模型训练</span>
      </div>
      
      <el-form :model="trainForm" label-width="150px" ref="trainForm">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="选择模型类型" required>
              <el-select v-model="trainForm.model_type" placeholder="请选择模型" @change="onModelChange">
                <el-option 
                  v-for="model in availableModels" 
                  :key="model.key"
                  :label="model.name" 
                  :value="model.key"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="测试集比例">
              <el-slider 
                v-model="trainForm.test_size" 
                :min="0.1" 
                :max="0.5" 
                :step="0.05"
                show-input
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="目标列选择">
          <el-select 
            v-model="trainForm.target_columns" 
            multiple 
            placeholder="请选择目标列"
            style="width: 100%"
          >
            <el-option 
              v-for="col in dataColumns" 
              :key="col"
              :label="col" 
              :value="col"
            />
          </el-select>
        </el-form-item>

        <!-- 模型参数配置 -->
        <el-card v-if="trainForm.model_type" style="margin-top: 20px;">
          <div slot="header">模型参数配置</div>
          <div v-if="trainForm.model_type === 'LinearRegression'">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-form-item label="拟合截距">
                  <el-checkbox v-model="trainForm.model_params.fit_intercept">fit_intercept</el-checkbox>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="复制输入">
                  <el-checkbox v-model="trainForm.model_params.copy_X">copy_X</el-checkbox>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="并行作业">
                  <el-select v-model="trainForm.model_params.n_jobs" placeholder="选择并行作业数">
                    <el-option label="自动" :value="null" />
                    <el-option label="全部CPU" :value="-1" />
                    <el-option label="单线程" :value="1" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="强制正系数">
                  <el-checkbox v-model="trainForm.model_params.positive">positive</el-checkbox>
                </el-form-item>
              </el-col>
            </el-row>
          </div>
          
          <div v-else-if="trainForm.model_type === 'RandomForest'">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="估计器数量">
                  <el-input-number v-model="trainForm.model_params.n_estimators" :min="10" :max="500" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="最大深度">
                  <el-input-number v-model="trainForm.model_params.max_depth" :min="1" :max="50" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="最小分割样本">
                  <el-input-number v-model="trainForm.model_params.min_samples_split" :min="2" :max="20" />
                </el-form-item>
              </el-col>
            </el-row>
          </div>
          
          <div v-else-if="trainForm.model_type === 'GradientBoosting'">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="估计器数量">
                  <el-input-number v-model="trainForm.model_params.n_estimators" :min="10" :max="500" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="学习率">
                  <el-input-number v-model="trainForm.model_params.learning_rate" :min="0.01" :max="1" :step="0.01" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="最大深度">
                  <el-input-number v-model="trainForm.model_params.max_depth" :min="1" :max="20" />
                </el-form-item>
              </el-col>
            </el-row>
          </div>
          
          <div v-else-if="trainForm.model_type === 'XGBoost'">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="估计器数量">
                  <el-input-number v-model="trainForm.model_params.n_estimators" :min="10" :max="500" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="学习率">
                  <el-input-number v-model="trainForm.model_params.learning_rate" :min="0.01" :max="1" :step="0.01" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="最大深度">
                  <el-input-number v-model="trainForm.model_params.max_depth" :min="1" :max="20" />
                </el-form-item>
              </el-col>
            </el-row>
          </div>
          
          <div v-else-if="trainForm.model_type === 'SVR'">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="C参数">
                  <el-input-number v-model="trainForm.model_params.C" :min="0.01" :max="100" :step="0.1" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="核函数">
                  <el-select v-model="trainForm.model_params.kernel">
                    <el-option label="RBF" value="rbf" />
                    <el-option label="Linear" value="linear" />
                    <el-option label="Poly" value="poly" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="Gamma">
                  <el-select v-model="trainForm.model_params.gamma">
                    <el-option label="Scale" value="scale" />
                    <el-option label="Auto" value="auto" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
          </div>
          
          <div v-else-if="trainForm.model_type === 'MLP'">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="隐藏层大小">
                  <el-input v-model="trainForm.model_params.hidden_layer_sizes" placeholder="例如: 100,50" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="激活函数">
                  <el-select v-model="trainForm.model_params.activation">
                    <el-option label="ReLU" value="relu" />
                    <el-option label="Tanh" value="tanh" />
                    <el-option label="Logistic" value="logistic" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="学习率">
                  <el-select v-model="trainForm.model_params.learning_rate">
                    <el-option label="Constant" value="constant" />
                    <el-option label="Adaptive" value="adaptive" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
          </div>
        </el-card>

        <el-form-item style="margin-top: 20px;">
          <el-checkbox v-model="trainForm.use_grid_search">使用网格搜索优化参数</el-checkbox>
        </el-form-item>

        <el-form-item>
          <el-button 
            type="primary" 
            @click="trainModel"
            :loading="loading.train"
            size="large"
          >
            <i class="el-icon-cpu"></i> 开始训练
          </el-button>
          <el-button 
            v-if="currentModel"
            type="success" 
            @click="predictModel"
            :loading="loading.predict"
            size="large"
          >
            <i class="el-icon-view"></i> 模型预测
          </el-button>
          <el-button 
            v-if="currentModel"
            type="info" 
            @click="evaluateModel"
            :loading="loading.evaluate"
            size="large"
          >
            <i class="el-icon-data-analysis"></i> 模型评估
          </el-button>
          <el-button 
            type="warning" 
            @click="debugConnection"
            size="small"
          >
            <i class="el-icon-s-tools"></i> 调试连接
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 训练结果展示 -->
    <el-card v-if="trainResult" class="section-card">
      <div slot="header" class="section-header">
        <span><i class="el-icon-success"></i> 训练结果</span>
      </div>
      
      <el-alert
        :title="trainResult.message"
        type="success"
        :closable="false"
        style="margin-bottom: 20px;"
      />
      
      <div style="margin-bottom: 20px; text-align: right;">
        <el-button 
          type="primary" 
          @click="downloadCurrentModel"
          :loading="loading.download"
          icon="el-icon-download"
          size="small"
        >
          下载模型
        </el-button>
      </div>
      
      <el-tabs v-model="resultTab" type="card">
        <el-tab-pane label="模型信息" name="info">
          <el-descriptions border :column="2">
            <el-descriptions-item label="模型ID">{{ trainResult.model_id }}</el-descriptions-item>
            <el-descriptions-item label="模型类型">{{ trainResult.model_info?.model_name }}</el-descriptions-item>
            <el-descriptions-item label="特征数量">{{ trainResult.feature_columns?.length }}</el-descriptions-item>
            <el-descriptions-item label="目标数量">{{ trainResult.target_columns?.length }}</el-descriptions-item>
            <el-descriptions-item label="训练时间">{{ trainResult.model_info?.training_time }}</el-descriptions-item>
            <el-descriptions-item label="数据形状">{{ trainResult.model_info?.data_shape?.join(' × ') }}</el-descriptions-item>
            <el-descriptions-item label="最优参数" :span="2">
              <pre>{{ JSON.stringify(trainResult.best_params, null, 2) }}</pre>
            </el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
        
        <el-tab-pane label="性能指标" name="metrics">
          <div v-if="!trainResult.metrics || (!trainResult.metrics.train && !trainResult.metrics.validation)" 
               style="text-align: center; padding: 40px; color: #909399;">
            <i class="el-icon-warning" style="font-size: 48px; margin-bottom: 16px;"></i>
            <p>暂无性能指标数据</p>
          </div>
          
          <div v-else>
            <!-- 训练集指标 -->
            <div v-if="trainResult.metrics.train">
              <h3 style="color: #409EFF; margin-bottom: 20px;">
                <i class="el-icon-data-line"></i> 训练集指标
              </h3>
              <div v-for="(metrics, target) in trainResult.metrics.train" :key="'train-' + target" style="margin-bottom: 30px;">
                <h4 style="color: #606266; margin-bottom: 15px;">{{ target }}</h4>
                <el-row :gutter="20">
                  <el-col :span="6">
                    <el-statistic 
                      title="MSE (均方误差)" 
                      :value="metrics.mse || 0" 
                      :precision="6" 
                      suffix=""
                    />
                  </el-col>
                  <el-col :span="6">
                    <el-statistic 
                      title="RMSE (均方根误差)" 
                      :value="metrics.rmse || 0" 
                      :precision="6" 
                      suffix=""
                    />
                  </el-col>
                  <el-col :span="6">
                    <el-statistic 
                      title="MAE (平均绝对误差)" 
                      :value="metrics.mae || 0" 
                      :precision="6" 
                      suffix=""
                    />
                  </el-col>
                  <el-col :span="6">
                    <el-statistic 
                      title="R² (决定系数)" 
                      :value="metrics.r2 || 0" 
                      :precision="6" 
                      suffix=""
                    />
                  </el-col>
                </el-row>
              </div>
            </div>
            
            <!-- 验证集指标 -->
            <div v-if="trainResult.metrics.validation" style="margin-top: 30px;">
              <h3 style="color: #67C23A; margin-bottom: 20px;">
                <i class="el-icon-data-analysis"></i> 验证集指标
              </h3>
              <div v-for="(metrics, target) in trainResult.metrics.validation" :key="'val-' + target" style="margin-bottom: 30px;">
                <h4 style="color: #606266; margin-bottom: 15px;">{{ target }}</h4>
                <el-row :gutter="20">
                  <el-col :span="6">
                    <el-statistic 
                      title="MSE (均方误差)" 
                      :value="metrics.mse || 0" 
                      :precision="6" 
                      suffix=""
                    />
                  </el-col>
                  <el-col :span="6">
                    <el-statistic 
                      title="RMSE (均方根误差)" 
                      :value="metrics.rmse || 0" 
                      :precision="6" 
                      suffix=""
                    />
                  </el-col>
                  <el-col :span="6">
                    <el-statistic 
                      title="MAE (平均绝对误差)" 
                      :value="metrics.mae || 0" 
                      :precision="6" 
                      suffix=""
                    />
                  </el-col>
                  <el-col :span="6">
                    <el-statistic 
                      title="R² (决定系数)" 
                      :value="metrics.r2 || 0" 
                      :precision="6" 
                      suffix=""
                    />
                  </el-col>
                </el-row>
              </div>
            </div>
            
            <!-- 交叉验证指标 -->
            <div v-if="trainResult.metrics.cross_validation" style="margin-top: 30px;">
              <h3 style="color: #E6A23C; margin-bottom: 20px;">
                <i class="el-icon-s-data"></i> 交叉验证指标 (CV MSE)
              </h3>
              <el-row :gutter="20">
                <el-col :span="6" v-for="(score, target) in trainResult.metrics.cross_validation" :key="'cv-' + target">
                  <el-statistic 
                    :title="target + ' CV MSE'" 
                    :value="score || 0" 
                    :precision="6" 
                    suffix=""
                  />
                </el-col>
              </el-row>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 预测结果展示 -->
    <el-card v-if="predictResult && predictResult.success" class="section-card">
      <div slot="header" class="section-header">
        <span><i class="el-icon-view"></i> 预测结果</span>
        <span style="float: right; font-size: 12px; color: #909399;">
          共 {{ predictResult.prediction_count || 0 }} 条预测结果
        </span>
      </div>
      
      <div v-if="!predictResult.predictions || predictResult.predictions.length === 0" 
           style="text-align: center; padding: 40px; color: #909399;">
        <i class="el-icon-info" style="font-size: 48px; margin-bottom: 16px;"></i>
        <p>暂无预测数据</p>
      </div>
      
      <div v-else>
        <el-table 
          :data="predictResult.predictions.slice(0, 100)" 
          border 
          stripe 
          max-height="400"
          style="width: 100%"
        >
          <el-table-column 
            v-for="col in (predictResult.columns || Object.keys(predictResult.predictions[0] || {}))" 
            :key="col"
            :prop="col" 
            :label="col"
            :width="col.includes('predicted') ? 150 : 120"
            :show-overflow-tooltip="true"
          >
            <template slot-scope="scope">
              <span v-if="typeof scope.row[col] === 'number'">
                {{ scope.row[col].toFixed(4) }}
              </span>
              <span v-else>{{ scope.row[col] }}</span>
            </template>
          </el-table-column>
        </el-table>
        
        <div style="text-align: center; margin-top: 10px;" v-if="predictResult.predictions.length > 100">
          <el-tag type="info">显示前100行，共{{ predictResult.predictions.length }}行</el-tag>
        </div>
      </div>
    </el-card>

    <!-- 评估结果展示 -->
    <el-card v-if="evaluateResult" class="section-card">
      <div slot="header" class="section-header">
        <span><i class="el-icon-data-analysis"></i> 模型评估</span>
      </div>
      
      <div v-for="(metrics, target) in evaluateResult.evaluation" :key="target">
        <h4>{{ target }} - 测试集评估</h4>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-statistic title="MSE" :value="metrics.mse" :precision="4" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="RMSE" :value="metrics.rmse" :precision="4" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="MAE" :value="metrics.mae" :precision="4" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="R²" :value="metrics.r2" :precision="4" />
          </el-col>
        </el-row>
      </div>
    </el-card>
  </div>
</template>

<script>
import { 
  getAvailableModels, 
  trainModel, 
  predictModel, 
  evaluateModel,
  getDataPreview,
  getSystemStatus,
  downloadModel
} from '@/api/mlApi'
import axios from 'axios'

export default {
  name: 'MachineLearning',
  data() {
    return {
      availableModels: [],
      dataColumns: [],
      trainForm: {
        model_type: '',
        test_size: 0.2,
        target_columns: [],
        model_params: {},
        use_grid_search: false,
        random_state: 42
      },
      trainResult: null,
      predictResult: null,
      evaluateResult: null,
      currentModel: null,
      resultTab: 'info',
      loading: {
        train: false,
        predict: false,
        evaluate: false,
        download: false
      }
    }
  },
  async mounted() {
    await this.loadAvailableModels()
    await this.loadDataInfo()
  },
  methods: {
    async loadAvailableModels() {
      try {
        const response = await getAvailableModels()
        console.log('Available models response:', response)
        if (response.success) {
          this.availableModels = response.models || []
          if (this.availableModels.length === 0) {
            this.$message.warning('没有可用的模型类型')
          }
        } else {
          this.$message.error(response.message || '加载可用模型失败')
        }
      } catch (error) {
        console.error('加载可用模型失败:', error)
        this.$message.error('加载可用模型失败: ' + (error.message || '未知错误'))
      }
    },
    
    async loadDataInfo() {
      try {
        const response = await getDataPreview()
        console.log('Data preview response:', response)
        if (response.success && response.train_preview) {
          this.dataColumns = response.train_preview.columns || []
          // 默认选择最后一列作为目标列
          if (this.dataColumns.length > 0) {
            this.trainForm.target_columns = [this.dataColumns[this.dataColumns.length - 1]]
          }
          if (this.dataColumns.length === 0) {
            this.$message.warning('没有可用的数据列，请先上传或加载数据')
          }
        } else {
          this.$message.warning(response.message || '未获取到数据预览信息')
        }
      } catch (error) {
        console.error('加载数据信息失败:', error)
        this.$message.error('加载数据信息失败: ' + (error.message || '未知错误'))
      }
    },
    
    onModelChange() {
      // 重置模型参数
      this.trainForm.model_params = this.getDefaultParams(this.trainForm.model_type)
    },
    
    getDefaultParams(modelType) {
      const defaults = {
        'LinearRegression': {
          fit_intercept: true,
          copy_X: true,
          n_jobs: null,
          positive: false
        },
        'RandomForest': {
          n_estimators: 100,
          max_depth: 10,
          min_samples_split: 2
        },
        'GradientBoosting': {
          n_estimators: 100,
          learning_rate: 0.1,
          max_depth: 3
        },
        'XGBoost': {
          n_estimators: 100,
          learning_rate: 0.1,
          max_depth: 3
        },
        'SVR': {
          C: 1.0,
          kernel: 'rbf',
          gamma: 'scale'
        },
        'MLP': {
          hidden_layer_sizes: '100',
          activation: 'relu',
          learning_rate: 'constant'
        }
      }
      return defaults[modelType] || {}
    },
    
    async trainModel() {
      if (!this.trainForm.model_type) {
        this.$message.warning('请选择模型类型')
        return
      }
      if (this.trainForm.target_columns.length === 0) {
        this.$message.warning('请选择目标列')
        return
      }
      
      // 检查数据规模并给出提示
      try {
        const statusResponse = await getSystemStatus()
        if (statusResponse.train_data_shape) {
          const dataSize = statusResponse.train_data_shape[0]
          if (dataSize > 15000) {
            const modelNames = {
              'LinearRegression': '线性回归',
              'RandomForest': '随机森林',
              'GradientBoosting': 'GBR模型',
              'XGBoost': 'XGBR模型',
              'SVR': '支持向量机',
              'MLP': '人工神经网络'
            }
            const modelName = modelNames[this.trainForm.model_type] || this.trainForm.model_type
            
            this.$message.info(`检测到大数据集(${dataSize}条数据)，${modelName}训练可能需要较长时间，请耐心等待...`)
          }
        }
      } catch (e) {
        console.log('无法获取数据状态:', e)
      }
      
      this.loading.train = true
      try {
        // 处理MLP的隐藏层参数
        let params = { ...this.trainForm }
        if (params.model_type === 'MLP' && params.model_params.hidden_layer_sizes) {
          const sizes = params.model_params.hidden_layer_sizes.split(',').map(s => parseInt(s.trim()))
          params.model_params.hidden_layer_sizes = sizes.length === 1 ? sizes[0] : sizes
        }
        
        console.log('开始训练模型，参数:', params)
        const response = await trainModel(params)
        console.log('训练模型响应:', response)
        
        if (response.success) {
          this.trainResult = response
          this.currentModel = response.model_id
          this.$message.success('模型训练完成')
        } else {
          this.$message.error(response.message || '模型训练失败')
        }
      } catch (error) {
        console.error('模型训练失败:', error)
        let errorMessage = '模型训练失败: '
        
        if (error.message && error.message.includes('timeout')) {
          errorMessage += '训练超时，请尝试使用较小的数据集或简化模型参数'
        } else {
          errorMessage += error.message || '未知错误'
        }
        
        this.$message.error(errorMessage)
      } finally {
        this.loading.train = false
      }
    },
    
    async predictModel() {
      this.loading.predict = true
      try {
        const response = await predictModel({
          model_id: this.currentModel,
          include_features: true
        })
        console.log('预测响应:', response)
        
        if (response.success) {
          this.predictResult = response
          this.$message.success('预测完成')
        } else {
          this.$message.error(response.message || '模型预测失败')
        }
      } catch (error) {
        console.error('模型预测失败:', error)
        this.$message.error('模型预测失败: ' + (error.message || '未知错误'))
      } finally {
        this.loading.predict = false
      }
    },
    
    async evaluateModel() {
      this.loading.evaluate = true
      try {
        const response = await evaluateModel({
          model_id: this.currentModel
        })
        console.log('评估响应:', response)
        
        if (response.success) {
          this.evaluateResult = response
          this.$message.success('模型评估完成')
        } else {
          this.$message.error(response.message || '模型评估失败')
        }
      } catch (error) {
        console.error('模型评估失败:', error)
        this.$message.error('模型评估失败: ' + (error.message || '未知错误'))
      } finally {
        this.loading.evaluate = false
      }
    },
    
    async debugConnection() {
      try {
        // 测试系统状态
        console.log('测试连接 - 获取系统状态')
        const statusResponse = await getSystemStatus()
        console.log('系统状态响应:', statusResponse)
        
        // 测试简单的GET请求（通过代理）
        console.log('测试连接 - 简单GET请求')
        const testResponse = await fetch('/api/health')
        const healthData = await testResponse.json()
        console.log('健康检查响应:', healthData)
        
        // 尝试发送极简训练请求（通过代理）
        console.log('测试连接 - 极简训练请求')
        const testParams = {
          model_type: 'LinearRegression',
          target_columns: this.trainForm.target_columns.length > 0 ? this.trainForm.target_columns : ['y'],
          test_size: 0.2,
          random_state: 42,
          model_params: { 
            fit_intercept: true,
            copy_X: true,
            n_jobs: null,
            positive: false
          }
        }
        
        try {
          console.log('发送极简请求:', testParams)
          const directResponse = await fetch('/api/ml/train', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            },
            body: JSON.stringify(testParams)
          })
          
          if (!directResponse.ok) {
            throw new Error(`HTTP ${directResponse.status}: ${directResponse.statusText}`)
          }
          
          const responseData = await directResponse.json()
          console.log('极简训练响应:', responseData)
          
          if (responseData.success) {
            this.$message.success('连接测试成功！模型训练正常')
          } else {
            this.$message.warning('连接成功，但训练失败: ' + responseData.message)
          }
        } catch (trainError) {
          console.error('极简训练请求失败:', trainError)
          
          let errorMsg = '训练请求失败: ';
          if (trainError.response) {
            errorMsg += `服务器返回 ${trainError.response.status}: ${JSON.stringify(trainError.response.data)}`;
          } else if (trainError.request) {
            errorMsg += '服务器未响应，可能网络问题或后端服务异常';
          } else {
            errorMsg += trainError.message || '未知错误';
          }
          
          this.$message.error(errorMsg)
        }
      } catch (error) {
        console.error('连接测试失败:', error)
        this.$message.error('连接测试失败: ' + (error.message || '未知错误'))
      }
    },
    
    async downloadCurrentModel() {
      if (!this.currentModel) {
        this.$message.warning('没有当前模型可下载')
        return
      }
      
      this.loading.download = true
      try {
        const response = await downloadModel(this.currentModel)
        
        // 创建下载链接
        const blob = new Blob([response], { type: 'application/octet-stream' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        
        // 生成文件名
        const modelInfo = this.trainResult?.model_info
        const modelName = modelInfo?.model_name || 'model'
        const modelId = this.currentModel.substring(0, 8)
        link.download = `${modelName}_${modelId}.pkl`
        
        link.click()
        window.URL.revokeObjectURL(url)
        
        this.$message.success('模型下载完成')
      } catch (error) {
        console.error('模型下载失败:', error)
        this.$message.error('模型下载失败: ' + (error.message || '未知错误'))
      } finally {
        this.loading.download = false
      }
    }
  }
}
</script>

<style scoped>
.machine-learning {
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

pre {
  background: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  font-size: 12px;
  max-height: 200px;
  overflow-y: auto;
}
</style> 