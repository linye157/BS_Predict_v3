/**
 * hidden: true                  如果设置为 true，该项菜单将不会显示在菜单栏中(默认为 false)
 * meta : {
    title: 'title'               菜单名
    icon: 'icon-name'            图标名
    fixed: true                  如果设置为 true，该项 tag 将一直存在 tag 栏中(默认为 false)
  }
 * */

// 移除Layout导入，因为页面现在直接访问
// import Layout from '../layout'

export const asyncRoutes = [
  // 机器学习子系统页面 - 直接路由访问
  {
    path: '/data-interface',
    name: 'DataInterface',
    component: () => import('../views/ml-system/DataInterface'),
    meta: {
      title: '系统接口',
      icon: 'vue-dsn-icon-database'
    }
  },
  {
    path: '/machine-learning',
    name: 'MachineLearning',
    component: () => import('../views/ml-system/MachineLearning'),
    meta: {
      title: '机器学习',
      icon: 'vue-dsn-icon-cpu'
    }
  },
  {
    path: '/stacking-ensemble',
    name: 'StackingEnsemble',
    component: () => import('../views/ml-system/StackingEnsemble'),
    meta: {
      title: '机器学习Stacking集成',
      icon: 'vue-dsn-icon-layer'
    }
  },
  {
    path: '/auto-ml',
    name: 'AutoML',
    component: () => import('../views/ml-system/AutoML'),
    meta: {
      title: '自动化机器学习',
      icon: 'vue-dsn-icon-magic'
    }
  },
  // 用户交互子系统页面 - 直接路由访问
  {
    path: '/visualization',
    name: 'Visualization',
    component: () => import('../views/user-system/Visualization'),
    meta: {
      title: '可视化分析',
      icon: 'vue-dsn-icon-chart'
    }
  },
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('../views/user-system/Reports'),
    meta: {
      title: '报表',
      icon: 'vue-dsn-icon-document'
    }
  }
]
