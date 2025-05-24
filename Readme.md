# BS_Predict_v3 ---- Streamlit到Vue+Flask架构迁移

这是一个将基于Streamlit的机器学习预测系统迁移到Vue+Flask架构的项目。迁移后的系统保持了原有的功能和页面布局，同时提供了更好的扩展性和维护性。

## 项目结构

```
BS_Predict_v4/
├── streamlit_Predict/          # 原始Streamlit项目
│   ├── app.py                  # Streamlit主应用
│   ├── modules/                # 功能模块
│   ├── data/                   # 数据文件
│   └── requirements.txt        # 依赖配置
│
├── flask_backend/              # Flask后端 (新)
│   ├── app.py                  # Flask主应用
│   ├── modules/                # 服务模块
│   │   ├── data_processing.py  # 数据处理服务
│   │   ├── machine_learning.py # 机器学习服务
│   │   ├── stacking_ensemble.py# Stacking集成服务
│   │   ├── auto_ml.py          # AutoML服务
│   │   ├── visualization.py    # 可视化服务
│   │   └── report.py           # 报表服务
│   ├── data/                   # 数据文件夹
│   ├── models/                 # 模型存储
│   ├── reports/                # 报表存储
│   ├── uploads/                # 上传文件存储
│   └── requirements.txt        # 依赖配置
│
└── vue-admin-design/           # Vue前端 (新增页面)
    ├── src/
    │   ├── views/
    │   │   ├── ml-system/      # 机器学习子系统页面
    │   │   │   ├── DataInterface.vue
    │   │   │   ├── MachineLearning.vue
    │   │   │   ├── StackingEnsemble.vue
    │   │   │   └── AutoML.vue
    │   │   └── user-system/    # 用户交互子系统页面
    │   │       ├── Visualization.vue
    │   │       └── Reports.vue
    │   ├── api/
    │   │   └── mlApi.js        # API接口配置
    │   ├── router/
    │   │   └── routes.js       # 路由配置
    │   └── request.js          # HTTP请求配置
    └── package.json
```

## 系统架构

### 后端架构 (Flask)
- **模块化设计**: 每个功能模块独立成服务类
- **RESTful API**: 标准的REST接口设计
- **统一响应格式**: 一致的JSON响应结构
- **错误处理**: 完善的异常处理机制
- **文件管理**: 支持文件上传、下载、存储

### 前端架构 (Vue + Element UI)
- **组件化开发**: 可复用的Vue组件
- **响应式布局**: 适配不同屏幕尺寸
- **统一风格**: 基于Element UI的一致UI设计
- **状态管理**: 实时的系统状态监控
- **错误提示**: 用户友好的错误信息展示

## 功能模块

### 1. 机器学习子系统

#### 系统接口 (DataInterface.vue)
- **数据加载**: 支持默认数据和自定义数据上传
- **数据预览**: 实时数据预览和统计信息
- **数据预处理**: 缺失值填充、特征标准化、异常值处理
- **数据下载**: 支持CSV和Excel格式下载
- **系统状态**: 实时监控数据加载和模型训练状态

#### 机器学习 (MachineLearning.vue)
- **多模型支持**: LR、RF、GBR、XGBR、SVR、ANN等模型
- **参数配置**: 可视化的模型参数设置
- **训练过程**: 实时训练进度和结果展示
- **模型评估**: 详细的性能指标和可视化

#### Stacking集成 (StackingEnsemble.vue)
- **基模型选择**: 灵活的基学习器配置
- **元模型设置**: 多种元学习器选项
- **交叉验证**: k折交叉验证支持
- **集成效果**: 可视化的集成学习效果

#### 自动化机器学习 (AutoML.vue)
- **模型自动筛选**: 自动尝试多种模型
- **超参数优化**: 网格搜索和随机搜索
- **性能比较**: 自动模型性能比较报告
- **最优模型**: 自动选择最佳模型

### 2. 用户交互子系统

#### 可视化分析 (Visualization.vue)
- **数据可视化**: 分布图、相关性矩阵、散点图等
- **模型可视化**: 预测图、残差图、特征重要性等
- **交互式图表**: 基于Plotly的动态图表
- **多种格式**: 支持Plotly和Matplotlib两种图表

#### 报表 (Reports.vue)
- **报表生成**: 自动生成分析报告
- **多种格式**: 支持HTML、PDF、DOCX格式
- **自定义内容**: 可配置的报表内容
- **报表管理**: 报表历史和下载管理

## 安装与运行

### 环境要求
- Python 3.8+
- Node.js 14+
- npm 或 yarn

### 后端启动
```bash
cd flask_backend
pip install -r requirements.txt
python app.py
```
后端将在 http://localhost:5000 启动

### 前端启动
```bash
cd vue-admin-design
npm install
npm run serve
```
前端将在 http://localhost:8080 启动

## API接口文档

### 系统状态
- `GET /api/system/status` - 获取系统状态

### 数据处理
- `POST /api/data/load-default` - 加载默认数据
- `POST /api/data/upload` - 上传数据文件
- `GET /api/data/preview` - 获取数据预览
- `POST /api/data/preprocess` - 数据预处理
- `GET /api/data/download/{type}/{format}` - 下载数据

### 机器学习
- `GET /api/ml/models` - 获取可用模型
- `POST /api/ml/train` - 训练模型
- `POST /api/ml/predict` - 模型预测
- `POST /api/ml/evaluate` - 模型评估

### Stacking集成
- `POST /api/stacking/train` - 训练Stacking模型

### AutoML
- `POST /api/automl/run` - 运行AutoML

### 可视化
- `POST /api/visualization/data` - 生成数据可视化
- `POST /api/visualization/model` - 生成模型可视化

### 报表
- `POST /api/reports/generate` - 生成报表
- `GET /api/reports/download/{id}/{format}` - 下载报表

## 主要特性

### 1. 完整功能迁移
- ✅ 保持原有Streamlit项目的所有功能
- ✅ 相同的页面布局和用户体验
- ✅ 完整的数据处理流程
- ✅ 所有机器学习模型支持

### 2. 架构优化
- ✅ 前后端分离架构
- ✅ RESTful API设计
- ✅ 模块化代码结构
- ✅ 统一错误处理

### 3. 用户体验提升
- ✅ 响应式页面设计
- ✅ 实时状态更新
- ✅ 友好的错误提示
- ✅ 流畅的交互体验

### 4. 可维护性
- ✅ 清晰的代码结构
- ✅ 详细的注释文档
- ✅ 标准的代码规范
- ✅ 便于扩展的架构

### 5. 数据安全
- ✅ 文件上传验证
- ✅ 错误信息过滤
- ✅ 安全的文件存储
- ✅ 请求参数验证

## 技术栈

### 后端
- **Flask**: Python Web框架
- **pandas**: 数据处理
- **scikit-learn**: 机器学习
- **XGBoost**: 梯度提升算法
- **matplotlib/seaborn**: 数据可视化
- **plotly**: 交互式图表
- **reportlab**: PDF报表生成

### 前端
- **Vue.js 2**: JavaScript框架
- **Element UI**: UI组件库
- **axios**: HTTP客户端
- **Vue Router**: 路由管理
- **ECharts**: 图表库

## 部署建议

### 开发环境
- 后端: Flask开发服务器
- 前端: Vue CLI开发服务器
- 数据库: 文件系统存储

### 生产环境
- 后端: Gunicorn + Nginx
- 前端: Nginx静态文件服务
- 数据库: PostgreSQL/MySQL
- 缓存: Redis
- 容器化: Docker

## 扩展方向

1. **用户认证**: 添加用户登录和权限管理
2. **数据库集成**: 使用数据库存储模型和结果
3. **分布式训练**: 支持大规模数据的分布式训练
4. **实时监控**: 添加系统监控和日志记录
5. **API文档**: 集成Swagger API文档
6. **单元测试**: 添加完整的测试覆盖

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交代码更改
4. 推送到分支
5. 创建Pull Request

## 许可证

本项目采用MIT许可证，详情请参阅LICENSE文件。
