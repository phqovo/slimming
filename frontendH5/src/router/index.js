import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/views/Layout.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/',
    component: Layout,
    redirect: '/home',
    children: [
      {
        path: '/home',
        name: 'Home',
        component: () => import('@/views/Home.vue'),
        meta: { title: '首页', icon: 'home-o' }
      },
      {
        path: '/record',
        name: 'Record',
        component: () => import('@/views/Record.vue'),
        meta: { title: '记录', icon: 'records' }
      },
      {
        path: '/trend',
        name: 'Trend',
        component: () => import('@/views/Trend.vue'),
        meta: { title: '趋势', icon: 'chart-trending-o' }
      },
      {
        path: '/profile',
        name: 'Profile',
        component: () => import('@/views/Profile.vue'),
        meta: { title: '我的', icon: 'user-o' }
      }
    ]
  },
  {
    path: '/diet/add',
    name: 'AddDiet',
    component: () => import('@/views/diet/AddDiet.vue'),
    meta: { title: '添加饮食' }
  },
  {
    path: '/exercise/add',
    name: 'AddExercise',
    component: () => import('@/views/exercise/AddExercise.vue'),
    meta: { title: '添加运动' }
  },
  {
    path: '/weight/add',
    name: 'AddWeight',
    component: () => import('@/views/weight/AddWeight.vue'),
    meta: { title: '记录体重' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  if (to.path !== '/login' && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/home')
  } else {
    next()
  }
})

export default router
