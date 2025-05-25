<template>
  <div class="reports">
    <div class="page-header">
      <h2>报表</h2>
      <p>报表项目订制、报表自动生成、报表多维度信息展示、报表多种格式下载、不同时间端报表对比分析、报表存储</p>
    </div>

    <!-- 报表生成配置 -->
    <el-card class="section-card">
      <div slot="header" class="section-header">
        <span><i class="el-icon-document-add"></i> 报表生成</span>
      </div>
      
      <el-form :model="reportForm" label-width="150px" ref="reportForm">
        <el-form-item label="报表类型">
          <el-select v-model="reportForm.report_type" @change="onReportTypeChange">
            <el-option label="数据分析报表" value="data_analysis" />
            <el-option label="模型训练报表" value="model_training" />
            <el-option label="性能评估报表" value="performance_evaluation" />
            <el-option label="综合分析报表" value="comprehensive" />
            <el-option label="自定义报表" value="custom" />
          </el-select>
        </el-form-item>

        <el-form-item label="报表标题">
          <el-input v-model="reportForm.title" placeholder="请输入报表标题" />
        </el-form-item>

        <el-form-item label="包含内容">
          <el-checkbox-group v-model="reportForm.content_sections">
            <el-checkbox label="data_summary">数据摘要</el-checkbox>
            <el-checkbox label="model_info">模型信息</el-checkbox>
            <el-checkbox label="performance_metrics">性能指标</el-checkbox>
            <el-checkbox label="visualizations">可视化图表</el-checkbox>
            <el-checkbox label="conclusions">结论与建议</el-checkbox>
            <el-checkbox label="technical_details">技术细节</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item label="选择模型" v-if="reportForm.content_sections.includes('model_info')">
          <el-select 
            v-model="reportForm.selected_models" 
            multiple 
            placeholder="请选择要包含的模型"
            style="width: 100%"
          >
            <el-option 
              v-for="model in availableModels" 
              :key="model.id"
              :label="model.name" 
              :value="model.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="输出格式">
          <el-checkbox-group v-model="reportForm.output_formats">
            <el-checkbox label="html">HTML</el-checkbox>
            <el-checkbox label="pdf">PDF</el-checkbox>
            <el-checkbox label="docx">DOCX</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item label="报表模板">
          <el-select v-model="reportForm.template">
            <el-option label="标准模板" value="standard" />
            <el-option label="详细模板" value="detailed" />
            <el-option label="简洁模板" value="minimal" />
            <el-option label="执行摘要" value="executive" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button 
            type="primary" 
            @click="generateReport"
            :loading="loading.generate"
            size="large"
          >
            <i class="el-icon-document-add"></i> 生成报表
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 报表列表 -->
    <el-card class="section-card">
      <div slot="header" class="section-header">
        <span><i class="el-icon-folder-opened"></i> 报表列表</span>
        <div style="float: right;">
          <el-button 
            type="text" 
            @click="refreshReports"
            :loading="loading.refresh"
            icon="el-icon-refresh"
          >
            刷新
          </el-button>
          <el-button 
            type="text" 
            @click="showComparisonDialog = true"
            icon="el-icon-data-analysis"
          >
            对比分析
          </el-button>
        </div>
      </div>
      
      <el-table :data="reportsList" border stripe v-loading="loading.list">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="title" label="报表标题" />
        <el-table-column prop="type" label="类型" width="120">
          <template slot-scope="scope">
            <el-tag :type="getReportTypeColor(scope.row.type)">
              {{ getReportTypeName(scope.row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column prop="formats" label="格式" width="120">
          <template slot-scope="scope">
            <el-tag 
              v-for="format in scope.row.formats" 
              :key="format"
              size="mini"
              style="margin-right: 5px;"
            >
              {{ format.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="size" label="文件大小" width="100" />
        <el-table-column label="操作" width="250">
          <template slot-scope="scope">
            <el-dropdown @command="(command) => handleReportAction(command, scope.row)">
              <el-button type="text">
                预览 <i class="el-icon-arrow-down el-icon--right"></i>
              </el-button>
              <el-dropdown-menu slot="dropdown">
                <el-dropdown-item command="preview">预览报表</el-dropdown-item>
                <el-dropdown-item divided command="download-html">下载HTML</el-dropdown-item>
                <el-dropdown-item command="download-pdf">下载PDF</el-dropdown-item>
                <el-dropdown-item command="download-docx">下载DOCX</el-dropdown-item>
                <el-dropdown-item divided command="share">分享报表</el-dropdown-item>
                <el-dropdown-item command="delete" style="color: #F56C6C;">删除报表</el-dropdown-item>
              </el-dropdown-menu>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 报表预览对话框 -->
    <el-dialog 
      :title="previewReport?.title" 
      :visible.sync="showPreviewDialog"
      width="80%"
      top="5vh"
    >
      <div v-if="previewReport" class="report-preview">
        <div v-html="previewReport.content" />
      </div>
      <div slot="footer" class="dialog-footer">
        <el-button @click="showPreviewDialog = false">关闭</el-button>
        <el-button 
          type="primary" 
          @click="downloadReport(previewReport, 'html')"
        >
          下载HTML
        </el-button>
        <el-button 
          type="primary" 
          @click="downloadReport(previewReport, 'pdf')"
        >
          下载PDF
        </el-button>
      </div>
    </el-dialog>

    <!-- 报表对比分析对话框 -->
    <el-dialog 
      title="报表对比分析" 
      :visible.sync="showComparisonDialog"
      width="70%"
    >
      <el-form :model="comparisonForm" label-width="120px">
        <el-form-item label="选择报表">
          <el-select 
            v-model="comparisonForm.reports" 
            multiple 
            placeholder="请选择要对比的报表（2-5个）"
            style="width: 100%"
          >
            <el-option 
              v-for="report in reportsList" 
              :key="report.id"
              :label="report.title" 
              :value="report.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="对比维度">
          <el-checkbox-group v-model="comparisonForm.dimensions">
            <el-checkbox label="performance">性能指标</el-checkbox>
            <el-checkbox label="accuracy">准确率对比</el-checkbox>
            <el-checkbox label="time_trends">时间趋势</el-checkbox>
            <el-checkbox label="model_comparison">模型对比</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>

      <div slot="footer" class="dialog-footer">
        <el-button @click="showComparisonDialog = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="generateComparison"
          :loading="loading.comparison"
        >
          生成对比报告
        </el-button>
      </div>
    </el-dialog>

    <!-- 分享对话框 -->
    <el-dialog 
      title="分享报表" 
      :visible.sync="showShareDialog"
      width="50%"
    >
      <div v-if="shareInfo">
        <el-form label-width="100px">
          <el-form-item label="分享链接">
            <el-input 
              v-model="shareInfo.link" 
              readonly
              style="width: 70%"
            />
            <el-button 
              type="primary" 
              @click="copyShareLink"
              style="margin-left: 10px;"
            >
              复制链接
            </el-button>
          </el-form-item>

          <el-form-item label="有效期">
            <el-select v-model="shareInfo.expiry">
              <el-option label="1天" value="1d" />
              <el-option label="7天" value="7d" />
              <el-option label="30天" value="30d" />
              <el-option label="永久" value="never" />
            </el-select>
          </el-form-item>

          <el-form-item label="访问权限">
            <el-radio-group v-model="shareInfo.permission">
              <el-radio label="view">仅查看</el-radio>
              <el-radio label="download">允许下载</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-form>
      </div>

      <div slot="footer" class="dialog-footer">
        <el-button @click="showShareDialog = false">关闭</el-button>
        <el-button type="primary" @click="updateShareSettings">更新设置</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { 
  generateReport,
  getReportsList,
  downloadReportFile,
  deleteReport,
  getModelsList 
} from '@/api/mlApi'

export default {
  name: 'Reports',
  data() {
    return {
      reportForm: {
        report_type: 'data_analysis',
        title: '',
        content_sections: ['data_summary', 'model_info', 'performance_metrics'],
        selected_models: [],
        output_formats: ['html'],
        template: 'standard'
      },
      comparisonForm: {
        reports: [],
        dimensions: ['performance']
      },
      availableModels: [],
      reportsList: [],
      previewReport: null,
      shareInfo: null,
      showPreviewDialog: false,
      showComparisonDialog: false,
      showShareDialog: false,
      loading: {
        generate: false,
        list: false,
        refresh: false,
        comparison: false
      }
    }
  },
  async mounted() {
    await this.loadReportsList()
    this.loadAvailableModels()
  },
  methods: {
    onReportTypeChange() {
      // 根据报表类型设置默认内容
      const defaultContent = {
        'data_analysis': ['data_summary', 'visualizations'],
        'model_training': ['model_info', 'performance_metrics'],
        'performance_evaluation': ['performance_metrics', 'visualizations'],
        'comprehensive': ['data_summary', 'model_info', 'performance_metrics', 'visualizations', 'conclusions'],
        'custom': []
      }
      
      this.reportForm.content_sections = defaultContent[this.reportForm.report_type] || []
      
      // 设置默认标题
      const titleMap = {
        'data_analysis': '数据分析报表',
        'model_training': '模型训练报表',
        'performance_evaluation': '性能评估报表',
        'comprehensive': '综合分析报表',
        'custom': '自定义报表'
      }
      
      if (!this.reportForm.title) {
        this.reportForm.title = titleMap[this.reportForm.report_type] + ' - ' + new Date().toLocaleDateString()
      }
    },
    
    async loadAvailableModels() {
      try {
        const response = await getModelsList()
        console.log('报表模型列表响应:', response)
        
        if (response.success && response.models) {
          this.availableModels = response.models.map(model => ({
            id: model.id,
            name: `${model.name} (${model.type})`
          }))
          
          console.log('报表加载的模型列表:', this.availableModels)
          
          if (this.availableModels.length === 0) {
            this.$message.info('暂无可用的训练模型，请先训练模型')
          }
        } else {
          console.warn('获取模型列表失败:', response.message)
          this.availableModels = []
        }
      } catch (error) {
        console.error('加载模型列表失败:', error)
        this.availableModels = []
        this.$message.error('加载模型列表失败: ' + (error.message || '未知错误'))
      }
    },
    
    async loadReportsList() {
      this.loading.list = true
      try {
        const response = await getReportsList()
        this.reportsList = response.reports || this.generateMockReports()
      } catch (error) {
        console.error('加载报表列表失败:', error)
        this.reportsList = this.generateMockReports()
      } finally {
        this.loading.list = false
      }
    },
    
    generateMockReports() {
      // 生成模拟报表数据
      return [
        {
          id: 'report_1',
          title: '数据分析报表 - 2024-01-15',
          type: 'data_analysis',
          created_at: '2024-01-15 14:30:00',
          formats: ['html', 'pdf'],
          size: '2.3MB'
        },
        {
          id: 'report_2',
          title: '模型训练报表 - RandomForest',
          type: 'model_training',
          created_at: '2024-01-14 10:15:00',
          formats: ['html', 'docx'],
          size: '1.8MB'
        },
        {
          id: 'report_3',
          title: '综合分析报表 - Q1',
          type: 'comprehensive',
          created_at: '2024-01-12 16:45:00',
          formats: ['html', 'pdf', 'docx'],
          size: '5.2MB'
        }
      ]
    },
    
    async generateReport() {
      if (!this.reportForm.title) {
        this.$message.warning('请输入报表标题')
        return
      }
      
      if (this.reportForm.content_sections.length === 0) {
        this.$message.warning('请选择报表内容')
        return
      }
      
      if (this.reportForm.output_formats.length === 0) {
        this.$message.warning('请选择输出格式')
        return
      }
      
      this.loading.generate = true
      try {
        console.log('生成报表参数:', this.reportForm)
        const response = await generateReport(this.reportForm)
        console.log('报表生成响应:', response)
        
        if (response.success) {
          this.$message.success('报表生成成功')
          await this.loadReportsList()
          
          // 重置表单
          this.reportForm = {
            report_type: 'data_analysis',
            title: '',
            content_sections: ['data_summary', 'model_info', 'performance_metrics'],
            selected_models: [],
            output_formats: ['html'],
            template: 'standard'
          }
        } else {
          this.$message.error(response.message || '报表生成失败')
        }
      } catch (error) {
        console.error('生成报表失败:', error)
        this.$message.error('生成报表失败: ' + (error.message || '未知错误'))
      } finally {
        this.loading.generate = false
      }
    },
    
    async refreshReports() {
      this.loading.refresh = true
      await this.loadReportsList()
      this.loading.refresh = false
      this.$message.success('报表列表已刷新')
    },
    
    async handleReportAction(command, report) {
      switch (command) {
        case 'preview':
          await this.previewReportContent(report)
          break
        case 'download-html':
          await this.downloadReport(report, 'html')
          break
        case 'download-pdf':
          await this.downloadReport(report, 'pdf')
          break
        case 'download-docx':
          await this.downloadReport(report, 'docx')
          break
        case 'share':
          this.shareReport(report)
          break
        case 'delete':
          await this.deleteReportConfirm(report)
          break
      }
    },
    
    async previewReportContent(report) {
      try {
        // 实际从后端获取报表内容
        this.$message.info('正在加载报表内容...')
        
        // 使用新窗口打开方式更可靠
        // 先在新窗口直接打开报表
        window.open(`/api/reports/download/${report.id}/html?preview=true`, '_blank')
        
        // 同时加载预览对话框
        try {
          // 使用preview参数标记这是预览模式，直接返回内容而非下载附件
          const response = await fetch(`/api/reports/download/${report.id}/html?preview=true`)
          
          if (response.ok) {
            const htmlContent = await response.text()
            console.log('获取到报表内容，长度:', htmlContent.length)
            
            if (htmlContent.startsWith('{') && htmlContent.includes('error')) {
              // 可能是JSON错误响应
              try {
                const errorJson = JSON.parse(htmlContent)
                throw new Error(errorJson.error || errorJson.message || '获取报表内容失败')
              } catch (jsonError) {
                // 解析失败，继续使用原始内容
              }
            }
            
            this.previewReport = {
              ...report,
              content: htmlContent
            }
            this.showPreviewDialog = true
          } else {
            throw new Error(`报表内容获取失败: ${response.status} ${response.statusText}`)
          }
        } catch (fetchError) {
          console.error('获取实际报表内容失败:', fetchError)
          this.$message.warning('无法在对话框中加载报表内容，但已在新窗口打开')
          
          // 不再使用模拟数据，因为已在新窗口打开
          this.showPreviewDialog = false
        }
      } catch (error) {
        console.error('加载报表内容失败:', error)
        this.$message.error('加载报表内容失败: ' + (error.message || '未知错误'))
      }
    },
    
    generateMockReportContent(report) {
      return `
        <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
          <h1 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
            ${report.title}
          </h1>
          
          <div style="margin: 20px 0; padding: 15px; background: #f8f9fa; border-left: 4px solid #3498db;">
            <h2>数据摘要</h2>
            <p>本报表基于训练数据集进行分析，包含以下关键信息：</p>
            <ul>
              <li>数据集大小: 10,000 条记录</li>
              <li>特征数量: 15 个</li>
              <li>目标变量: 3 个</li>
              <li>数据质量: 95.2% 完整度</li>
            </ul>
          </div>
          
          <div style="margin: 20px 0;">
            <h2>模型信息</h2>
            <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
              <tr style="background: #3498db; color: white;">
                <th style="padding: 10px; border: 1px solid #ddd;">模型类型</th>
                <th style="padding: 10px; border: 1px solid #ddd;">R² 分数</th>
                <th style="padding: 10px; border: 1px solid #ddd;">RMSE</th>
              </tr>
              <tr>
                <td style="padding: 10px; border: 1px solid #ddd;">随机森林</td>
                <td style="padding: 10px; border: 1px solid #ddd;">0.923</td>
                <td style="padding: 10px; border: 1px solid #ddd;">0.156</td>
              </tr>
              <tr style="background: #f2f2f2;">
                <td style="padding: 10px; border: 1px solid #ddd;">XGBoost</td>
                <td style="padding: 10px; border: 1px solid #ddd;">0.945</td>
                <td style="padding: 10px; border: 1px solid #ddd;">0.132</td>
              </tr>
            </table>
          </div>
          
          <div style="margin: 20px 0; padding: 15px; background: #e8f5e8; border-left: 4px solid #27ae60;">
            <h2>结论与建议</h2>
            <p>基于分析结果，我们得出以下结论：</p>
            <ol>
              <li>XGBoost模型表现最佳，建议作为主要预测模型</li>
              <li>数据质量良好，可以支持进一步的模型优化</li>
              <li>建议增加更多特征工程来提升模型性能</li>
            </ol>
          </div>
          
          <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666;">
            <p>报表生成时间: ${new Date().toLocaleString()}</p>
            <p>系统版本: BS_Predict_v4</p>
          </div>
        </div>
      `
    },
    
    async downloadReport(report, format) {
      try {
        this.$message.info(`正在下载${format.toUpperCase()}报表...`)
        
        console.log(`尝试下载报表: ${report.id}, 格式: ${format}, 标题: ${report.title || '未命名'}`)
        
        // 构建完整链接并创建blob
        const url = `/api/reports/download/${report.id}/${format}`
        
        try {
          // 创建一个表单进行下载(回退方案)
          const form = document.createElement('form')
          form.style.display = 'none' // 隐藏表单
          form.method = 'GET'
          form.action = url
          form.target = '_blank' // 在新窗口打开
          
          document.body.appendChild(form)
          form.submit()
          document.body.removeChild(form)
          
          this.$message.success(`${format.toUpperCase()}报表下载完成`)
        } catch (downloadError) {
          console.error('表单下载方法失败，尝试fetch方式:', downloadError)
          
          // 回退到fetch API下载方式
          try {
            const response = await fetch(url)
            
            if (!response.ok) {
              throw new Error(`下载失败: ${response.status} ${response.statusText}`)
            }
            
            const blob = await response.blob()
            const contentType = response.headers.get('content-type') || this.getContentType(format)
            
            // 创建下载链接
            const blobUrl = window.URL.createObjectURL(blob)
            const link = document.createElement('a')
            link.href = blobUrl
            link.download = `${report.title || '报表'}.${format}`
            document.body.appendChild(link)
            link.click()
            document.body.removeChild(link)
            window.URL.revokeObjectURL(blobUrl)
            
            this.$message.success(`${format.toUpperCase()}报表下载完成`)
          } catch (fetchError) {
            throw new Error(`无法下载报表: ${fetchError.message}`)
          }
        }
      } catch (error) {
        console.error('下载报表失败:', error)
        this.$message.error(`下载失败: ${error.message || '服务器错误'}`)
      }
    },
    
    getContentType(format) {
      const types = {
        'html': 'text/html',
        'pdf': 'application/pdf',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      }
      return types[format] || 'application/octet-stream'
    },
    
    shareReport(report) {
      this.shareInfo = {
        reportId: report.id,
        link: `${window.location.origin}/shared/reports/${report.id}`,
        expiry: '7d',
        permission: 'view'
      }
      this.showShareDialog = true
    },
    
    copyShareLink() {
      navigator.clipboard.writeText(this.shareInfo.link).then(() => {
        this.$message.success('分享链接已复制到剪贴板')
      })
    },
    
    updateShareSettings() {
      this.$message.success('分享设置已更新')
      this.showShareDialog = false
    },
    
    async deleteReportConfirm(report) {
      try {
        await this.$confirm(`确定要删除报表 "${report.title}" 吗？`, '删除确认', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await deleteReport(report.id)
        await this.loadReportsList()
        this.$message.success('报表删除成功')
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除报表失败:', error)
        }
      }
    },
    
    async generateComparison() {
      if (this.comparisonForm.reports.length < 2) {
        this.$message.warning('请至少选择2个报表进行对比')
        return
      }
      
      this.loading.comparison = true
      try {
        // 这里应该调用对比分析API
        await new Promise(resolve => setTimeout(resolve, 2000)) // 模拟API调用
        
        this.$message.success('对比报告生成成功')
        this.showComparisonDialog = false
        await this.loadReportsList()
      } catch (error) {
        console.error('生成对比报告失败:', error)
      } finally {
        this.loading.comparison = false
      }
    },
    
    getReportTypeName(type) {
      const names = {
        'data_analysis': '数据分析',
        'model_training': '模型训练',
        'performance_evaluation': '性能评估',
        'comprehensive': '综合分析',
        'custom': '自定义'
      }
      return names[type] || type
    },
    
    getReportTypeColor(type) {
      const colors = {
        'data_analysis': 'primary',
        'model_training': 'success',
        'performance_evaluation': 'warning',
        'comprehensive': 'danger',
        'custom': 'info'
      }
      return colors[type] || ''
    }
  }
}
</script>

<style scoped>
.reports {
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

.report-preview {
  max-height: 60vh;
  overflow-y: auto;
  padding: 20px;
  border: 1px solid #EBEEF5;
  border-radius: 4px;
  background: white;
}

.dialog-footer {
  text-align: right;
}
</style> 