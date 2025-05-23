<template>
  <div class="visualization">
    <div class="page-header">
      <h2>可视化分析</h2>
      <p>数据可视化、模型可视化、分析结果可视化</p>
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
                <el-option label="数据分布图" value="distribution" />
                <el-option label="相关性矩阵" value="correlation" />
                <el-option label="散点图" value="scatter" />
                <el-option label="箱线图" value="box" />
                <el-option label="直方图" value="histogram" />
              </el-select>
            </el-form-item>

            <el-form-item label="选择列" v-if="dataVizForm.type !== 'correlation'">
              <el-select 
                v-model="dataVizForm.columns" 
                multiple 
                placeholder="请选择要可视化的列"
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
                <el-radio label="plotly">Plotly (交互式)</el-radio>
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
                <el-radio label="plotly">Plotly (交互式)</el-radio>
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
          
          <!-- Plotly图表 -->
          <div 
            v-if="result.chart_type === 'plotly'" 
            :id="`plotly-chart-${index}`"
            class="chart-container"
          />
          
          <!-- Matplotlib图片 -->
          <div v-else-if="result.chart_type === 'matplotlib'" class="chart-container">
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
                <div 
                  v-if="subResult.chart_type === 'plotly'"
                  :id="`plotly-chart-${index}-${subKey}`"
                  class="chart-container"
                />
                <div v-else class="chart-container">
                  <img 
                    :src="`data:image/png;base64,${subResult.chart_data}`" 
                    alt="Chart"
                    style="max-width: 100%; height: auto;"
                  />
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
  getDataPreview 
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
        type: 'distribution',
        columns: [],
        x_column: '',
        y_column: '',
        chart_type: 'plotly'
      },
      modelVizForm: {
        type: 'prediction',
        model_id: '',
        chart_type: 'plotly'
      },
      visualizationResults: [],
      visualizationHistory: [],
      loading: {
        dataViz: false,
        modelViz: false
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
        if (response.train_preview) {
          this.dataColumns = response.train_preview.columns || []
          this.numericColumns = response.train_preview.columns?.filter(col => 
            response.train_preview.dtypes[col]?.includes('float') || 
            response.train_preview.dtypes[col]?.includes('int')
          ) || []
          
          // 默认选择前6个数值列
          this.dataVizForm.columns = this.numericColumns.slice(0, 6)
          if (this.numericColumns.length >= 2) {
            this.dataVizForm.x_column = this.numericColumns[0]
            this.dataVizForm.y_column = this.numericColumns[1]
          }
        }
      } catch (error) {
        console.error('加载数据信息失败:', error)
      }
    },
    
    loadAvailableModels() {
      // 模拟可用模型数据，实际应该从API获取
      this.availableModels = [
        { id: 'model_1', name: '随机森林模型' },
        { id: 'model_2', name: 'XGBoost模型' },
        { id: 'model_3', name: '线性回归模型' }
      ]
    },
    
    onDataVizTypeChange() {
      // 根据类型重置相关配置
      if (this.dataVizForm.type === 'correlation') {
        this.dataVizForm.columns = []
      } else if (this.dataVizForm.type === 'scatter') {
        this.dataVizForm.columns = []
      }
    },
    
    async generateDataVisualization() {
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
        
        const response = await generateDataVisualization(params)
        
        if (response.success) {
          const result = {
            title: this.getDataVizTitle(),
            type: 'data',
            chart_type: this.dataVizForm.chart_type,
            ...response
          }
          
          this.visualizationResults.push(result)
          this.addToHistory(result)
          
          // 如果是Plotly图表，需要在下一个tick渲染
          if (response.chart_type === 'plotly') {
            this.$nextTick(() => {
              this.renderPlotlyChart(result, this.visualizationResults.length - 1)
            })
          }
          
          this.$message.success('数据可视化生成成功')
        }
      } catch (error) {
        console.error('生成数据可视化失败:', error)
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
        const response = await generateModelVisualization(this.modelVizForm)
        
        if (response.success) {
          const result = {
            title: this.getModelVizTitle(),
            type: 'model',
            chart_type: this.modelVizForm.chart_type,
            ...response
          }
          
          this.visualizationResults.push(result)
          this.addToHistory(result)
          
          // 处理多个结果的情况
          if (response.results) {
            result.activeTab = Object.keys(response.results)[0]
            this.$nextTick(() => {
              Object.keys(response.results).forEach((key, index) => {
                if (response.results[key].chart_type === 'plotly') {
                  this.renderPlotlyChart(
                    response.results[key], 
                    `${this.visualizationResults.length - 1}-${key}`
                  )
                }
              })
            })
          } else if (response.chart_type === 'plotly') {
            this.$nextTick(() => {
              this.renderPlotlyChart(result, this.visualizationResults.length - 1)
            })
          }
          
          this.$message.success('模型可视化生成成功')
        }
      } catch (error) {
        console.error('生成模型可视化失败:', error)
      } finally {
        this.loading.modelViz = false
      }
    },
    
    renderPlotlyChart(chartData, chartId) {
      // 这里需要引入Plotly库来渲染图表
      // 由于没有实际的Plotly数据，这里只是占位
      console.log('渲染Plotly图表:', chartId, chartData)
      
      // 实际代码应该是：
      // if (window.Plotly && chartData.chart_data) {
      //   const plotData = JSON.parse(chartData.chart_data)
      //   Plotly.newPlot(`plotly-chart-${chartId}`, plotData.data, plotData.layout)
      // }
    },
    
    getDataVizTitle() {
      const typeNames = {
        'distribution': '数据分布图',
        'correlation': '相关性矩阵',
        'scatter': '散点图',
        'box': '箱线图',
        'histogram': '直方图'
      }
      return typeNames[this.dataVizForm.type] || '数据可视化'
    },
    
    getModelVizTitle() {
      const typeNames = {
        'prediction': '预测vs实际值',
        'residuals': '残差图',
        'feature_importance': '特征重要性',
        'learning_curve': '学习曲线'
      }
      return typeNames[this.modelVizForm.type] || '模型可视化'
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
      
      if (historyItem.chart_type === 'plotly') {
        this.$nextTick(() => {
          this.renderPlotlyChart(historyItem.data, this.visualizationResults.length - 1)
        })
      }
    }
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

.chart-container {
  min-height: 300px;
  background: white;
  border-radius: 4px;
  padding: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.multi-results {
  background: white;
  border-radius: 4px;
}
</style> 