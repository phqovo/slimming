<template>
  <div class="login-success-container">
    <div class="success-card">
      <div class="loading-icon">
        <el-icon :size="60" color="#67c23a">
          <Loading />
        </el-icon>
      </div>
      <h2>登录成功</h2>
      <p>正在跳转...</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useSettingsStore } from '@/stores/settings'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const settingsStore = useSettingsStore()

onMounted(async () => {
  console.log('=== LoginSuccess 页面加载 ===')
  console.log('window.location.href:', window.location.href)
  console.log('window.location.search:', window.location.search)
  console.log('route.query:', route.query)
  
  try {
    // 从URL参数中获取token
    const token = route.query.token
    
    console.log('🚀 LoginSuccess 处理开始:', { 
      token: token ? token.substring(0, 50) + '...' : null,
      tokenLength: token ? token.length : 0
    })
    
    if (!token) {
      console.error('❌ 未获取到token')
      ElMessage.error('登录失败：未获取到token')
      router.push('/login')
      return
    }
    
    // 保存token
    localStorage.setItem('token', token)
    userStore.token = token
    console.log('✅ Token保存成功:', token.substring(0, 20) + '...')
    
    // 获取用户信息
    console.log('👤 获取用户信息...')
    await userStore.fetchUserInfo()
    console.log('✅ 用户信息获取成功:', userStore.userInfo)
    
    // 加载设置
    console.log('⚙️ 加载设置...')
    await settingsStore.reloadSettings()
    console.log('✅ 设置加载成功')
    
    ElMessage.success('登录成功')
    
    // 关闭当前窗口（如果是弹窗）
    if (window.opener) {
      console.log('💬 关闭弹窗并通知父窗口')
      window.close()
      // 通知父窗口刷新
      window.opener.postMessage({ type: 'oauth_login_success' }, '*')
    } else {
      // 跳转到首页
      console.log('🏠 跳转到首页')
      router.push('/')
    }
  } catch (error) {
    console.error('❌ 处理登录失败:', error)
    ElMessage.error('登录失败，请重试')
    router.push('/login')
  }
})
</script>

<style scoped>
.login-success-container {
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.success-card {
  padding: 60px 80px;
  background: white;
  border-radius: 16px;
  text-align: center;
}

.loading-icon {
  margin-bottom: 24px;
  animation: rotate 2s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.success-card h2 {
  font-size: 24px;
  color: #333;
  margin-bottom: 12px;
}

.success-card p {
  font-size: 14px;
  color: #999;
}
</style>
