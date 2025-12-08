import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getUserSettings, updateUserSettings } from '@/api/settings'

export const useSettingsStore = defineStore('settings', () => {
  const weightUnit = ref('kg') // 体重单位：kg 或 jin
  const isLoaded = ref(false) // 设置是否已加载
  const settings = ref(null) // 存储完整的设置信息

  // 加载用户设置
  const loadSettings = async () => {
    if (isLoaded.value) return // 已加载过就不重复加载
    
    try {
      const result = await getUserSettings()
      settings.value = result // 存储完整设置
      weightUnit.value = result.weight_unit || 'kg'
      isLoaded.value = true
    } catch (error) {
      console.error('加载设置失败:', error)
      weightUnit.value = 'kg' // 使用默认值
      isLoaded.value = true
    }
  }

  // 重新加载用户设置（用于重新登录或刷新）
  const reloadSettings = async () => {
    isLoaded.value = false // 重置加载状态
    return loadSettings()
  }

  // 保存用户设置
  const saveSettings = async (settings) => {
    try {
      const result = await updateUserSettings(settings)
      weightUnit.value = result.weight_unit
      return true
    } catch (error) {
      console.error('保存设置失败:', error)
      return false
    }
  }

  // 体重转换：数据库 kg -> 显示单位
  const convertWeightToDisplay = (kgValue) => {
    if (!kgValue) return 0
    return weightUnit.value === 'jin' ? (kgValue * 2).toFixed(1) : kgValue.toFixed(1)
  }

  // 体重转换：显示单位 -> 数据库 kg
  const convertWeightToKg = (displayValue) => {
    if (!displayValue) return 0
    return weightUnit.value === 'jin' ? displayValue / 2 : displayValue
  }

  // 获取体重单位文本
  const getWeightUnitText = () => {
    return weightUnit.value === 'jin' ? '斤' : 'kg'
  }

  return {
    weightUnit,
    isLoaded,
    settings,  // 导出完整设置
    loadSettings,
    reloadSettings,
    saveSettings,
    convertWeightToDisplay,
    convertWeightToKg,
    getWeightUnitText
  }
})
