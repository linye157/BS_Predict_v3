<template>
  <div class="auto-ml">
    <div class="page-header">
      <h2>自动化机器学习</h2>
      <p>模型自动筛选、模型参数自动最优化设置、模型打包制作与输出</p>
    </div>

    <!-- AutoML配置 -->
    <el-card class="section-card">
      <div slot="header" class="section-header">
        <span><i class="el-icon-magic-stick"></i> AutoML配置</span>
      </div>
      
      <el-form :model="automlForm" label-width="150px" ref="automlForm">
        <el-form-item label="目标列选择" required>
          <el-select 
            v-model="automlForm.target_columns" 
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

        <el-form-item label="模型选择">
          <el-checkbox-group v-model="automlForm.models">
            <el-checkbox label="LinearRegression">线性回归 (LR)</el-checkbox>
            <el-checkbox label="RandomForest">随机森林 (RF)</el-checkbox>
            <el-checkbox label="GradientBoosting">梯度提升 (GBR)</el-checkbox>
            <el-checkbox label="XGBoost">XGBoost (XGBR)</el-checkbox>
            <el-checkbox label="SVR">支持向量机 (SVR)</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item>
          <el-button 
            type="primary" 
            @click="runAutoML"
            :loading="loading.automl"
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
      
      <el-tabs v-model="resultTab" type="card">
        <el-tab-pane label="最优模型" name="best">
          <div v-for="(bestModel, target) in automlResult.best_models" :key="target">
            <h4>{{ target }} - 最优模型</h4>
            <el-descriptions border :column="2">
              <el-descriptions-item label="模型类型">{{ bestModel.model_name }}</el-descriptions-item>
              <el-descriptions-item label="CV分数">{{ bestModel.score?.toFixed(4) }}</el-descriptions-item>
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
            <div class="performance-chart">
              <el-progress 
                v-for="(modelResult, modelName) in targetResults.models" 
                :key="modelName"
                v-if="!modelResult.error"
                :text-inside="true" 
                :stroke-width="26" 
                :percentage="Math.round((modelResult.train_r2 || 0) * 100)"
                :status="getProgressStatus(modelResult.train_r2)"
                style="margin-bottom: 10px;"
              >
                <template slot-scope="{ percentage }">
                  {{ getModelDisplayName(modelName) }}: {{ percentage }}%
                </template>
              </el-progress>
            </div>
            <div style="margin-bottom: 30px;"></div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="模型信息" name="info">
          <el-descriptions border :column="2">
            <el-descriptions-item label="模型ID">{{ automlResult.model_id }}</el-descriptions-item>
            <el-descriptions-item label="模型类型">{{ automlResult.model?.model_name }}</el-descriptions-item>
            <el-descriptions-item label="特征数量">{{ automlResult.feature_columns?.length }}</el-descriptions-item>
            <el-descriptions-item label="目标数量">{{ automlResult.target_columns?.length }}</el-descriptions-item>
            <el-descriptions-item label="搜索方法">{{ automlResult.model?.automl_config?.search_method }}</el-descriptions-item>
            <el-descriptions-item label="交叉验证">{{ automlResult.model?.automl_config?.cv_folds }}折</el-descriptions-item>
            <el-descriptions-item label="评估指标">{{ automlResult.model?.automl_config?.scoring }}</el-descriptions-item>
            <el-descriptions-item label="训练时间">{{ automlResult.model?.training_time }}</el-descriptions-item>
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
  getDataPreview 
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
        models: ['LinearRegression', 'RandomForest', 'GradientBoosting', 'XGBoost', 'SVR']
      },
      automlResult: null,
      comparisonReport: null,
      automlProgress: 0,
      automlStatus: '准备开始...',
      resultTab: 'best',
      loading: {
        automl: false,
        comparison: false
      }
    }
  },
  async mounted() {
    await this.loadDataInfo()
  },
  methods: {
    async loadDataInfo() {
      try {
        const response = await getDataPreview()
        if (response.train_preview) {
          this.dataColumns = response.train_preview.columns || []
          // 默认选择最后3列作为目标列
          this.automlForm.target_columns = this.dataColumns.slice(-3)
        }
      } catch (error) {
        console.error('加载数据信息失败:', error)
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
      
      // 模拟进度更新
      const progressInterval = setInterval(() => {
        if (this.automlProgress < 90) {
          this.automlProgress += Math.random() * 10
          this.updateAutoMLStatus()
        }
      }, 1000)
      
      try {
        const response = await runAutoML(this.automlForm)
        this.automlResult = response
        this.automlProgress = 100
        this.automlStatus = 'AutoML完成！'
        this.$message.success('AutoML运行完成')
      } catch (error) {
        console.error('AutoML运行失败:', error)
        this.automlStatus = 'AutoML运行失败'
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
        '正在进行超参数优化...',
        '正在评估模型性能...',
        '正在生成结果报告...'
      ]
      const index = Math.floor(this.automlProgress / 12.5)
      this.automlStatus = statuses[Math.min(index, statuses.length - 1)]
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
        'SVR': '支持向量机'
      }
      return names[modelKey] || modelKey
    },
    
    getProgressStatus(r2Score) {
      if (r2Score >= 0.9) return 'success'
      if (r2Score >= 0.8) return 'warning'
      return 'exception'
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
</style> 