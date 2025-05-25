<template>
  <div class="visualization">
    <div class="page-header">
      <h2>可视化分析</h2>
      <p>数据可视化、模型可视化、分析结果可视化</p>
      <div class="header-actions">
        <el-button 
          type="primary" 
          size="small" 
          @click="refreshData"
          :loading="loading.refresh"
        >
          刷新数据
        </el-button>

      </div>
    </div>

    <!-- 可视化配置 -->
    <el-card class="section-card">
      <div slot="header" class="section-header">
        <span><i class="el-icon-pie-chart"></i> 可视化配置</span>
      </div>
      
      <el-tabs v-model="activeTab" type="card">
        <!-- 数据可视化 -->
        <el-tab-pane label="数据可视化" name="data">
          <el-form :model="dataVizForm" label-width="120px">
            <el-form-item label="可视化类型">
              <el-select v-model="dataVizForm.type" @change="onDataVizTypeChange">
                <el-option label="相关性矩阵" value="correlation" />
                <el-option label="散点图" value="scatter" />
                <el-option label="数据分布直方图" value="histogram" />
              </el-select>
            </el-form-item>

            <el-form-item label="选择列" v-if="dataVizForm.type === 'correlation'">
              <el-select 
                v-model="dataVizForm.columns" 
                multiple 
                placeholder="请选择要分析的特征列"
                style="width: 100%"
              >
                <el-option 
                  v-for="col in numericColumns" 
                  :key="col"
                  :label="col" 
                  :value="col"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="选择列" v-if="dataVizForm.type === 'histogram'">
              <el-select 
                v-model="dataVizForm.columns" 
                multiple 
                placeholder="请选择要生成直方图的列"
                style="width: 100%"
              >
                <el-option 
                  v-for="col in numericColumns" 
                  :key="col"
                  :label="col" 
                  :value="col"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="X轴" v-if="dataVizForm.type === 'scatter'">
              <el-select v-model="dataVizForm.x_column">
                <el-option 
                  v-for="col in numericColumns" 
                  :key="col"
                  :label="col" 
                  :value="col"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="Y轴" v-if="dataVizForm.type === 'scatter'">
              <el-select v-model="dataVizForm.y_column">
                <el-option 
                  v-for="col in numericColumns" 
                  :key="col"
                  :label="col" 
                  :value="col"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="图表引擎">
              <el-radio-group v-model="dataVizForm.chart_type">
                <el-radio label="matplotlib">Matplotlib (静态)</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item>
              <el-button 
                type="primary" 
                @click="generateDataVisualization"
                :loading="loading.dataViz"
              >
                生成数据可视化
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 模型可视化 -->
        <el-tab-pane label="模型可视化" name="model">
          <el-form :model="modelVizForm" label-width="120px">
            <el-form-item label="可视化类型">
              <el-select v-model="modelVizForm.type">
                <el-option label="预测vs实际" value="prediction" />
                <el-option label="残差图" value="residuals" />
                <el-option label="特征重要性" value="feature_importance" />
                <el-option label="学习曲线" value="learning_curve" />
              </el-select>
            </el-form-item>

            <el-form-item label="选择模型">
              <el-select v-model="modelVizForm.model_id" placeholder="请选择模型">
                <el-option 
                  v-for="model in availableModels" 
                  :key="model.id"
                  :label="model.name" 
                  :value="model.id"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="图表引擎">
              <el-radio-group v-model="modelVizForm.chart_type">
                <el-radio label="matplotlib">Matplotlib (静态)</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item>
              <el-button 
                type="primary" 
                @click="generateModelVisualization"
                :loading="loading.modelViz"
              >
                生成模型可视化
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 可视化结果展示 -->
    <el-card v-if="visualizationResults.length > 0" class="section-card">
      <div slot="header" class="section-header">
        <span><i class="el-icon-picture"></i> 可视化结果</span>
        <el-button 
          type="text" 
          @click="clearAllVisualizations"
          style="float: right; padding: 3px 0;"
        >
          清空所有
        </el-button>
      </div>
      
      <div class="visualization-grid">
        <div 
          v-for="(result, index) in visualizationResults" 
          :key="index"
          class="visualization-item"
        >
          <div class="viz-header">
            <h4>{{ result.title }}</h4>
            <el-button 
              type="text" 
              @click="removeVisualization(index)"
              icon="el-icon-close"
              size="mini"
            />
          </div>
          
          <!-- Matplotlib图片 -->
          <div v-if="result.chart_type === 'matplotlib'" class="chart-container">
            <img 
              :src="`data:image/png;base64,${result.chart_data}`" 
              alt="Chart"
              style="max-width: 100%; height: auto;"
            />
          </div>
          
          <!-- 多个结果的情况 -->
          <div v-else-if="result.results" class="multi-results">
            <el-tabs v-model="result.activeTab" type="border-card">
              <el-tab-pane 
                v-for="(subResult, subKey) in result.results" 
                :key="subKey"
                :label="subKey"
                :name="subKey"
              >
                <div v-if="subResult && subResult.chart_data" class="chart-container">
                  <img 
                    :src="`data:image/png;base64,${subResult.chart_data}`" 
                    alt="Chart"
                    style="max-width: 100%; height: auto;"
                  />
                </div>
                <div v-else class="empty-chart-container">
                  <el-empty description="无法显示图表数据" :image-size="100">
                    <template #description>
                      <p>无法显示图表数据，可能是模型不支持该可视化类型。</p>
                    </template>
                  </el-empty>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 可视化历史 -->
    <el-card v-if="visualizationHistory.length > 0" class="section-card">
      <div slot="header" class="section-header">
        <span><i class="el-icon-time"></i> 可视化历史</span>
      </div>
      
      <el-table :data="visualizationHistory" border stripe>
        <el-table-column prop="timestamp" label="时间" width="180" />
        <el-table-column prop="type" label="类型" width="120" />
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="chart_type" label="图表引擎" width="120" />
        <el-table-column label="操作" width="100">
          <template slot-scope="scope">
            <el-button 
              type="text" 
              @click="restoreVisualization(scope.row)"
              size="mini"
            >
              恢复
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import { 
  generateDataVisualization,
  generateModelVisualization,
  getDataPreview,
  getModelsList 
} from '@/api/mlApi'

export default {
  name: 'Visualization',
  data() {
    return {
      activeTab: 'data',
      dataColumns: [],
      numericColumns: [],
      availableModels: [],
      dataVizForm: {
        type: 'correlation',
        columns: [],
        x_column: '',
        y_column: '',
        chart_type: 'matplotlib'
      },
      modelVizForm: {
        type: 'prediction',
        model_id: '',
        chart_type: 'matplotlib'
      },
      visualizationResults: [],
      visualizationHistory: [],
      loading: {
        dataViz: false,
        modelViz: false,
        refresh: false
      }
    }
  },
  async mounted() {
    await this.loadDataInfo()
    this.loadAvailableModels()
  },
  methods: {
    async loadDataInfo() {
      try {
        const response = await getDataPreview()
        console.log('可视化数据预览响应:', response)
        
        if (response.success && response.train_preview) {
          this.dataColumns = response.train_preview.columns || []
          this.numericColumns = response.train_preview.columns?.filter(col => 
            response.train_preview.dtypes[col]?.includes('float') || 
            response.train_preview.dtypes[col]?.includes('int')
          ) || []
          
          console.log('数据列:', this.dataColumns)
          console.log('数值列:', this.numericColumns)
          
          // 默认选择前6个数值列（用于直方图）
          this.dataVizForm.columns = this.numericColumns.slice(0, 6)
          if (this.numericColumns.length >= 2) {
            this.dataVizForm.x_column = this.numericColumns[0]
            this.dataVizForm.y_column = this.numericColumns[1]
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
    
    async loadAvailableModels() {
      try {
        const response = await getModelsList()
        console.log('可视化模型列表响应:', response)
        
        if (response.success && response.models) {
          this.availableModels = response.models.map(model => ({
            id: model.id,
            name: `${model.name} (${model.type})`
          }))
          
          console.log('加载的模型列表:', this.availableModels)
          
          if (this.availableModels.length === 0) {
            this.$message.info('暂无可用的训练模型，请先训练模型')
          }
        } else {
          console.warn('获取模型列表失败:', response.message)
          this.availableModels = []
          this.$message.warning('获取模型列表失败，请检查是否有已训练的模型')
        }
      } catch (error) {
        console.error('加载模型列表失败:', error)
        this.availableModels = []
        this.$message.error('加载模型列表失败: ' + (error.message || '未知错误'))
      }
    },
    
    onDataVizTypeChange() {
      // 根据类型重置相关配置
      this.dataVizForm.columns = []
      if (this.dataVizForm.type === 'scatter') {
        // 散点图自动选择前两个数值列
        if (this.numericColumns.length >= 2) {
          this.dataVizForm.x_column = this.numericColumns[0]
          this.dataVizForm.y_column = this.numericColumns[1]
        }
      }
    },
    
    async generateDataVisualization() {
      if (this.dataColumns.length === 0) {
        this.$message.warning('请先加载数据')
        return
      }
      
      this.loading.dataViz = true
      try {
        const params = {
          type: this.dataVizForm.type,
          columns: this.dataVizForm.columns,
          chart_type: this.dataVizForm.chart_type
        }
        
        if (this.dataVizForm.type === 'scatter') {
          params.x_column = this.dataVizForm.x_column
          params.y_column = this.dataVizForm.y_column
        }
        
        console.log('发送可视化请求:', params)
        const response = await generateDataVisualization(params)
        console.log('可视化响应:', response)
        
        if (response.success) {
          const result = {
            title: this.getDataVizTitle(),
            type: 'data',
            chart_type: this.dataVizForm.chart_type,
            ...response
          }
          
          this.visualizationResults.push(result)
          this.addToHistory(result)
          
          this.$message.success('数据可视化生成成功')
        } else {
          this.$message.error(response.message || '生成可视化失败')
        }
      } catch (error) {
        console.error('生成数据可视化失败:', error)
        this.$message.error('生成数据可视化失败: ' + (error.message || '未知错误'))
      } finally {
        this.loading.dataViz = false
      }
    },
    
    async generateModelVisualization() {
      if (!this.modelVizForm.model_id) {
        this.$message.warning('请选择模型')
        return
      }
      
      this.loading.modelViz = true
      try {
        const params = {
          type: this.modelVizForm.type,
          model_id: this.modelVizForm.model_id,
          chart_type: this.modelVizForm.chart_type
        }
        
        console.log('发送模型可视化请求:', params)
        const response = await generateModelVisualization(params)
        console.log('模型可视化响应:', response)
        
        if (response.success) {
          const result = {
            title: this.getModelVizTitle(),
            type: 'model',
            chart_type: this.modelVizForm.chart_type,
            ...response
          }
          
          // 检查并处理响应格式
          if (response.results) {
            // 确保结果是有效的
            const targetKeys = Object.keys(response.results)
            if (targetKeys.length > 0) {
              result.activeTab = targetKeys[0]
              
              // 调试查看结果格式
              console.log('可视化结果格式：', response.results)
              
              // 检查结果中是否有任何有效的图表数据
              let hasValidChartData = false
              for (const key in response.results) {
                if (response.results[key].chart_data) {
                  hasValidChartData = true
                  console.log(`${key} 有有效的chart_data`)
                } else {
                  console.warn(`${key} 没有chart_data`)
                  // 添加空图表指示器
                  response.results[key] = {
                    ...response.results[key],
                    chart_data: null,  // 确保前端可以识别这是缺失数据而不是格式错误
                    message: '当前模型不支持此可视化类型或图表生成失败'
                  }
                }
              }
              
              if (hasValidChartData) {
                this.visualizationResults.push(result)
                this.addToHistory(result)
                this.$message.success('模型可视化生成成功')
              } else {
                this.$message.warning('当前模型不支持所选可视化类型，请尝试其他类型')
              }
            } else {
              this.$message.warning('模型可视化未返回有效数据')
            }
          } else {
            this.$message.warning('模型可视化响应格式错误')
          }
        } else {
          this.$message.error(response.message || '生成模型可视化失败')
        }
      } catch (error) {
        console.error('生成模型可视化失败:', error)
        this.$message.error('生成模型可视化失败: ' + (error.message || '未知错误'))
      } finally {
        this.loading.modelViz = false
      }
    },
    

    
    getDataVizTitle() {
      const typeNames = {
        'correlation': 'Correlation Matrix',
        'scatter': 'Scatter Plot',
        'histogram': 'Data Distribution Histogram'
      }
      return typeNames[this.dataVizForm.type] || 'Data Visualization'
    },
    
    getModelVizTitle() {
      const typeNames = {
        'prediction': 'Prediction vs Actual',
        'residuals': 'Residual Plot',
        'feature_importance': 'Feature Importance',
        'learning_curve': 'Learning Curve'
      }
      return typeNames[this.modelVizForm.type] || 'Model Visualization'
    },
    
    addToHistory(result) {
      this.visualizationHistory.unshift({
        timestamp: new Date().toLocaleString(),
        type: result.type,
        title: result.title,
        chart_type: result.chart_type,
        data: result
      })
    },
    
    removeVisualization(index) {
      this.visualizationResults.splice(index, 1)
    },
    
    clearAllVisualizations() {
      this.visualizationResults = []
    },
    
    restoreVisualization(historyItem) {
      this.visualizationResults.push(historyItem.data)
    },
    
    async refreshData() {
      this.loading.refresh = true
      try {
        await this.loadDataInfo()
        await this.loadAvailableModels()
        this.$message.success('数据刷新成功')
      } catch (error) {
        this.$message.error('数据刷新失败: ' + error.message)
      } finally {
        this.loading.refresh = false
      }
    },
    

  }
}
</script>

<style scoped>
.visualization {
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

.header-actions {
  margin-top: 15px;
}

.header-actions .el-button {
  margin-right: 10px;
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

.visualization-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 20px;
}

.visualization-item {
  border: 1px solid #EBEEF5;
  border-radius: 4px;
  padding: 15px;
  background: #FAFAFA;
}

.viz-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #E4E7ED;
}

.viz-header h4 {
  margin: 0;
  color: #303133;
}

.chart-container, .empty-chart-container {
  min-height: 400px;
  width: 100%;
  background: white;
  border-radius: 4px;
  padding: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #f0f0f0;
}

.multi-results {
  background: white;
  border-radius: 4px;
}

.multi-results .chart-container {
  min-height: 350px;
}
</style> 