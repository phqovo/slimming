<template>
  <div class="profile-page">
    <van-nav-bar title="我的" />
    
    <!-- 用户信息卡片 -->
    <div class="user-card">
      <van-image
        round
        width="60"
        height="60"
        :src="userInfo?.avatar || 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg'"
      />
      <div class="user-info">
        <div class="nickname">{{ userInfo?.nickname || '用户' }}</div>
        <div class="phone">{{ userInfo?.phone }}</div>
      </div>
    </div>

    <!-- 目标设置 -->
    <van-cell-group inset class="section">
      <van-cell title="目标体重" :value="`${targetWeight || '--'} kg`" is-link @click="showWeightPicker = true" />
      <van-cell title="体重单位" :value="weightUnit === 'kg' ? '公斤' : '斤'" is-link @click="showUnitPicker = true" />
    </van-cell-group>

    <!-- 功能菜单 -->
    <van-cell-group inset class="section">
      <van-cell title="我的减肥榜排名" is-link @click="$router.push('/leaderboard')" />
      <van-cell title="食物库" icon="food-o" is-link @click="$router.push('/food-library')" />
      <van-cell title="数据同步" icon="sync" is-link @click="$router.push('/data-sync')" />
    </van-cell-group>

    <!-- 其他 -->
    <van-cell-group inset class="section">
      <van-cell title="关于我们" is-link />
      <van-cell title="退出登录" @click="handleLogout" />
    </van-cell-group>

    <!-- 目标体重选择器 -->
    <van-popup v-model:show="showWeightPicker" position="bottom">
      <van-picker
        :columns="weightColumns"
        @confirm="onWeightConfirm"
        @cancel="showWeightPicker = false"
      />
    </van-popup>

    <!-- 单位选择器 -->
    <van-popup v-model:show="showUnitPicker" position="bottom">
      <van-picker
        :columns="unitColumns"
        @confirm="onUnitConfirm"
        @cancel="showUnitPicker = false"
      />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showConfirmDialog } from 'vant'
import { getUserProfile, updateUserProfile } from '@/api/user'
import { useSettingsStore } from '@/stores/settings'

const router = useRouter()
const settingsStore = useSettingsStore()
const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || '{}'))
const targetWeight = ref(null)
const weightUnit = ref(settingsStore.weightUnit || 'kg')
const showWeightPicker = ref(false)
const showUnitPicker = ref(false)

// 体重选项（30-150kg）
const weightColumns = ref(
  Array.from({ length: 121 }, (_, i) => ({
    text: `${30 + i} kg`,
    value: 30 + i
  }))
)

// 单位选项
const unitColumns = [
  { text: '公斤(kg)', value: 'kg' },
  { text: '斤', value: 'jin' }
]

// 获取用户信息
const fetchUserProfile = async () => {
  try {
    const res = await getUserProfile()
    targetWeight.value = res.target_weight
  } catch (error) {
    console.error('获取失败', error)
  }
}

// 确认选择目标体重
const onWeightConfirm = async ({ selectedValues }) => {
  try {
    await updateUserProfile({ target_weight: selectedValues[0] })
    targetWeight.value = selectedValues[0]
    showToast('设置成功')
  } catch (error) {
    showToast('设置失败')
  }
  showWeightPicker.value = false
}

// 确认选择单位
const onUnitConfirm = ({ selectedValues }) => {
  settingsStore.setWeightUnit(selectedValues[0])
  weightUnit.value = selectedValues[0]
  showToast('设置成功')
  showUnitPicker.value = false
}

// 退出登录
const handleLogout = async () => {
  try {
    await showConfirmDialog({
      title: '提示',
      message: '确定要退出登录吗？'
    })
    localStorage.clear()
    router.replace('/login')
  } catch {
    // 取消
  }
}

onMounted(() => {
  fetchUserProfile()
})
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: #f7f8fa;
  padding-bottom: 20px;
}

.user-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 30px 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  color: white;
}

.user-info {
  flex: 1;
}

.nickname {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 6px;
}

.phone {
  font-size: 13px;
  opacity: 0.9;
}

.section {
  margin-top: 12px;
}
</style>
