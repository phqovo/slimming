import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login, getCurrentUser } from '@/api/user'
import { useSettingsStore } from '@/stores/settings'
import router from '@/router'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(null)

  // 登录
  const handleLogin = async (phone, code) => {
    const res = await login(phone, code)
    token.value = res.token
    userInfo.value = res.user
    localStorage.setItem('token', res.token)
    return res
  }

  // 退出登录
  const handleLogout = () => {
    const settingsStore = useSettingsStore()
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    // 重置设置业态，以便下次登录上次加载
    settingsStore.reloadSettings()
    router.push('/login')
  }

  // 获取用户信息
  const fetchUserInfo = async () => {
    try {
      const res = await getCurrentUser()
      userInfo.value = res
      return res
    } catch (error) {
      handleLogout()
      throw error
    }
  }

  // 更新用户信息
  const setUserInfo = (info) => {
    userInfo.value = { ...userInfo.value, ...info }
  }

  return {
    token,
    userInfo,
    handleLogin,
    handleLogout,
    fetchUserInfo,
    setUserInfo
  }
})
