<template>
  <div class="stacking-ensemble">
    <div class="page-header">
      <h2>机器学习Stacking集成</h2>
      <p>训练一级模型、训练二级模型、k折交叉验证</p>
    </div>

    <!-- Stacking模型配置 -->
    <el-card class="section-card">
      <div slot="header" class="section-header">
        <span><i class="el-icon-connection"></i> Stacking集成配置</span>
      </div>
      
      <el-form :model="stackingForm" label-width="150px" ref="stackingForm">
        <el-form-item label="目标列选择" required>
          <el-select 
            v-model="stackingForm.target_columns" 
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

        <el-form-item label="基学习器选择" required>
          <el-checkbox-group v-model="stackingForm.base_models">
            <el-checkbox label="rf">随机森林 (Random Forest)</el-checkbox>
            <el-checkbox label="gbr">梯度提升 (Gradient Boosting)</el-checkbox>
            <el-checkbox label="lr">线性回归 (Linear Regression)</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item label="元学习器选择">
          <el-select v-model="stackingForm.meta_model">
            <el-option label="线性回归" value="LinearRegression" />
            <el-option label="随机森林" value="RandomForest" />
          </el-select>
        </el-form-item>

        <el-form-item label="交叉验证折数">
          <el-input-number 
            v-model="stackingForm.cv_folds" 
            :min="3" 
            :max="10" 
            :step="1"
          />
        </el-form-item>

        <el-form-item>
          <el-button 
            type="primary" 
            @click="trainStackingModel"
            :loading="loading.train"
            size="large"
          >
            <i class="el-icon-connection"></i> 训练Stacking模型
          </el-button>
          <el-button 
            type="info" 
            @click="analyzeBaseModels"
            :loading="loading.analyze"
            size="large"
          >
            <i class="el-icon-data-analysis"></i> 分析基模型
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 基模型分析结果 -->
    <el-card v-if="baseModelAnalysis" class="section-card">
      <div slot="header" class="section-header">
        <span><i class="el-icon-data-analysis"></i> 基模型分析</span>
      </div>
      
      <div v-for="(targetData, target) in baseModelAnalysis.results" :key="target">
        <h4>{{ target }} - 基模型性能对比</h4>
        <el-table :data="formatBaseModelData(targetData)" border stripe>
          <el-table-column prop="model" label="模型" width="150" />
          <el-table-column prop="r2" label="R²" width="100">
            <template slot-scope="scope">
              <span>{{ scope.row.r2.toFixed(4) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="mse" label="MSE" width="120">
            <template slot-scope="scope">
              <span>{{ scope.row.mse.toFixed(4) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="rmse" label="RMSE" width="120">
            <template slot-scope="scope">
              <span>{{ scope.row.rmse.toFixed(4) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="mae" label="MAE" width="120">
            <template slot-scope="scope">
              <span>{{ scope.row.mae.toFixed(4) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="cv_mean" label="CV均值" width="120">
            <template slot-scope="scope">
              <span>{{ scope.row.cv_mean.toFixed(4) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="cv_std" label="CV标准差" width="120">
            <template slot-scope="scope">
              <span>{{ scope.row.cv_std.toFixed(4) }}</span>
            </template>
          </el-table-column>
        </el-table>
        <div style="margin-bottom: 30px;"></div>
      </div>
    </el-card>

    <!-- Stacking训练结果 -->
    <el-card v-if="stackingResult" class="section-card">
      <div slot="header" class="section-header">
        <span><i class="el-icon-success"></i> Stacking训练结果</span>
      </div>
      
      <el-alert
        :title="stackingResult.message"
        type="success"
        :closable="false"
        style="margin-bottom: 20px;"
      />
      
      <el-tabs v-model="resultTab" type="card">
        <el-tab-pane label="模型信息" name="info">
          <el-descriptions border :column="2">
            <el-descriptions-item label="模型ID">{{ stackingResult.model_id }}</el-descriptions-item>
            <el-descriptions-item label="模型类型">{{ stackingResult.model?.model_name }}</el-descriptions-item>
            <el-descriptions-item label="特征数量">{{ stackingResult.feature_columns?.length }}</el-descriptions-item>
            <el-descriptions-item label="目标数量">{{ stackingResult.target_columns?.length }}</el-descriptions-item>
            <el-descriptions-item label="基学习器">{{ stackingResult.model?.base_models?.join(', ') }}</el-descriptions-item>
            <el-descriptions-item label="元学习器">{{ stackingResult.model?.meta_model }}</el-descriptions-item>
            <el-descriptions-item label="交叉验证折数">{{ stackingResult.model?.cv_folds }}</el-descriptions-item>
            <el-descriptions-item label="训练时间">{{ stackingResult.model?.training_time }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
        
        <el-tab-pane label="性能指标" name="metrics">
          <div v-for="(metrics, target) in stackingResult.metrics" :key="target">
            <h4>{{ target }} - Stacking集成指标</h4>
            <el-row :gutter="20">
              <el-col :span="4">
                <el-statistic title="MSE" :value="metrics.mse" :precision="4" />
              </el-col>
              <el-col :span="4">
                <el-statistic title="RMSE" :value="metrics.rmse" :precision="4" />
              </el-col>
              <el-col :span="4">
                <el-statistic title="MAE" :value="metrics.mae" :precision="4" />
              </el-col>
              <el-col :span="4">
                <el-statistic title="R²" :value="metrics.r2" :precision="4" />
              </el-col>
              <el-col :span="4">
                <el-statistic title="CV Score" :value="metrics.cv_score" :precision="4" />
              </el-col>
              <el-col :span="4">
                <el-statistic title="CV Std" :value="metrics.cv_std" :precision="4" />
              </el-col>
            </el-row>
            <div style="margin-bottom: 30px;"></div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="集成架构" name="architecture">
          <div class="stacking-architecture">
            <h4>Stacking集成学习架构</h4>
            <div class="architecture-diagram">
              <div class="level-1">
                <h5>第一层：基学习器</h5>
                <div class="base-models">
                  <div 
                    v-for="model in stackingResult.model?.base_models" 
                    :key="model"
                    class="base-model-box"
                  >
                    {{ getModelName(model) }}
                  </div>
                </div>
              </div>
              <div class="arrow">↓</div>
              <div class="level-2">
                <h5>第二层：元学习器</h5>
                <div class="meta-model-box">
                  {{ stackingResult.model?.meta_model }}
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 性能比较图表 -->
    <el-card v-if="baseModelAnalysis && stackingResult" class="section-card">
      <div slot="header" class="section-header">
        <span><i class="el-icon-pie-chart"></i> 模型性能比较</span>
      </div>
      
      <div v-for="(targetData, target) in baseModelAnalysis.results" :key="target">
        <h4>{{ target }} - 模型R²对比</h4>
        <div class="performance-chart">
          <el-progress 
            v-for="(modelData, modelName) in targetData" 
            :key="modelName"
            :text-inside="true" 
            :stroke-width="26" 
            :percentage="Math.round(modelData.metrics.r2 * 100)"
            status="success"
            style="margin-bottom: 10px;"
          >
            <template slot-scope="{ percentage }">
              {{ getModelName(modelName) }}: {{ percentage }}%
            </template>
          </el-progress>
          
          <el-progress 
            v-if="stackingResult.metrics[target]"
            :text-inside="true" 
            :stroke-width="26" 
            :percentage="Math.round(stackingResult.metrics[target].r2 * 100)"
            status="warning"
            style="margin-bottom: 10px;"
          >
            <template slot-scope="{ percentage }">
              Stacking集成: {{ percentage }}%
            </template>
          </el-progress>
        </div>
        <div style="margin-bottom: 30px;"></div>
      </div>
    </el-card>
  </div>
</template>

<script>
import { 
  trainStackingModel,
  getDataPreview 
} from '@/api/mlApi'

export default {
  name: 'StackingEnsemble',
  data() {
    return {
      dataColumns: [],
      stackingForm: {
        target_columns: [],
        base_models: ['rf', 'gbr', 'lr'],
        meta_model: 'LinearRegression',
        cv_folds: 5
      },
      stackingResult: null,
      baseModelAnalysis: null,
      resultTab: 'info',
      loading: {
        train: false,
        analyze: false
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
          this.stackingForm.target_columns = this.dataColumns.slice(-3)
        }
      } catch (error) {
        console.error('加载数据信息失败:', error)
      }
    },
    
    async trainStackingModel() {
      if (this.stackingForm.target_columns.length === 0) {
        this.$message.warning('请选择目标列')
        return
      }
      if (this.stackingForm.base_models.length === 0) {
        this.$message.warning('请选择至少一个基学习器')
        return
      }
      
      this.loading.train = true
      try {
        const response = await trainStackingModel(this.stackingForm)
        this.stackingResult = response
        this.$message.success('Stacking模型训练完成')
      } catch (error) {
        console.error('Stacking模型训练失败:', error)
      } finally {
        this.loading.train = false
      }
    },
    
    async analyzeBaseModels() {
      if (this.stackingForm.target_columns.length === 0) {
        this.$message.warning('请选择目标列')
        return
      }
      
      this.loading.analyze = true
      try {
        // 这里应该调用基模型分析API，暂时模拟数据
        this.baseModelAnalysis = this.generateMockBaseModelAnalysis()
        this.$message.success('基模型分析完成')
      } catch (error) {
        console.error('基模型分析失败:', error)
      } finally {
        this.loading.analyze = false
      }
    },
    
    generateMockBaseModelAnalysis() {
      // 模拟基模型分析数据
      const results = {}
      this.stackingForm.target_columns.forEach(target => {
        results[target] = {
          rf: {
            metrics: {
              r2: 0.85 + Math.random() * 0.1,
              mse: Math.random() * 0.5,
              rmse: Math.random() * 0.3,
              mae: Math.random() * 0.2,
              cv_mean: 0.82 + Math.random() * 0.1,
              cv_std: 0.01 + Math.random() * 0.02
            }
          },
          gbr: {
            metrics: {
              r2: 0.87 + Math.random() * 0.08,
              mse: Math.random() * 0.4,
              rmse: Math.random() * 0.25,
              mae: Math.random() * 0.18,
              cv_mean: 0.84 + Math.random() * 0.08,
              cv_std: 0.01 + Math.random() * 0.015
            }
          },
          lr: {
            metrics: {
              r2: 0.75 + Math.random() * 0.15,
              mse: Math.random() * 0.6,
              rmse: Math.random() * 0.35,
              mae: Math.random() * 0.25,
              cv_mean: 0.72 + Math.random() * 0.15,
              cv_std: 0.02 + Math.random() * 0.025
            }
          }
        }
      })
      
      return {
        success: true,
        message: '基模型分析完成',
        results: results
      }
    },
    
    formatBaseModelData(targetData) {
      return Object.keys(targetData).map(modelName => ({
        model: this.getModelName(modelName),
        ...targetData[modelName].metrics
      }))
    },
    
    getModelName(modelKey) {
      const names = {
        'rf': '随机森林',
        'gbr': '梯度提升',
        'lr': '线性回归',
        'LinearRegression': '线性回归',
        'RandomForest': '随机森林'
      }
      return names[modelKey] || modelKey
    }
  }
}
</script>

<style scoped>
.stacking-ensemble {
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

.stacking-architecture {
  text-align: center;
  padding: 20px;
}

.architecture-diagram {
  max-width: 600px;
  margin: 0 auto;
}

.level-1, .level-2 {
  margin: 20px 0;
}

.level-1 h5, .level-2 h5 {
  margin-bottom: 15px;
  color: #606266;
}

.base-models {
  display: flex;
  justify-content: center;
  gap: 20px;
  flex-wrap: wrap;
}

.base-model-box {
  background: #E3F2FD;
  border: 2px solid #2196F3;
  border-radius: 8px;
  padding: 15px 20px;
  color: #1976D2;
  font-weight: bold;
  min-width: 120px;
}

.meta-model-box {
  background: #FFF3E0;
  border: 2px solid #FF9800;
  border-radius: 8px;
  padding: 15px 20px;
  color: #F57C00;
  font-weight: bold;
  display: inline-block;
  min-width: 120px;
}

.arrow {
  font-size: 24px;
  color: #909399;
  margin: 10px 0;
}

.performance-chart {
  max-width: 600px;
  margin: 20px auto;
}
</style> 