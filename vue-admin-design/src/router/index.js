import Vue from 'vue'
import Router from 'vue-router'
// 移除Layout导入，因为不再需要布局
import { asyncRoutes } from './routes'

Vue.use(Router)

/**
 * hidden: true                  如果设置为 true，该项菜单将不会显示在菜单栏中(默认为 false)
 * meta : {
    title: 'title'               菜单名
    icon: 'icon-name'            图标名
    fixed: true                  如果设置为 true，该项 tag 将一直存在 tag 栏中(默认为 false)
  }
 * */

export const constantRoutes = [
  {
    path: '/401',
    name: '401',
    component: () => import('../views/error-page/401'),
    hidden: true,
    meta: { title: '401' }
  },
  {
    path: '/404',
    name: '404',
    component: () => import('../views/error-page/404'),
    hidden: true,
    meta: { title: '404' }
  },
  // 移除首页路由，改为重定向到第一个可用页面
  {
    path: '/',
    redirect: '/data-interface'
  }
]

const routes = [...constantRoutes, ...asyncRoutes]

export default new Router({
  routes
})

