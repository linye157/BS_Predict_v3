'use strict'

const name = '智能轧钢力学性能预测与优化系统' // 网页标题title
const port = 8000 // 端口号

module.exports = {
  publicPath: './', // 部署应用包时的基本 url
  outputDir: 'dist', // build 构建文件目录
  assetsDir: 'static', // 静态资源目录
  lintOnSave: process.env.NODE_ENV === 'development', // 仅在开发模式下进行 eslint 检测代码
  productionSourceMap: false, // 禁用生产环境的 source map
  runtimeCompiler: true, // 是否运行时组件中使用 template
  configureWebpack: {
    name: name // 配置网页title 名称
  },
  devServer: {
    host: '0.0.0.0', // 默认是 localhost,可不配置
    port: port, // 配置端口号
    open: true, // 启动是否打开浏览器
    overlay: { // 是否在浏览器上显示编译的 errors 或 warnings
      warnings: false,
      errors: true
    },
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000', // 使用127.0.0.1而不是localhost
        changeOrigin: true,
        secure: false,
        ws: true, // 支持websocket
        timeout: 300000, // 延长超时时间到5分钟
        pathRewrite: null, // 不进行路径重写
        onProxyReq: function(proxyReq, req, res) {
          // 打印请求详情以便调试
          console.log('>>>>>>>>>> 代理请求:', req.method, req.url);
          if (req.method === 'POST') {
            // 确保内容类型设置正确
            proxyReq.setHeader('Content-Type', 'application/json');
            proxyReq.setHeader('Accept', 'application/json');
          }
        },
        onProxyRes: function(proxyRes, req, res) {
          // 打印响应状态以便调试
          console.log('<<<<<<<<<< 代理响应:', proxyRes.statusCode, req.url);
          
          // 确保跨域头被正确设置
          proxyRes.headers['Access-Control-Allow-Origin'] = '*';
          proxyRes.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept';
          proxyRes.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS';
        },
        onError: function(err, req, res) {
          // 代理错误处理
          console.error('代理错误:', err);
          res.writeHead(500, {
            'Content-Type': 'application/json'
          });
          res.end(JSON.stringify({
            success: false,
            message: '代理服务器错误: ' + err.message
          }));
        }
      }
    }
  }
}
