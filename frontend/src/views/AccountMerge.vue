<template>
  <div class="merge-container">
    <el-card class="merge-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon :size="32" color="#409EFF"><Warning /></el-icon>
          <h2>账号合并确认</h2>
        </div>
      </template>

      <div class="merge-content">
        <el-alert
          title="检测到账号冲突"
          type="warning"
          :closable="false"
          show-icon
        >
          <p>您要绑定的{{ platformText }}已关联另一个账号，且两个账号都有数据记录。</p>
          <p>请选择如何处理：</p>
        </el-alert>

        <div class="options">
          <el-radio-group v-model="selectedAction" size="large">
            <el-radio label="merge" border>
              <div class="option-content">
                <el-icon><Promotion /></el-icon>
                <div class="option-text">
                  <div class="option-title">合并数据</div>
                  <div class="option-desc">将两个账号的所有数据合并到当前账号</div>
                </div>
              </div>
            </el-radio>

            <el-radio label="replace" border>
              <div class="option-content">
                <el-icon><Delete /></el-icon>
                <div class="option-text">
                  <div class="option-title">保留当前账号数据</div>
                  <div class="option-desc">删除另一个账号的所有数据，仅保留当前账号数据</div>
                </div>
              </div>
            </el-radio>
          </el-radio-group>
        </div>

        <el-alert
          title="重要提示"
          type="error"
          :closable="false"
          show-icon
          style="margin-top: 24px;"
        >
          此操作不可撤销，请谨慎选择！
        </el-alert>
      </div>

      <template #footer>
        <div class="footer-buttons">
          <el-button @click="handleCancel" size="large">取消</el-button>
          <el-button
            type="primary"
            @click="handleConfirm"
            :disabled="!selectedAction"
            :loading="submitting"
            size="large"
          >
            确认{{ selectedAction === 'merge' ? '合并' : '保留' }}
          </el-button>
        </div>
      </template>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Warning, Promotion, Delete } from '@element-plus/icons-vue'
import request from '@/utils/request'

const route = useRoute()
const router = useRouter()

const token = ref('')
const selectedAction = ref('')
const submitting = ref(false)

const platformText = computed(() => {
  // 可以从token中解析平台信息，暂时先用通用文本
  return 'QQ/微信'
})

onMounted(() => {
  token.value = route.query.token
  if (!token.value) {
    ElMessage.error('无效的绑定请求')
    router.push('/profile')
  }
})

const handleConfirm = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要${selectedAction.value === 'merge' ? '合并' : '保留当前账号'}数据吗？此操作不可撤销！`,
      '最终确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    submitting.value = true

    await request({
      url: '/api/v1/oauth/merge-account',
      method: 'post',
      data: {
        temp_bind_token: token.value,
        action: selectedAction.value
      }
    })

    ElMessage.success('账号合并成功')
    
    // 跳转回个人信息页面
    setTimeout(() => {
      router.push('/profile')
      // 刷新页面以更新用户信息
      window.location.reload()
    }, 1000)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('合并失败:', error)
      ElMessage.error(error.response?.data?.detail || '合并失败，请重试')
    }
  } finally {
    submitting.value = false
  }
}

const handleCancel = () => {
  router.push('/profile')
}
</script>

<style scoped>
.merge-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.merge-card {
  width: 100%;
  max-width: 600px;
  border-radius: 16px;
}

.merge-card :deep(.el-card__header) {
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.card-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #333;
}

.merge-content {
  padding: 24px 0;
}

.options {
  margin-top: 24px;
}

.options :deep(.el-radio-group) {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.options :deep(.el-radio.is-bordered) {
  width: 100%;
  height: auto;
  padding: 20px;
  border-radius: 12px;
  transition: all 0.3s;
}

.options :deep(.el-radio.is-bordered.is-checked) {
  border-color: #409EFF;
  background: #ecf5ff;
}

.option-content {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  width: 100%;
}

.option-content .el-icon {
  font-size: 28px;
  margin-top: 4px;
}

.option-text {
  flex: 1;
  text-align: left;
}

.option-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.option-desc {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
}

.footer-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
