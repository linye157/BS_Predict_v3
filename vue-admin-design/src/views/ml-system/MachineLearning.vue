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
            <el-checkbox v-model="trainForm.model_params.fit_intercept">拟合截距</el-checkbox>
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
      
      <el-tabs v-model="resultTab" type="card">
        <el-tab-pane label="模型信息" name="info">
          <el-descriptions border :column="2">
            <el-descriptions-item label="模型ID">{{ trainResult.model_id }}</el-descriptions-item>
            <el-descriptions-item label="模型类型">{{ trainResult.model?.model_name }}</el-descriptions-item>
            <el-descriptions-item label="特征数量">{{ trainResult.feature_columns?.length }}</el-descriptions-item>
            <el-descriptions-item label="目标数量">{{ trainResult.target_columns?.length }}</el-descriptions-item>
            <el-descriptions-item label="最优参数" :span="2">
              <pre>{{ JSON.stringify(trainResult.best_params, null, 2) }}</pre>
            </el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
        
        <el-tab-pane label="性能指标" name="metrics">
          <div v-for="(metrics, target) in trainResult.metrics?.train" :key="target">
            <h4>{{ target }} - 训练集指标</h4>
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
          
          <div v-for="(metrics, target) in trainResult.metrics?.validation" :key="target" style="margin-top: 20px;">
            <h4>{{ target }} - 验证集指标</h4>
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
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 预测结果展示 -->
    <el-card v-if="predictResult" class="section-card">
      <div slot="header" class="section-header">
        <span><i class="el-icon-view"></i> 预测结果</span>
      </div>
      
      <el-table 
        :data="predictResult.predictions?.slice(0, 100)" 
        border 
        stripe 
        max-height="400"
      >
        <el-table-column 
          v-for="col in Object.keys(predictResult.predictions?.[0] || {})" 
          :key="col"
          :prop="col" 
          :label="col"
          width="150"
        />
      </el-table>
      
      <div style="text-align: center; margin-top: 10px;" v-if="predictResult.predictions?.length > 100">
        <el-tag>显示前100行，共{{ predictResult.predictions.length }}行</el-tag>
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
  getDataPreview 
} from '@/api/mlApi'

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
        evaluate: false
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
        this.availableModels = response.models || []
      } catch (error) {
        console.error('加载可用模型失败:', error)
      }
    },
    
    async loadDataInfo() {
      try {
        const response = await getDataPreview()
        if (response.train_preview) {
          this.dataColumns = response.train_preview.columns || []
          // 默认选择最后3列作为目标列
          this.trainForm.target_columns = this.dataColumns.slice(-3)
        }
      } catch (error) {
        console.error('加载数据信息失败:', error)
      }
    },
    
    onModelChange() {
      // 重置模型参数
      this.trainForm.model_params = this.getDefaultParams(this.trainForm.model_type)
    },
    
    getDefaultParams(modelType) {
      const defaults = {
        'LinearRegression': {
          fit_intercept: true
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
      
      this.loading.train = true
      try {
        // 处理MLP的隐藏层参数
        let params = { ...this.trainForm }
        if (params.model_type === 'MLP' && params.model_params.hidden_layer_sizes) {
          const sizes = params.model_params.hidden_layer_sizes.split(',').map(s => parseInt(s.trim()))
          params.model_params.hidden_layer_sizes = sizes.length === 1 ? sizes[0] : sizes
        }
        
        const response = await trainModel(params)
        this.trainResult = response
        this.currentModel = response.model_id
        this.$message.success('模型训练完成')
      } catch (error) {
        console.error('模型训练失败:', error)
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
        this.predictResult = response
        this.$message.success('预测完成')
      } catch (error) {
        console.error('模型预测失败:', error)
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
        this.evaluateResult = response
        this.$message.success('模型评估完成')
      } catch (error) {
        console.error('模型评估失败:', error)
      } finally {
        this.loading.evaluate = false
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