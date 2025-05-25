<template>
  <div class="auto-ml">
    <div class="page-header">
      <h2>自动化机器学习</h2>
      <p>模型自动筛选、模型参数自动最优化设置、模型打包制作与输出</p>
      <div style="margin-top: 10px;">
        <el-tag 
          :type="dataColumns.length > 0 ? 'success' : 'warning'"
          size="small"
        >
          数据状态: {{ dataColumns.length > 0 ? `已加载 ${dataColumns.length} 列数据` : '未加载数据' }}
        </el-tag>
      </div>
    </div>

    <!-- AutoML配置 -->
    <el-card class="section-card">
      <div slot="header" class="section-header">
        <span><i class="el-icon-magic-stick"></i> AutoML配置</span>
        <el-button 
          type="text" 
          @click="refreshData"
          :loading="loading.refresh"
          style="float: right; padding: 3px 0"
        >
          <i class="el-icon-refresh"></i> 刷新数据
        </el-button>
      </div>
      
      <el-form :model="automlForm" label-width="150px" ref="automlForm">
        <!-- 数据状态提示 -->
        <el-alert
          v-if="dataColumns.length === 0"
          title="请先加载数据"
          description="在进行AutoML之前，请先在数据接口页面上传或加载默认数据"
          type="warning"
          :closable="false"
          style="margin-bottom: 20px;"
        />
        <el-form-item label="目标列选择" required>
          <el-select 
            v-model="automlForm.target_columns" 
            multiple 
            placeholder="请选择目标列"
            style="width: 100%"
            :disabled="dataColumns.length === 0"
          >
            <el-option 
              v-for="col in dataColumns" 
              :key="col"
              :label="col" 
              :value="col"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="搜索方法">
          <el-select v-model="automlForm.search_method">
            <el-option label="网格搜索 (Grid Search)" value="grid" />
            <el-option label="随机搜索 (Random Search)" value="random" />
          </el-select>
        </el-form-item>

        <el-form-item label="交叉验证折数">
          <el-input-number 
            v-model="automlForm.cv_folds" 
            :min="3" 
            :max="10" 
            :step="1"
          />
        </el-form-item>

        <el-form-item label="评估指标">
          <el-select v-model="automlForm.scoring">
            <el-option label="负均方误差 (neg_mean_squared_error)" value="neg_mean_squared_error" />
            <el-option label="R² 分数 (r2)" value="r2" />
            <el-option label="负平均绝对误差 (neg_mean_absolute_error)" value="neg_mean_absolute_error" />
          </el-select>
        </el-form-item>

        <el-form-item label="随机搜索迭代次数" v-if="automlForm.search_method === 'random'">
          <el-input-number 
            v-model="automlForm.max_iter" 
            :min="10" 
            :max="200" 
            :step="10"
          />
        </el-form-item>

        <el-form-item label="训练模式">
          <el-radio-group v-model="automlForm.training_mode">
            <el-radio label="fast">快速模式 (参数较少，训练更快)</el-radio>
            <el-radio label="thorough">完整模式 (参数较多，训练较慢)</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="模型选择">
          <el-checkbox-group v-model="automlForm.models" :disabled="dataColumns.length === 0">
            <el-checkbox label="LinearRegression">线性回归 (LR)</el-checkbox>
            <el-checkbox label="RandomForest">随机森林 (RF)</el-checkbox>
            <el-checkbox label="GradientBoosting">梯度提升 (GBR)</el-checkbox>
            <el-checkbox label="XGBoost">XGBoost (XGBR)</el-checkbox>
            <el-checkbox label="SVR">支持向量机 (SVR)</el-checkbox>
            <el-checkbox label="MLP">人工神经网络 (ANN)</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item>
          <el-button 
            type="primary" 
            @click="runAutoML"
            :loading="loading.automl"
            :disabled="dataColumns.length === 0"
            size="large"
          >
            <i class="el-icon-magic-stick"></i> 运行AutoML
          </el-button>
          <el-button 
            v-if="automlResult"
            type="success" 
            @click="generateComparison"
            :loading="loading.comparison"
            size="large"
          >
            <i class="el-icon-data-analysis"></i> 生成对比报告
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- AutoML进度 -->
    <el-card v-if="loading.automl" class="section-card">
      <div slot="header" class="section-header">
        <span><i class="el-icon-loading"></i> AutoML运行中</span>
      </div>
      
      <div class="progress-container">
        <el-progress 
          :percentage="automlProgress" 
          :status="automlProgress === 100 ? 'success' : ''"
          :stroke-width="20"
        />
        <p style="margin-top: 10px; text-align: center;">{{ automlStatus }}</p>
      </div>
    </el-card>

    <!-- AutoML结果 -->
    <el-card v-if="automlResult" class="section-card">
      <div slot="header" class="section-header">
        <span><i class="el-icon-success"></i> AutoML结果</span>
      </div>
      
      <el-alert
        :title="automlResult.message"
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
        <el-tab-pane label="最优模型" name="best">
          <div v-for="(bestModel, target) in automlResult.best_models" :key="target">
            <h4>{{ target }} - 最优模型</h4>
            <el-descriptions border :column="2">
              <el-descriptions-item label="模型类型">{{ getModelDisplayName(bestModel.model_name) }}</el-descriptions-item>
              <el-descriptions-item label="CV分数">{{ Math.abs(bestModel.score || 0).toFixed(4) }}</el-descriptions-item>
              <el-descriptions-item label="最优参数" :span="2">
                <pre>{{ JSON.stringify(bestModel.params, null, 2) }}</pre>
              </el-descriptions-item>
            </el-descriptions>
            <div style="margin-bottom: 30px;"></div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="模型对比" name="comparison">
          <div v-for="(targetResults, target) in automlResult.results" :key="target">
            <h4>{{ target }} - 模型性能对比</h4>
            <el-table :data="formatModelComparison(targetResults.models)" border stripe>
              <el-table-column prop="model" label="模型" width="150" />
              <el-table-column prop="cv_score" label="CV分数" width="120">
                <template slot-scope="scope">
                  <span>{{ scope.row.cv_score?.toFixed(4) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="train_r2" label="训练R²" width="120">
                <template slot-scope="scope">
                  <span>{{ scope.row.train_r2?.toFixed(4) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="train_rmse" label="训练RMSE" width="120">
                <template slot-scope="scope">
                  <span>{{ scope.row.train_rmse?.toFixed(4) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="test_r2" label="测试R²" width="120">
                <template slot-scope="scope">
                  <span>{{ scope.row.test_r2?.toFixed(4) || 'N/A' }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="test_rmse" label="测试RMSE" width="120">
                <template slot-scope="scope">
                  <span>{{ scope.row.test_rmse?.toFixed(4) || 'N/A' }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="100">
                <template slot-scope="scope">
                  <el-tag :type="scope.row.status === 'success' ? 'success' : 'danger'">
                    {{ scope.row.status === 'success' ? '成功' : '失败' }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
            <div style="margin-bottom: 30px;"></div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="性能图表" name="charts">
          <div v-for="(targetResults, target) in automlResult.results" :key="target">
            <h4>{{ target }} - 模型性能对比图</h4>
            
            <!-- 图表说明 -->
            <el-alert
              :title="getChartTitle()"
              :description="getChartDescription()"
              type="info"
              :closable="false"
              style="margin-bottom: 20px;"
            />
            
            <div class="performance-chart">
              <!-- 使用计算属性过滤成功的模型 -->
              <el-progress 
                v-for="modelData in getSuccessfulModels(targetResults.models)" 
                :key="modelData.name"
                :text-inside="true" 
                :stroke-width="26" 
                :percentage="modelData.percentage"
                :status="modelData.status"
                style="margin-bottom: 10px;"
              >
                <template slot-scope="{ percentage }">
                  {{ modelData.displayName }}: {{ percentage }}% ({{ modelData.metricName }} = {{ modelData.primaryValue }})
                </template>
              </el-progress>
              
              <!-- 显示失败的模型 -->
              <div v-if="getFailedModels(targetResults.models).length > 0" style="margin-top: 20px;">
                <h5 style="color: #F56C6C;">训练失败的模型:</h5>
                <el-tag 
                  v-for="failedModel in getFailedModels(targetResults.models)"
                  :key="failedModel.name"
                  type="danger"
                  style="margin-right: 10px; margin-bottom: 5px;"
                >
                  {{ failedModel.displayName }}: {{ failedModel.error }}
                </el-tag>
              </div>
            </div>
            
            <!-- 性能指标说明 -->
            <div class="metrics-explanation" style="margin-top: 20px;">
              <h5>性能指标说明:</h5>
              <el-row :gutter="20">
                <el-col :span="8">
                  <div class="metric-item">
                    <strong>R² (决定系数)</strong>
                    <p>衡量模型解释数据变异的比例，范围0-1，越接近1越好</p>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="metric-item">
                    <strong>CV分数</strong>
                    <p>交叉验证平均分数，反映模型的泛化能力</p>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="metric-item">
                    <strong>RMSE</strong>
                    <p>均方根误差，数值越小表示预测越准确</p>
                  </div>
                </el-col>
              </el-row>
            </div>
            
            <div style="margin-bottom: 30px;"></div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="模型信息" name="info">
          <el-descriptions border :column="2">
            <el-descriptions-item label="模型ID">{{ automlResult.model_id }}</el-descriptions-item>
            <el-descriptions-item label="模型类型">{{ automlResult.model_info?.model_name || 'AutoML最优模型' }}</el-descriptions-item>
            <el-descriptions-item label="特征数量">{{ automlResult.feature_columns?.length }}</el-descriptions-item>
            <el-descriptions-item label="目标数量">{{ automlResult.target_columns?.length }}</el-descriptions-item>
            <el-descriptions-item label="搜索方法">{{ automlResult.model_info?.automl_config?.search_method }}</el-descriptions-item>
            <el-descriptions-item label="交叉验证">{{ automlResult.model_info?.automl_config?.cv_folds }}折</el-descriptions-item>
            <el-descriptions-item label="评估指标">{{ automlResult.model_info?.automl_config?.scoring }}</el-descriptions-item>
            <el-descriptions-item label="训练时间">{{ automlResult.model_info?.training_time }}</el-descriptions-item>
            <el-descriptions-item label="数据形状" :span="2">{{ automlResult.model_info?.data_shape?.join(' × ') }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 模型对比报告 -->
    <el-card v-if="comparisonReport" class="section-card">
      <div slot="header" class="section-header">
        <span><i class="el-icon-document"></i> 模型对比报告</span>
      </div>
      
      <div class="comparison-summary">
        <h4>总结</h4>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-statistic title="训练模型总数" :value="comparisonReport.summary?.total_models_trained" />
          </el-col>
          <el-col :span="8">
            <el-statistic title="处理目标数" :value="comparisonReport.summary?.targets_processed" />
          </el-col>
          <el-col :span="8">
            <div class="best-model-info">
              <h5>最佳整体模型</h5>
              <p v-if="comparisonReport.summary?.best_overall_model">
                <strong>{{ getModelDisplayName(comparisonReport.summary.best_overall_model.model_name) }}</strong><br>
                平均CV分数: {{ comparisonReport.summary.best_overall_model.average_cv_score?.toFixed(4) }}
              </p>
            </div>
          </el-col>
        </el-row>
      </div>
      
      <div class="comparison-table" style="margin-top: 20px;">
        <h4>详细对比</h4>
        <el-table :data="comparisonReport.comparison_table" border stripe>
          <el-table-column prop="target" label="目标" width="150" />
          <el-table-column prop="model" label="模型" width="150" />
          <el-table-column prop="cv_score" label="CV分数" width="120">
            <template slot-scope="scope">
              <span>{{ scope.row.cv_score?.toFixed(4) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="train_r2" label="训练R²" width="120">
            <template slot-scope="scope">
              <span>{{ scope.row.train_r2?.toFixed(4) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="train_rmse" label="训练RMSE" width="120">
            <template slot-scope="scope">
              <span>{{ scope.row.train_rmse?.toFixed(4) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="test_r2" label="测试R²" width="120">
            <template slot-scope="scope">
              <span>{{ scope.row.test_r2 !== 'N/A' ? scope.row.test_r2?.toFixed(4) : 'N/A' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="test_rmse" label="测试RMSE" width="120">
            <template slot-scope="scope">
              <span>{{ scope.row.test_rmse !== 'N/A' ? scope.row.test_rmse?.toFixed(4) : 'N/A' }}</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script>
import { 
  runAutoML,
  getDataPreview,
  downloadModel
} from '@/api/mlApi'

export default {
  name: 'AutoML',
  data() {
    return {
      dataColumns: [],
      automlForm: {
        target_columns: [],
        search_method: 'grid',
        cv_folds: 5,
        scoring: 'neg_mean_squared_error',
        max_iter: 50,
        training_mode: 'fast',
        models: ['LinearRegression', 'RandomForest', 'GradientBoosting', 'XGBoost', 'SVR', 'MLP']
      },
      automlResult: null,
      comparisonReport: null,
      automlProgress: 0,
      automlStatus: '准备开始...',
      resultTab: 'best',
      loading: {
        automl: false,
        comparison: false,
        refresh: false,
        download: false
      }
    }
  },
  async mounted() {
    await this.loadDataInfo()
  },
  methods: {
    // 获取训练成功的模型数据
    getSuccessfulModels(models) {
      if (!models) return []
      
      const scoring = this.automlResult?.model_info?.automl_config?.scoring || 'neg_mean_squared_error'
      
      return Object.keys(models)
        .filter(modelName => !models[modelName].error)
        .map(modelName => {
          const modelResult = models[modelName]
          
          // 根据评估指标选择显示的数据
          let primaryValue, displayValue, metricName, percentage, sortValue
          
          if (scoring === 'r2') {
            primaryValue = modelResult.train_r2 || 0
            displayValue = primaryValue.toFixed(4)
            metricName = 'R²'
            percentage = Math.round(Math.max(0, Math.min(100, primaryValue * 100)))
            sortValue = primaryValue
          } else if (scoring === 'neg_mean_squared_error') {
            primaryValue = modelResult.cv_score || 0
            displayValue = primaryValue.toFixed(4)
            metricName = 'MSE'
            // MSE越小越好，转换为百分比显示（取倒数并标准化）
            const maxMSE = 100 // 假设最大MSE为100
            percentage = Math.round(Math.max(0, Math.min(100, (1 - primaryValue / maxMSE) * 100)))
            sortValue = -primaryValue // 负值排序，越小越好
          } else if (scoring === 'neg_mean_absolute_error') {
            primaryValue = modelResult.cv_score || 0
            displayValue = primaryValue.toFixed(4)
            metricName = 'MAE'
            // MAE越小越好，转换为百分比显示
            const maxMAE = 50 // 假设最大MAE为50
            percentage = Math.round(Math.max(0, Math.min(100, (1 - primaryValue / maxMAE) * 100)))
            sortValue = -primaryValue // 负值排序，越小越好
          } else {
            // 默认使用R²
            primaryValue = modelResult.train_r2 || 0
            displayValue = primaryValue.toFixed(4)
            metricName = 'R²'
            percentage = Math.round(Math.max(0, Math.min(100, primaryValue * 100)))
            sortValue = primaryValue
          }
          
          return {
            name: modelName,
            displayName: this.getModelDisplayName(modelName),
            percentage: percentage,
            primaryValue: displayValue,
            metricName: metricName,
            status: this.getProgressStatus(primaryValue, scoring),
            modelResult: modelResult,
            sortValue: sortValue
          }
        })
        .sort((a, b) => b.sortValue - a.sortValue) // 按性能排序
    },
    
    // 获取训练失败的模型数据
    getFailedModels(models) {
      if (!models) return []
      
      return Object.keys(models)
        .filter(modelName => models[modelName].error)
        .map(modelName => ({
          name: modelName,
          displayName: this.getModelDisplayName(modelName),
          error: models[modelName].error || '训练失败'
        }))
    },
    async loadDataInfo() {
      try {
        const response = await getDataPreview()
        console.log('AutoML数据预览响应:', response)
        if (response.success && response.train_preview) {
          this.dataColumns = response.train_preview.columns || []
          // 默认选择最后一列作为目标列
          if (this.dataColumns.length > 0) {
            this.automlForm.target_columns = [this.dataColumns[this.dataColumns.length - 1]]
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
    
    async runAutoML() {
      if (this.automlForm.target_columns.length === 0) {
        this.$message.warning('请选择目标列')
        return
      }
      if (this.automlForm.models.length === 0) {
        this.$message.warning('请选择至少一个模型')
        return
      }
      
      this.loading.automl = true
      this.automlProgress = 0
      this.automlStatus = '正在初始化AutoML...'
      
      // 计算总的训练步骤
      const totalSteps = this.automlForm.target_columns.length * this.automlForm.models.length
      let currentStep = 0
      
      // 更智能的进度更新
      const progressInterval = setInterval(() => {
        if (this.automlProgress < 95) {
          // 基于时间的渐进式进度更新
          const increment = Math.random() * 3 + 1  // 1-4%的增量
          this.automlProgress += increment
          // 保留一位小数
          this.automlProgress = Math.round(Math.min(this.automlProgress, 95) * 10) / 10
          this.updateAutoMLStatus()
        }
      }, 2000)  // 每2秒更新一次
      
      try {
        const response = await runAutoML(this.automlForm)
        if (response.success) {
          this.automlResult = response
          this.automlProgress = 100.0
          this.automlStatus = 'AutoML完成！'
          this.$message.success('AutoML运行完成')
        } else {
          this.automlStatus = 'AutoML运行失败: ' + response.message
          this.$message.error(response.message || 'AutoML运行失败')
        }
      } catch (error) {
        console.error('AutoML运行失败:', error)
        this.automlStatus = 'AutoML运行失败: ' + (error.message || '未知错误')
        this.$message.error(error.message || 'AutoML运行失败')
      } finally {
        clearInterval(progressInterval)
        this.loading.automl = false
      }
    },
    
    updateAutoMLStatus() {
      const statuses = [
        '正在训练线性回归模型...',
        '正在训练随机森林模型...',
        '正在训练梯度提升模型...',
        '正在训练XGBoost模型...',
        '正在训练支持向量机模型...',
        '正在训练神经网络模型...',
        '正在进行超参数优化...',
        '正在评估模型性能...',
        '正在生成结果报告...'
      ]
      const progress = this.automlProgress
      let index
      if (progress < 15) index = 0
      else if (progress < 30) index = 1
      else if (progress < 45) index = 2
      else if (progress < 60) index = 3
      else if (progress < 75) index = 4
      else if (progress < 85) index = 5
      else if (progress < 92) index = 6
      else if (progress < 98) index = 7
      else index = 8
      
      this.automlStatus = statuses[index]
    },
    
    async generateComparison() {
      this.loading.comparison = true
      try {
        // 模拟生成对比报告
        this.comparisonReport = this.generateMockComparison()
        this.$message.success('对比报告生成完成')
      } catch (error) {
        console.error('生成对比报告失败:', error)
      } finally {
        this.loading.comparison = false
      }
    },
    
    generateMockComparison() {
      // 模拟对比报告数据
      const comparisonTable = []
      const targets = this.automlForm.target_columns
      const models = this.automlForm.models
      
      targets.forEach(target => {
        models.forEach(model => {
          comparisonTable.push({
            target: target,
            model: this.getModelDisplayName(model),
            cv_score: 0.8 + Math.random() * 0.15,
            train_r2: 0.85 + Math.random() * 0.1,
            train_rmse: Math.random() * 0.3,
            test_r2: 0.82 + Math.random() * 0.12,
            test_rmse: Math.random() * 0.35
          })
        })
      })
      
      return {
        success: true,
        comparison_table: comparisonTable,
        summary: {
          total_models_trained: targets.length * models.length,
          targets_processed: targets.length,
          best_overall_model: {
            model_name: 'RandomForest',
            average_cv_score: 0.92,
            score_std: 0.02,
            targets_count: targets.length
          }
        }
      }
    },
    
    formatModelComparison(models) {
      return Object.keys(models).map(modelName => {
        const model = models[modelName]
        return {
          model: this.getModelDisplayName(modelName),
          status: model.error ? 'failed' : 'success',
          ...model
        }
      })
    },
    
    getModelDisplayName(modelKey) {
      const names = {
        'LinearRegression': '线性回归',
        'RandomForest': '随机森林',
        'GradientBoosting': '梯度提升',
        'XGBoost': 'XGBoost',
        'SVR': '支持向量机',
        'MLP': '人工神经网络'
      }
      return names[modelKey] || modelKey
    },
    
    getProgressStatus(value, scoring = 'r2') {
      if (scoring === 'r2') {
        if (value >= 0.9) return 'success'
        if (value >= 0.8) return 'warning'
        return 'exception'
      } else if (scoring === 'neg_mean_squared_error') {
        // MSE越小越好
        if (value <= 5) return 'success'
        if (value <= 20) return 'warning'
        return 'exception'
      } else if (scoring === 'neg_mean_absolute_error') {
        // MAE越小越好
        if (value <= 2) return 'success'
        if (value <= 10) return 'warning'
        return 'exception'
      } else {
        // 默认按R²处理
        if (value >= 0.9) return 'success'
        if (value >= 0.8) return 'warning'
        return 'exception'
      }
    },
    
    getChartTitle() {
      const scoring = this.automlResult?.model_info?.automl_config?.scoring || 'neg_mean_squared_error'
      const metricNames = {
        'r2': 'R²决定系数',
        'neg_mean_squared_error': '均方误差(MSE)',
        'neg_mean_absolute_error': '平均绝对误差(MAE)'
      }
      return `模型性能对比 - ${metricNames[scoring] || '性能指标'}`
    },
    
    getChartDescription() {
      const scoring = this.automlResult?.model_info?.automl_config?.scoring || 'neg_mean_squared_error'
      
      if (scoring === 'r2') {
        return '以下图表显示各模型的R²决定系数，数值越高表示模型拟合效果越好。绿色表示优秀(≥90%)，橙色表示良好(≥80%)，红色表示需要改进(<80%)。'
      } else if (scoring === 'neg_mean_squared_error') {
        return '以下图表显示各模型的均方误差(MSE)，数值越小表示模型预测越准确。绿色表示优秀(≤5)，橙色表示良好(≤20)，红色表示需要改进(>20)。'
      } else if (scoring === 'neg_mean_absolute_error') {
        return '以下图表显示各模型的平均绝对误差(MAE)，数值越小表示模型预测越准确。绿色表示优秀(≤2)，橙色表示良好(≤10)，红色表示需要改进(>10)。'
      } else {
        return '以下图表显示各模型的性能指标，数值反映模型的预测效果。'
      }
    },
    
    async refreshData() {
      this.loading.refresh = true
      try {
        await this.loadDataInfo()
        this.$message.success('数据刷新完成')
      } catch (error) {
        console.error('刷新数据失败:', error)
        this.$message.error('刷新数据失败: ' + (error.message || '未知错误'))
      } finally {
        this.loading.refresh = false
      }
    },
    
    async downloadCurrentModel() {
      if (!this.automlResult || !this.automlResult.model_id) {
        this.$message.warning('没有当前模型可下载')
        return
      }
      
      this.loading.download = true
      try {
        const response = await downloadModel(this.automlResult.model_id)
        
        // 创建下载链接
        const blob = new Blob([response], { type: 'application/octet-stream' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        
        // 生成文件名
        const modelName = 'AutoML最优模型'
        const modelId = this.automlResult.model_id.substring(0, 8)
        link.download = `${modelName}_${modelId}.pkl`
        
        link.click()
        window.URL.revokeObjectURL(url)
        
        this.$message.success('AutoML模型下载完成')
      } catch (error) {
        console.error('AutoML模型下载失败:', error)
        this.$message.error('AutoML模型下载失败: ' + (error.message || '未知错误'))
      } finally {
        this.loading.download = false
      }
    }
  }
}
</script>

<style scoped>
.auto-ml {
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

.progress-container {
  padding: 20px;
  text-align: center;
}

.performance-chart {
  max-width: 600px;
  margin: 20px auto;
}

.comparison-summary {
  margin-bottom: 20px;
}

.best-model-info h5 {
  margin-bottom: 10px;
  color: #303133;
}

.best-model-info p {
  margin: 0;
  color: #606266;
}

pre {
  background: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  font-size: 12px;
  max-height: 200px;
  overflow-y: auto;
}

.metrics-explanation {
  background: #fafbfc;
  padding: 15px;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.metrics-explanation h5 {
  margin-bottom: 15px;
  color: #303133;
  font-size: 14px;
}

.metric-item {
  text-align: center;
  padding: 10px;
}

.metric-item strong {
  display: block;
  margin-bottom: 8px;
  color: #409EFF;
  font-size: 14px;
}

.metric-item p {
  margin: 0;
  color: #606266;
  font-size: 12px;
  line-height: 1.4;
}
</style> 