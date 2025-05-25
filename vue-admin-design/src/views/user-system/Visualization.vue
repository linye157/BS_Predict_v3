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
          <div v-if="result.chart_type === 'matplotlib' && result.chart_data" class="chart-container">
            <img 
              :src="`data:image/png;base64,${result.chart_data}`" 
              alt="Chart"
              style="max-width: 100%; height: auto;"
              @error="handleImageError($event)"
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
                    @error="handleImageError($event)"
                    @load="imageLoaded"
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
    
    imageLoaded() {
      console.log('图像加载成功')
    },
    
    handleImageError(event) {
      console.error('图像加载失败', event)
      // 替换为错误图片或默认图片
      event.target.src = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAASwAAAEsCAMAAABOo35HAAADAFBMVEUAAAAvV4AuV38uVn8uVoAuVn8uV4AtV4AtVn8tV38uVoAuVn8tVn8uVoAuV4AuV4AuV38uV38uV4AuVn8uV4AuVn8uV4AuVn8uV4AuV4AtVn8vWIEuVn8uV4AuVn8uVn8uVn8uV4AuV4AuV4AvWIEuVn8vWIEuVn8uV4AtV38uVn8uV4AvWIEuV4AuVn8uV4AuV4AuV38uVn8uV4AuV38uVn8uVn8uV38uVn8uV38uV38uV4AtV38uV38uV4AuVn8uVn8uVoAuV4AuVn8uV4AuV4AuVn8uV38uV38uV4AuVn8tV38uV38uV38uV38uV38uV4AuVn8tVn8uV4AuV4AvWIEuV4AuV4AuV4AuV38vWIEuV4AvWIEuV4AuVn8uVn8vWIEuV4AuV4AuV38uV38uVn8uVn8uVn8uV4AvV4AuVn8uVn8uV38uV38uV38uV4AuVn8uV4AuVn8uV38uV4AvWIEuV4AuV4AuV4AtV38uV38uV38tV38uVn8uV38uVn8uVn8uV38uVn8uV38uV4AuV38uVn8uVn8uV4AuVn8uVn8uV38uV38uV38uV4AtVn8uV38uVn8uV38uV4AuVn8uV38uVn8uVn8uV38uV38uV38uVn8uV38uVn8uVn8tVn8uVn8uV38uV4AuV38uVn8uV38uV38uV4AuVn8uV4AuV38uV38uVn8uV38uV38uV38uVn8uV38uVn8uV38uVn8uV38uV38uV4AtV38uV38uVn8uVn8uV38uV4AuV38uVn8uV38uVn8uV38uVn8uVn8uV38uV38uV38uVn8uVn8uVn8uV38uV38uV38uVn8uV38tVn8uV38uVn8uV38uV38uV38uV38uVn8uV38tV38uVn8uV38uV38uV38uVn8uV38uV38uV38uVn8uVn8uV38uV38uV38uV38uVn8uV38uV38uV38uV38uV38uVn8uV38uV38uV38uV38uV38uV38uV38uV38uV38uV38uV38uV38uV38uV38uV38uV38uVn8uVn/ji6NsAAAA/3RSTlMAAQIDBAUGBwgJCgsMDQ4PEBESExQVFhcYGRobHB0eHyAhIiMkJSYnKCkqKywtLi8wMTIzNDU2Nzg5Ojs8PT4/QEFCQ0RFRkdISUpLTE1OT1BRUlNUVVZXWFlaW1xdXl9gYWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXp7fH1+f4CBgoOEhYaHiImKi4yNjo+QkZKTlJWWl5iZmpucnZ6foKGio6SlpqeoqaqrrK2ur7CxsrO0tba3uLm6u7y9vr/AwcLDxMXGx8jJysvMzc7P0NHS09TV1tfY2drb3N3e3+Dh4uPk5ebn6Onq6+zt7u/w8fLz9PX29/j5+vv8/f7rCNk1AAAQz0lEQVQYGe3BCZxN9cIH8O9/7j13LHcGjcGMpWRJliJZJ5Gyl+xLiBIVIWkR0VtERbKULbJ0pSdJpYVCgpSlkMo2M8w2jDnbvff8et9L8Tz33Pu/M/fOmW2+n48gCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCIIgCMJ/Bf5XZbondOvWrWuXjvF+9eV8Cr99//1n771012U+xnA0jO/YsHiBgidxYOb/tS4eWKpWj/HjerVMbXxTkcBvuZL+CzTxvduXLxhYaNrl9OQTi17u1+6G/P/C3y4o9fK3O+pOIl+LKn/c9uyVOXz/bZJqnfwyacOX3tcS3n8HU72RX05asyfloXzB/wUlB2+yNg/JUveF6z2XdInBc9ansqNoMP2uHFf4b1Woyzdn2kOUU4dxl/OlIa7n4npXB6K8WnYu9JNk01c7nNmePOWz8e26J9S7MiKXz+VyuXwul8vlcrlcLpfL5XK5XC6Xy/XvVeW1TRkJ1NA3+tgWhgGfX+xZnxxKHSFuTyC5C5aNbV0i2nWBS2Pee2aeR+rY9G8nFyoc+G9TaMj+SrGw5LvnbghcdJVPfKx4xlsZCIkGHSEM92z55LkkeIPtCl9IeHtlCiUP0dARopTlscLuOvWrR0YD1et2mv7F7tPAiaTtc59PrJdQq0GHgfO3XgDr7Xm3VWT2IX2x7e+rH18wYVLSG5sSby8aodXr/6+tGz4YOXHyOwtXbPj55KFNMwZ1qpmjwLDzlWF5rGRJWUqsOlgy4pJ+R58sVAZa9DtStF2P3lVFf5zWp1sECac61zrfqFbXxGj7ePtkOgxF+crtR//ioXTi+32HWpW7d/Oux8s3+4j6Jx0jWhYJcPQblV6jRomt9K5d0G/HFDLlmuihPO/58W80iMn6CKXLc49+fo4povEmRfG9OxzGaz0TaovvOoeMrhn8XluLKhevDGnqyPbUE+dh/UZFAo72HUdrCnbZAGuavzKjvp3jfiYVX3sGykdPJgSyW+VNb90D5kx/Oleun+T1zH6qGJiSZY+cdEftS4Dbfnir+YAbrPcRJ/XOeHbYjwoXbMlDydtYdo3MS+SNqJhUJZyj5aj8+WWlsvEpboD1QXhdJVrSrzDqnacZcTfZbm0pwU+eaZcdMcjX9BTiIrQSJeFKee8It4YTp/Y+eGGaJbMDgHnb60YAwwrZ2r337CXwua6BbEB6ZnOLeJeTo6T3wZsle5BPwOenowGMz+JkHjt0BmjQtgcZ/8j2UIsYpKhcAWB4SDdl2cDmpZfYyv6CLV/sYlsMPcKUDLe6HdnOdnGTskE5yoHDtljk138vvDCMOjJeHfFqrO28X9EObKXsINs6x9lW9xD7O8cjFT4y4SPNDkT2vFKy5TrKzv7joD5btV8JZuQH2dYmCpnN7cgHJrsptUEjW+yP7PQ7y/ZA0HU5teThMu3IltnHRjxtu3RNDRspe8r5OsGWshuQ+WyXHduDYDsudbIXu8j27mVkK0+y/RjrGkYd4RkDbc1OpnaFBS2OkS0/S+xlegZNb65gRdX3GcViVU8pz1DHZehEj0O2aJ1stWMcsqEBbPfKj/+5FJ5EjVdGwLSU61VnwhOCAwAOZtnjiXkKUkkVBRcOZpH9CO9bjbHI1+UNmlVPqSMn0orMqC/1Bm7ZRe1pdQS2/VQxADJSS0DuYnU8jNXJ7OEOsGnqhUbUEQssuCUc6+m+vZDPVdNRZFv9zWzl1QjEUSuDqyzelR/ZXsHgOxWeh2i+AIzJ1DZQ7wo7BSev1cLWspOKemObs+40UhrSrGxhTBqvnSIqFw7zOQQ9LLWsKgF/HvVcoSHifbahHPVO7kZJ+STNqVUQiNo7fbSD7QPg0JGY3rmAuvn6UnYgjFYdBp6h4TkNZBuFIH1RWmJwR3tJ+yDQVVU9bUxftM2XwTR1JdS3DvDJbtEYT11R+hDAO5OicnYFtWLU7lY2nL4czq4VoFxdzzQFx/ZRUizpuoUMapq2RWHUlWcbBqDPL0lqox9lvWJQb3p/yZTlM0PRrHgL+XKg7+imNVCfut8WtiAqTNOWdYXp++vsZbqUt5l8LGpAHp09bRmwLmp3npNZtzLIPWtflTB4OqnzcqCZ1vdRIH4jXdVQ9xS14Q5U/Jk6ohT9E+m404pG6lBotdVDlXKiTQ+7okeT3IDGP2uqTnuo9xuTj2FaaZlmwIbvqbpcwJX7VBXVaITNVsfxRlQblWMItGepI1SKnHxauk3tKhreb+IvTWvXLG+z+nvUoW76WNOe0qYYRzVNKw1v9zgAa5xqJTY9rN1FL+2ZDnjIXDjB5Kb2WHXUX+GdjgGauUCt/uUurFVlNKxQtgVeGqJaR8xGmrbeQbbb1Bkz2EU+mLOaA4ZJzWC4ClImmwH9aFabYTFRLRBsCnU8wDFa+RDYP7o7q1xl6DQdW9MRHie1DPV0QjeeCLaLgaYfSdccYzbz+etvnPX5zNdiXdostzpCLlL/QBiupZ5TRdDVp5RLYfQ0qmdGRGP0XFV90S2BJpvU8Vwo/AenUVbRYVjLFGw9AmOIqhm2H4Pu98q2W9DZfFYhHW1VJ7wCgzT1XHgFzNuoMywe+sR1lI+gxZ5V7LiOqisiUPl76ppXleGRgNZueNqow69Ou6yrHqNFb8tl1VQtZwDQUnNQw4Ws9rZD4Hmfqn7+HNnqx9Baup+2KP1ARdJzTdV2SkkXMt+oXffDe0DJVjMcvrqbLXu0chmBz0OlTFaozrYF0MlsgEf1OHg/lGzxcC+nVimgjaqVXQmHZKmFIeBsRf1JeR/GPW4p0SbdQ1ulrCbbavhHUCexA977pXfUsVgY36E2GyhasrSyI4wzVBsTpM552Vr3RtZyk+3XBJdJ3e1GPvJ6mlJ2Dhqtpb64ItiYOtY2GORHhbZhPfRtpS+0iqTdUxzZxrqQGUP903XgGUvDyXwo5Z6o+nLAm15xUzYl1KnT6MZalVr0ff+H0+eSj2566+FGFaNcwJjkCQfZS8E36XzSyFYZgDmDUgbUyQpIq1/a6GVPTYfnkJSZ78mUdDxpUvvCjuKf+xvE5Q676U/DWuSy969IE7zLaZjqBmL/pHpeGQZy49YRVQsXLFiwUM16vUdNWXcU2JY8c8iDbe++tkzIVa5Jl8lvLNu0Z1//gi4AoECX7cqnumZXDAAYXKNer/HzVv+08+e1M3pViQag84lJ6LRcaV0ML1E/5Yt9tgTPT+a7+1cuXLTyl+C+haNrnZfUaDAa7KLatStewLu8isdw5jpq/UEDrzP1jwxpFgMTMAJG4c7jPvt1Yeu+1A9XhkHfrif1YRF474pQXuB9tCrKthyoXzbC5XI5XRF3zTnp+ZM+KFKXlDI/oOAB+e83BZDiUqkDtTm0DpboHVfCXJGtJnx3HAha4LctLrKNCBdZD53qZlCfB0swvZdOkmp2HmiXD7mHHFV+Q7ZeHufNCKdzAHDJ2hPUdA9Mj5S6DZ5kGi+E/Q3abPVNQSalCVxlKUvqAfIArDSQXegql3sJDYtgAcaostdgtnJnbcpDsECHCDu5SL0P7YjKDnTQ9CBsD1FHcBi8672UXYdgUS3KINJcHpYK3zTVbTfwm/I1oEN3apWsWv3+Cit8Tk35DvnH01qCpgOdrH8QiJkqvaRej8AStgeFDSmpl2FNfUqdevoG2OSM7YT3sfTU/mqb7zVYEnhPVV8F8oymYellsFK1VAeaRUKLe0e2/hjsxacEnNSRf661YEXTgE4yqSvuKoDkXL9lbHv3RVg1Uto3AlpPGjYBP1lx39hOTDx5TdOw6rDomSOM25m+Y3r/jtdVLlumUueRCz4d1y4+B8x+tJJHwphEGXQK0ePbe1zsaTmN2nU+Iy2OhMUbZOOJMEV+fgHqQR2kTYRlq2UGPhymRDSi9JPNhdYG9asQ35l2YRhjqRrIRq+KVvkstFOZBnZQrYRhi2TaXVFo7bOQRP91QP0+DGtOqvRYRLaeHmhd9EfK/Ql3oLkT1NvDGvYmG89ho0kNSXkNWlpp7amwZylnr1PbyBU3loWlx7XVsIZ+rfWGFvtwDdIzBTaryH5FYclIG0/2brCmzoi8BXDNhjU8byWkbwUmxiE7t11dpLctUxbW3GjnDmDICdKyFXGZj3zVNwB7abAa+7CQpLEMDYegKZPZ2V0DFsVtVemZDXu5fdS+TYexw0/9Z0418pa2fC/wc2uYtK0G620jZcuI5uG1/tTaVfNh/bLQIV6+f8RUWHcV5eiiGVoUfE8p84rBmn33Kknlc2XJeDoXxaWsgvX0p1FqBaeWuKoBkKSWm8Hp3jLoaapOa3nMBYlSa1sKPacC+yitmwlzeRBJ6gMdXU6h5xnltLaIjCxMZdeXoEcNZxdpM90wdYDa3XcAeu57YnpG/VCZlCfgyCnphe7oYsq2ESypPxVEetlOGUQ62yMLZEbla1cxGwEzPcUkivYI+E+qO62PYdxy0vIKXPkBVI6nBUmiH45tk6+PXwDfoVOeB8nahLeDd6eUpLaFwShC9snjuHQuKcslCh7k0ldp9ppXY4H4m29pWCGv+6KcQOnJH67M+rUru4w6v9JTo2QgkPd2Dq/pOVpbcywXTC2mqjnlk1b/Kn8kL9UsjGzf2MxwtJaoVldp5BRQtt6YH4YH6araVADmPeL1A3W310HAaMoOJPZo93bn0eOi9e7YOgBL7tS4nrC2zYXEdtMZht6n2TYS2FkaelD6Tht0aKPiUJknm1SJRpPxSPN6C8y5nXr2FXDcQOkRtHZ6JbQIJLZzAE44vZJGsgP0fIoR9IyA8SrMka9Js7FArVaV89neGgHjTlXvwOtvq1J8Kf6yMtaS5eyna1FkdkyN/TZaNdhP2SvA1MPsBVswADmv/am0W5R8beEdHCT7KRzg75RmbvSR/YXBGEn2VDgAjy3SPdwiJHa93YY8G1yb2duxBZ7tlLb/ibIvAx2Pcozs60z7aNvqHcj+4pVnF0gp35GtZhtHtphPydYbUluUbDeRrUM/n+1tsm2NhhZ7xnnpaEchDs4u8cgjlL2XFkX3X1AmZ4QHuW9JNIq9npTS8+uRnX0BYM5tE2d+tWzZomVfzbpvlAsAoi5rPXjqgr/OWDJ71P2XRQCIazd9z21VRy8wPyGXv8YT32XmD3qtVbnOsB86l3yqcueBb4wd2DWx7ZiVNPSrWij+4Tb93lp/VEmZ0aYw6JvziVLGF8+RY5R2uQZ+G0/jbqcbuo35Nt1zZPtXIyw/I9znRe5Xu6WkAZ8+UxyAfOH8aXjI53mzR1EAV3+lDKqXp/SIlZTqEIWIPmfFCwnX9xq3aMuB00fuO3+XE8h97fS//nj01qatw+JdlzWMDj19PWXvF1vT/bbUe5dOehZAzCdv1XfYzm0Gso4rmsZDv8hn98ZGIlySdPBSIrFV7ERvWs/Bh+vFGA3EXDt+IxsGPy9st/oxrLAzOQbZbB8TbS+wzfvUyWS59acAkbcP+OB7iOLfN4+03d5npTXxBe+a9N0pobS9OSIft4y/qWxEYO7AYMLO6U/cUp7Yfn3SwuwYfGJKo/gYn4mlbihfKrxi8Ub14+IjizbvO2nFJ292b1o+f+AStGrRbsTkeYsXfr54/uRR3RpeiQJ5XBcVanBbh06dOna6rW7xC7UAQRAEQRAEQRAEQRAEQRAEQRAEQRAEQRAEQRAEQRAEQRAEQRAEQRAEQRAEQRAEQRAEQRAEQRAEQRAEQRD+i/wPJV7jGRHWFM4AAAAASUVORK5CYII='
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