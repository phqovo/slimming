<template>
  <div class="settings-container">
    <el-card class="settings-card" shadow="never">
      <template #header>
        <h3>个人设置</h3>
      </template>

      <el-form :model="settings" label-width="120px">
        <el-form-item label="体重单位">
          <el-radio-group v-model="settings.weight_unit" @change="handleSave">
            <el-radio label="kg">千克 (kg)</el-radio>
            <el-radio label="jin">斤</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="数据公开">
          <div class="switch-wrapper">
            <el-switch 
              v-model="settings.data_public" 
              @change="handleDataPublicChange"
              active-text="开启" 
              inactive-text="关闭"
            />
            <span class="setting-tip">
              <el-icon style="margin-right: 4px;"><InfoFilled /></el-icon>
              开启后其他小伙伴能看到你的减肥数据
            </span>
          </div>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { ElMessage } from 'element-plus'
import { InfoFilled } from '@element-plus/icons-vue'

const settingsStore = useSettingsStore()

const settings = ref({
  weight_unit: 'kg',
  data_public: false
})

onMounted(async () => {
  await settingsStore.loadSettings()
  settings.value.weight_unit = settingsStore.weightUnit
  settings.value.data_public = settingsStore.settings.data_public || false
})

const handleSave = async () => {
  const success = await settingsStore.saveSettings({
    weight_unit: settings.value.weight_unit
  })
  
  if (success) {
    ElMessage.success('设置已保存')
    // 刷新页面以应用新设置
    setTimeout(() => {
      window.location.reload()
    }, 500)
  } else {
    ElMessage.error('保存失败')
  }
}

const handleDataPublicChange = async () => {
  try {
    await settingsStore.saveSettings({
      data_public: settings.value.data_public
    })
    ElMessage.success(settings.value.data_public ? '已开启数据公开' : '已关闭数据公开')
  } catch (error) {
    ElMessage.error('设置失败')
    // 回滚设置
    settings.value.data_public = !settings.value.data_public
  }
}
</script>

<style scoped>
.settings-container {
  max-width: 800px;
}

.settings-card h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.switch-wrapper {
  display: flex;
  align-items: center;
  gap: 15px;
}

.setting-tip {
  font-size: 12px;
  color: #999;
  display: flex;
  align-items: center;
}
</style>
