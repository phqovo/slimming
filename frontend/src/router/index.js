import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory('/health/'),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/login-success',
      name: 'LoginSuccess',
      component: () => import('@/views/LoginSuccess.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/account-merge',
      name: 'AccountMerge',
      component: () => import('@/views/AccountMerge.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      component: () => import('@/views/Layout.vue'),
      redirect: '/home',
      meta: { requiresAuth: true },
      children: [
        {
          path: '/home',
          name: 'Home',
          component: () => import('@/views/Home.vue'),
          meta: { title: '首页' }
        },
        {
          path: '/trend',
          name: 'Trend',
          component: () => import('@/views/Trend.vue'),
          meta: { title: '体重趋势' }
        },
        {
          path: '/profile',
          name: 'Profile',
          component: () => import('@/views/Profile.vue'),
          meta: { title: '个人信息' }
        },
        {
          path: '/settings',
          name: 'Settings',
          component: () => import('@/views/Settings.vue'),
          meta: { title: '设置' }
        },
        {
          path: '/history',
          name: 'History',
          component: () => import('@/views/History.vue'),
          meta: { title: '历史记录' }
        },
        {
          path: '/food-library',
          name: 'FoodLibrary',
          component: () => import('@/views/FoodLibrary.vue'),
          meta: { title: '食物热量库' }
        },
        {
          path: '/local-food-library',
          name: 'LocalFoodLibrary',
          component: () => import('@/views/LocalFoodLibrary.vue'),
          meta: { title: '本地食物库' }
        },
        {
          path: '/nutrition-analysis',
          name: 'NutritionAnalysis',
          component: () => import('@/views/NutritionAnalysis.vue'),
          meta: { title: '成分分析' }
        },
        {
          path: '/body-composition',
          name: 'BodyCompositionReport',
          component: () => import('@/views/BodyCompositionReport.vue'),
          meta: { title: '人体成分报告' }
        },
        {
          path: '/ai',
          name: 'AI',
          component: () => import('@/views/AI.vue'),
          meta: { title: 'AI 助手' }
        },
        {
          path: '/leaderboard',
          name: 'Leaderboard',
          component: () => import('@/views/Leaderboard.vue'),
          meta: { title: '减肥榜' }
        },
        {
          path: '/auth-management',
          name: 'AuthManagement',
          component: () => import('@/views/AuthManagement.vue'),
          meta: { title: '授权管理' }
        },
        {
          path: '/external-data',
          name: 'ExternalData',
          component: () => import('@/views/ExternalData.vue'),
          meta: { title: '三方数据查询' }
        },
        {
          path: '/data-sync-config',
          name: 'DataSyncConfig',
          component: () => import('@/views/DataSyncConfig.vue'),
          meta: { title: '数据拉取配置' }
        }
      ]
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  console.log('=== 路由守卫 ===')
  console.log('跳转到:', to.path)
  console.log('来自:', from.path)
  console.log('requiresAuth:', to.meta.requiresAuth)
  console.log('localStorage token:', token ? token.substring(0, 20) + '...' : 'null')
  
  if (to.meta.requiresAuth !== false && !token) {
    console.log('❌ 需要登录但没有token，跳转到登录页')
    next('/login')
  } else if (to.path === '/login' && token) {
    console.log('✅ 已登录，跳转到首页')
    next('/')
  } else {
    console.log('✅ 放行')
    next()
  }
})

export default router
