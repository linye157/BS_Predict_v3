import router from './index'

// 移除登录认证，允许直接访问所有页面
router.beforeEach((to, from, next) => {
  next()
})
