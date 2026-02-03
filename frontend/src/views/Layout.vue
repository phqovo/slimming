<template>
  <div class="layout-container">
    <el-container>
      <!-- 顶部导航栏 -->
      <el-header class="layout-header">
        <div class="header-content">
          <div class="header-left">
            <h2>体重管理平台</h2>
          </div>
          
          <div class="header-center" v-if="encouragementMessage">
            <el-icon class="trophy-icon-small"><Trophy /></el-icon>
            <span class="encouragement-text-small">{{ encouragementMessage }}</span>
          </div>

          <div class="header-right">
            <el-dropdown @command="handleCommand">
              <div class="user-info">
                <el-avatar :src="userStore.userInfo?.avatar || '/default-avatar.png'" />
                <span class="username">{{ userStore.userInfo?.nickname || '用户' }}</span>
                <el-icon><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                  <el-dropdown-item command="settings">设置</el-dropdown-item>
                  <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>

      <el-container>
        <!-- 侧边栏 -->
        <el-aside width="220px" class="layout-aside">
          <el-menu
            :default-active="currentRoute"
            router
            class="aside-menu"
          >
            <el-menu-item index="/home">
              <el-icon><House /></el-icon>
              <span>首页</span>
            </el-menu-item>
            <el-menu-item index="/trend">
              <el-icon><TrendCharts /></el-icon>
              <span>体重趋势</span>
            </el-menu-item>
            <el-menu-item index="/history">
              <el-icon><DocumentCopy /></el-icon>
              <span>历史记录</span>
            </el-menu-item>
            <el-menu-item index="/food-library">
              <el-icon><Food /></el-icon>
              <span>食物热量库</span>
            </el-menu-item>
            <el-menu-item index="/local-food-library">
              <el-icon><Notebook /></el-icon>
              <span>本地食物库</span>
            </el-menu-item>
            <el-menu-item index="/nutrition-analysis">
              <el-icon><PieChart /></el-icon>
              <span>成分分析</span>
            </el-menu-item>
            <el-menu-item index="/body-composition">
              <el-icon><User /></el-icon>
              <span>人体成分报告</span>
            </el-menu-item>
            <el-menu-item index="/ai">
              <el-icon><ChatDotRound /></el-icon>
              <span>AI 助手</span>
            </el-menu-item>
            <el-menu-item index="/leaderboard">
              <el-icon><TrophyBase /></el-icon>
              <span>减肥榜</span>
            </el-menu-item>
            <el-menu-item index="/profile">
              <el-icon><User /></el-icon>
              <span>个人信息</span>
            </el-menu-item>
            <el-menu-item index="/auth-management">
              <el-icon><Lock /></el-icon>
              <span>授权管理</span>
            </el-menu-item>
            <el-menu-item index="/external-data">
              <el-icon><DataAnalysis /></el-icon>
              <span>三方数据查询</span>
            </el-menu-item>
            <el-menu-item index="/data-sync-config">
              <el-icon><Setting /></el-icon>
              <span>数据拉取配置</span>
            </el-menu-item>
          </el-menu>
        </el-aside>

        <!-- 主内容区 -->
        <el-main class="layout-main">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useSettingsStore } from '@/stores/settings'
import { ElMessage, ElMessageBox } from 'element-plus'
import { House, TrendCharts, User, DocumentCopy, ArrowDown, Food, Notebook, PieChart, ChatDotRound, TrophyBase, Lock, DataAnalysis, Setting, Tools, Trophy } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const settingsStore = useSettingsStore()

const currentRoute = computed(() => route.path)

// 激励信息
const encouragementMessage = computed(() => {
  const progress = userStore.weightProgress
  if (!progress || progress.weight_lost === null || progress.weight_lost === undefined) {
    return ''
  }
  
  const weightLost = progress.weight_lost
  const weightToGoal = progress.weight_to_goal
  const daysElapsed = progress.days_elapsed || 0
  
  // 转换为显示单位
  const displayWeightLost = settingsStore.convertWeightToDisplay(Math.abs(weightLost))
  const displayWeightToGoal = weightToGoal ? settingsStore.convertWeightToDisplay(Math.abs(weightToGoal)) : 0
  const unit = settingsStore.getWeightUnitText()
  
  if (weightLost > 0) {
    // 减重成功
    if (weightToGoal && weightToGoal <= 0) {
      return `🎉 太棒啦！你已经达成目标，成功减去 ${displayWeightLost} ${unit}，耗时 ${daysElapsed} 天！`
    } else if (weightToGoal) {
      return `👏 太棒啦！你已经减去 ${displayWeightLost} ${unit}，耗时 ${daysElapsed} 天，距离目标还有 ${displayWeightToGoal} ${unit}！`
    } else {
      return `💪 加油！你已经减去 ${displayWeightLost} ${unit}，耗时 ${daysElapsed} 天，继续加油！`
    }
  } else if (weightLost < 0) {
    return `⚠️ 注意！相比最初体重增加了 ${displayWeightLost} ${unit}，别气馁，从现在开始努力！`
  } else {
    if (daysElapsed > 7) {
      return `🤔 体重 ${daysElapsed} 天没有变化，试试调整饮食和运动计划吧！`
    } else {
      return `👍 保持当前状态，坚持就是胜利！`
    }
  }
})

onMounted(async () => {
  // 获取用户信息
  if (!userStore.userInfo) {
    try {
      await userStore.fetchUserInfo()
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  }
  
  // 加载用户设置
  await settingsStore.loadSettings()
  
  // 加载体重进度
  userStore.fetchWeightProgress()
})

const handleCommand = (command) => {
  if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'settings') {
    router.push('/settings')
  } else if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      userStore.handleLogout()
      ElMessage.success('已退出登录')
    }).catch(() => {})
  }
}
</script>

<style scoped>
.layout-container {
  width: 100%;
  height: 100vh;
}

.el-container {
  height: 100%;
}

.layout-header {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 0;
  z-index: 100;
}

.header-content {
  height: 100%;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left h2 {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  transition: background 0.2s;
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
  padding: 6px 16px;
  border-radius: 20px;
  margin: 0 24px;
  max-width: 600px;
}

.trophy-icon-small {
  color: #ff9800;
  font-size: 18px;
}

.encouragement-text-small {
  font-size: 15px;
  color: #5e35b1;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-info:hover {
  background: #f5f7fa;
}

.username {
  font-size: 14px;
  color: #333;
}

.layout-aside {
  background: white;
  border-right: 1px solid #e4e7ed;
  padding: 16px 0;
}

.aside-menu {
  border: none;
}

.layout-main {
  background: #f5f7fa;
  padding: 24px;
  overflow-y: auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}

.fade-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}
</style>
