# API 配置说明

## 概述

本项目使用集中式配置管理后端API地址，避免在代码中硬编码URL，便于部署和维护。

## 配置文件

主配置文件：`src/config/api.js`

## 修改后端地址

当需要修改后端服务器地址时，只需要修改 `src/config/api.js` 文件中的 `API_BASE_URL` 常量：

```javascript
// 修改这个地址即可
export const API_BASE_URL = 'http://你的后端地址:端口'
```

例如：
- 本地开发：`http://localhost:5000`
- 测试环境：`http://192.168.1.100:5000`
- 生产环境：`http://your-domain.com:5000`

## 使用方式

### 1. 引入配置

```javascript
import { API_BASE_URL, API_CONFIG, getApiUrl } from '@/config/api'
```

### 2. 使用基础URL

```javascript
// 直接使用基础URL
const baseURL = API_BASE_URL

// 使用配置对象
const config = {
  baseURL: API_CONFIG.baseURL,
  timeout: API_CONFIG.timeout.default
}
```

### 3. 构建完整URL

```javascript
// 使用便捷方法构建URL
const healthUrl = getApiUrl(API_CONFIG.endpoints.health)
const statusUrl = getApiUrl(API_CONFIG.endpoints.system.status)
```

### 4. 超时配置

项目中预定义了不同类型操作的超时时间：

```javascript
API_CONFIG.timeout.default    // 60秒 - 默认操作
API_CONFIG.timeout.upload     // 120秒 - 文件上传
API_CONFIG.timeout.training   // 600秒 - 模型训练
API_CONFIG.timeout.automl     // 600秒 - AutoML
```

## 已更新的文件

以下文件已经更新为使用配置文件：

1. `src/utils/apiCheck.js` - API健康检查工具
2. `src/api/mlApi.js` - 机器学习API接口
3. `src/request.js` - Axios请求配置
4. `src/components/ServerStatus.vue` - 服务器状态组件
5. `src/views/ml-system/DataInterface.vue` - 数据接口页面

## 注意事项

1. 修改 `API_BASE_URL` 后需要重新启动开发服务器
2. 确保新的后端地址格式正确（包含协议、域名/IP和端口）
3. 如果使用HTTPS，记得将协议改为 `https://`
4. 生产环境部署时，建议使用环境变量来管理不同环境的配置 