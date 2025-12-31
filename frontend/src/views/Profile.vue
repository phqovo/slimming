<template>
  <div class="profile-container">
    <el-row :gutter="24">
      <!-- 个人信息卡片 -->
      <el-col :span="8">
        <el-card class="rounded-card profile-card" shadow="never">
          <div class="avatar-section">
            <el-upload
              :auto-upload="true"
              :show-file-list="false"
              :on-success="handleAvatarSuccess"
              :before-upload="beforeAvatarUpload"
              action="/health/api/v1/user/upload-avatar"
              :headers="{ Authorization: `Bearer ${token}` }"
            >
              <el-avatar :src="userInfo.avatar || '/default-avatar.png'" :size="120" />
              <div class="avatar-overlay">
                <el-icon><Camera /></el-icon>
                <span>更换头像</span>
              </div>
            </el-upload>
          </div>

          <div class="user-name">{{ userInfo.nickname || '未设置昵称' }}</div>
          <div class="user-phone">{{ userInfo.phone || '未绑定手机' }}</div>

          <div class="quick-stats">
            <div class="quick-stat-item">
              <div class="stat-label">身高</div>
              <div class="stat-value">{{ userInfo.height ? userInfo.height + ' cm' : '--' }}</div>
            </div>
            <div class="quick-stat-item">
              <div class="stat-label">年龄</div>
              <div class="stat-value">{{ userInfo.age ? userInfo.age + ' 岁' : '--' }}</div>
            </div>
            <div class="quick-stat-item">
              <div class="stat-label">性别</div>
              <div class="stat-value">{{ genderText }}</div>
            </div>
          </div>
        </el-card>

        <!-- 账号绑定卡片 -->
        <el-card class="rounded-card account-bind-card" shadow="never" style="margin-top: 24px;">
          <template #header>
            <h3>账号绑定</h3>
          </template>

          <div class="bind-items">
            <!-- 手机号 -->
            <div class="bind-item">
              <div class="bind-info">
                <el-icon :size="20" color="#409EFF"><Iphone /></el-icon>
                <div class="bind-text">
                  <div class="bind-label">手机号</div>
                  <div class="bind-value">{{ userInfo.phone || '未绑定' }}</div>
                </div>
              </div>
              <el-button 
                v-if="userInfo.phone" 
                type="danger" 
                size="small" 
                text
                @click="handleUnbind('phone')"
                :disabled="!canUnbind('phone')"
              >
                解绑
              </el-button>
              <el-button 
                v-else 
                type="primary" 
                size="small"
                @click="handleBind('phone')"
              >
                绑定
              </el-button>
            </div>

            <!-- QQ号 -->
            <div class="bind-item">
              <div class="bind-info">
                <el-icon :size="20" color="#12B7F5"><ChatDotSquare /></el-icon>
                <div class="bind-text">
                  <div class="bind-label">QQ号</div>
                  <div class="bind-value">{{ userInfo.qq_nickname || (userInfo.qq_openid ? '已绑定' : '未绑定') }}</div>
                </div>
              </div>
              <el-button 
                v-if="userInfo.qq_openid" 
                type="danger" 
                size="small" 
                text
                @click="handleUnbind('qq')"
                :disabled="!canUnbind('qq')"
              >
                解绑
              </el-button>
              <el-button 
                v-else 
                type="primary" 
                size="small"
                @click="handleBind('qq')"
              >
                绑定
              </el-button>
            </div>

            <!-- 微信号 -->
            <div class="bind-item">
              <div class="bind-info">
                <el-icon :size="20" color="#09BB07"><ChatLineSquare /></el-icon>
                <div class="bind-text">
                  <div class="bind-label">微信号</div>
                  <div class="bind-value">{{ userInfo.wechat_nickname || (userInfo.wechat_openid ? '已绑定' : '未绑定') }}</div>
                </div>
              </div>
              <el-button 
                v-if="userInfo.wechat_openid" 
                type="danger" 
                size="small" 
                text
                @click="handleUnbind('wechat')"
                :disabled="!canUnbind('wechat')"
              >
                解绑
              </el-button>
              <el-button 
                v-else 
                type="primary" 
                size="small"
                @click="handleBind('wechat')"
              >
                绑定
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 信息编辑 -->
      <el-col :span="16">
        <el-card class="rounded-card info-card" shadow="never">
          <template #header>
            <div class="card-header">
              <h3>个人信息</h3>
              <el-button type="primary" @click="handleSave" :loading="saving">
                保存
              </el-button>
            </div>
          </template>

          <el-form :model="formData" :rules="rules" ref="formRef" label-width="120px">
            <el-form-item label="昵称" prop="nickname">
              <el-input
                v-model="formData.nickname"
                placeholder="请输入昵称"
                maxlength="50"
                show-word-limit
              />
            </el-form-item>

            <el-form-item label="性别" prop="gender">
              <el-radio-group v-model="formData.gender">
                <el-radio label="male">男</el-radio>
                <el-radio label="female">女</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="年龄" prop="age">
              <el-input-number
                v-model="formData.age"
                :min="1"
                :max="150"
                controls-position="right"
                placeholder="请输入年龄"
              />
              <span style="margin-left: 8px">岁</span>
            </el-form-item>

            <el-form-item label="身高" prop="height">
              <el-input-number
                v-model="formData.height"
                :min="50"
                :max="250"
                :precision="1"
                :step="0.1"
                controls-position="right"
                placeholder="请输入身高"
              />
              <span style="margin-left: 8px">cm</span>
            </el-form-item>

            <el-form-item label="当前体重" prop="current_weight">
              <el-input-number
                v-model="formData.current_weight"
                :min="30"
                :max="settingsStore.weightUnit === 'jin' ? 600 : 300"
                :precision="1"
                :step="0.1"
                controls-position="right"
                :placeholder="`请输入当前体重（${settingsStore.getWeightUnitText()}）`"
              />
              <span style="margin-left: 8px">{{ settingsStore.getWeightUnitText() }}</span>
            </el-form-item>

            <el-form-item label="目标体重" prop="target_weight">
              <el-input-number
                v-model="formData.target_weight"
                :min="30"
                :max="settingsStore.weightUnit === 'jin' ? 600 : 300"
                :precision="1"
                :step="0.1"
                controls-position="right"
                :placeholder="`请输入目标体重（${settingsStore.getWeightUnitText()}）`"
              />
              <span style="margin-left: 8px">{{ settingsStore.getWeightUnitText() }}</span>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 健康指标 -->
        <el-card class="rounded-card health-card" shadow="never" style="margin-top: 24px;">
          <template #header>
            <h3>健康指标</h3>
          </template>

          <el-row :gutter="24">
            <el-col :span="12">
              <div class="health-item">
                <div class="health-label">BMI 指数</div>
                <div class="health-value">
                  <span class="value">{{ stats.bmi || '--' }}</span>
                  <el-tag v-if="stats.bmi" :type="getBMIType(stats.bmi)" size="small" style="margin-left: 12px">
                    {{ getBMIStatus(stats.bmi) }}
                  </el-tag>
                </div>
                <div class="health-desc">
                  正常范围：18.5 - 24.9
                </div>
              </div>
            </el-col>

            <el-col :span="12">
              <div class="health-item">
                <div class="health-label">基础代谢率</div>
                <div class="health-value">
                  <span class="value">{{ stats.bmr || '--' }}</span>
                  <span v-if="stats.bmr" class="unit">kcal/天</span>
                </div>
                <div class="health-desc">
                  维持基本生命活动所需热量
                </div>
              </div>
            </el-col>

            <el-col :span="12" style="margin-top: 24px;">
              <div class="health-item">
                <div class="health-label">当前体重</div>
                <div class="health-value">
                  <span class="value">{{ displayCurrentWeight }}</span>
                  <span v-if="stats.current_weight" class="unit">{{ settingsStore.getWeightUnitText() }}</span>
                </div>
              </div>
            </el-col>

            <el-col :span="12" style="margin-top: 24px;">
              <div class="health-item">
                <div class="health-label">目标体重</div>
                <div class="health-value">
                  <span class="value">{{ displayTargetWeight }}</span>
                  <span v-if="stats.target_weight" class="unit">{{ settingsStore.getWeightUnitText() }}</span>
                </div>
                <div class="health-desc" v-if="stats.current_weight && stats.target_weight">
                  还需{{ getWeightDiff() }}
                </div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <!-- 手机号绑定弹窗 -->
    <el-dialog
      v-model="bindPhoneDialogVisible"
      title="绑定手机号"
      width="450px"
    >
      <el-form :model="bindPhoneForm" label-width="80px">
        <el-form-item label="手机号">
          <el-input
            v-model="bindPhoneForm.phone"
            placeholder="请输入手机号"
            maxlength="11"
          />
        </el-form-item>
        <el-form-item label="验证码">
          <div style="display: flex; gap: 12px;">
            <el-input
              v-model="bindPhoneForm.code"
              placeholder="请输入验证码"
              maxlength="6"
            />
            <el-button
              @click="sendCode"
              :disabled="countdown > 0 || sendingCode"
              :loading="sendingCode"
            >
              {{ countdown > 0 ? `${countdown}s` : '发送验证码' }}
            </el-button>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="bindPhoneDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmBindPhone">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useUserStore } from '@/stores/user'
import { useSettingsStore } from '@/stores/settings'
import { getCurrentUser, updateUser, getUserStats } from '@/api/user'
import { bindPhone, unbindAccount, sendBindSmsCode } from '@/api/account'
import { getQQBindUrl, getWechatBindUrl } from '@/api/bind'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Camera, Iphone, ChatDotSquare, ChatLineSquare } from '@element-plus/icons-vue'

const userStore = useUserStore()
const settingsStore = useSettingsStore()
const formRef = ref(null)
const saving = ref(false)

const userInfo = computed(() => userStore.userInfo || {})
const token = computed(() => localStorage.getItem('token'))

const formData = ref({
  nickname: '',
  gender: '',
  age: null,
  height: null,
  current_weight: null,
  target_weight: null
})

const stats = ref({})

const rules = {
  nickname: [
    { required: true, message: '请输入昵称', trigger: 'blur' },
    { min: 2, max: 50, message: '昵称长度在 2 到 50 个字符', trigger: 'blur' }
  ]
}

const genderText = computed(() => {
  const map = { male: '男', female: '女' }
  return map[userInfo.value.gender] || '未设置'
})

// 加载用户信息
const loadUserInfo = async () => {
  try {
    const userData = await getCurrentUser()
    
    // 更新 store
    userStore.setUserInfo(userData)
    
    // 回填表单数据（体重需要转换为显示单位）
    formData.value = {
      nickname: userData.nickname || '',
      gender: userData.gender || '',
      age: userData.age || null,
      height: userData.height || null,
      current_weight: userData.current_weight ? parseFloat(settingsStore.convertWeightToDisplay(userData.current_weight)) : null,
      target_weight: userData.target_weight ? parseFloat(settingsStore.convertWeightToDisplay(userData.target_weight)) : null
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
  }
}

// 加载健康数据
const loadStats = async () => {
  try {
    const res = await getUserStats()
    stats.value = res.data
  } catch (error) {
    console.error('加载健康数据失败:', error)
  }
}

// 上传头像前的校验
const beforeAvatarUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传图片文件')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB')
    return false
  }
  return true
}

// 上传成功
const handleAvatarSuccess = (response) => {
  if (response.code === 200) {
    userStore.setUserInfo({ avatar: response.data.avatar_url })
    ElMessage.success('头像更新成功')
  }
}

// 保存信息
const handleSave = async () => {
  try {
    await formRef.value.validate()
    saving.value = true
    
    // 准备保存的数据（体重需要转换为kg）
    const saveData = {
      nickname: formData.value.nickname,
      gender: formData.value.gender,
      age: formData.value.age,
      height: formData.value.height,
      current_weight: formData.value.current_weight ? settingsStore.convertWeightToKg(formData.value.current_weight) : null,
      target_weight: formData.value.target_weight ? settingsStore.convertWeightToKg(formData.value.target_weight) : null
    }
    
    const updatedUser = await updateUser(saveData)
    
    // 更新store中的用户信息
    userStore.setUserInfo(updatedUser)
    
    ElMessage.success('保存成功')
    
    // 重新加载健康数据
    await loadStats()
    
    // 重新加载用户信息以更新计算后的 BMI/BMR
    await loadUserInfo()
  } catch (error) {
    console.error('保存失败:', error)
  } finally {
    saving.value = false
  }
}

// 获取BMI状态
const getBMIStatus = (bmi) => {
  if (!bmi) return '未知'
  if (bmi < 18.5) return '偏瘦'
  if (bmi < 24.9) return '正常'
  if (bmi < 29.9) return '偏胖'
  return '肥胖'
}

// 获取BMI类型
const getBMIType = (bmi) => {
  if (!bmi) return 'info'
  if (bmi < 18.5) return 'warning'
  if (bmi < 24.9) return 'success'
  if (bmi < 29.9) return 'warning'
  return 'danger'
}

// 计算转换后的当前体重
const displayCurrentWeight = computed(() => {
  if (!stats.value.current_weight) return '--'
  return settingsStore.convertWeightToDisplay(stats.value.current_weight)
})

// 计算转换后的目标体重
const displayTargetWeight = computed(() => {
  if (!stats.value.target_weight) return '--'
  return settingsStore.convertWeightToDisplay(stats.value.target_weight)
})

// 获取体重差距
const getWeightDiff = () => {
  const diff = Math.abs(stats.value.current_weight - stats.value.target_weight)
  const displayDiff = settingsStore.convertWeightToDisplay(diff)
  const action = stats.value.current_weight > stats.value.target_weight ? '减重' : '增重'
  const unit = settingsStore.getWeightUnitText()
  return `${action} ${displayDiff} ${unit}`
}

// 判断是否可以解绑（至少保疙1个绑定方式）
const canUnbind = (type) => {
  const hasPhone = !!userInfo.value.phone
  const hasQQ = !!userInfo.value.qq_openid
  const hasWechat = !!userInfo.value.wechat_openid
  
  const bindCount = [hasPhone, hasQQ, hasWechat].filter(Boolean).length
  
  // 至少保疙1个绑定方式
  return bindCount > 1
}

// 绑定账号
const handleBind = async (type) => {
  if (type === 'phone') {
    // 手机号绑定：显示弹窗
    showBindPhoneDialog()
  } else if (type === 'qq') {
    // QQ授权绑定
    try {
      ElMessage.info('正在跳转QQ授权...')
      const res = await getQQBindUrl()
      console.log('QQ绑定URL响应:', res)
      // 在弹窗中打开授权页面
      const bindUrl = res.bind_url || res.data?.bind_url
      if (bindUrl) {
        window.open(bindUrl, 'QQ绑定', 'width=800,height=600')
      } else {
        ElMessage.error('获取绑定链接失败')
      }
    } catch (error) {
      console.error('获取QQ绑定URL失败:', error)
      ElMessage.error(error.response?.data?.detail || '获取绑定链接失败，请重试')
    }
  } else if (type === 'wechat') {
    // 微信授权绑定
    try {
      ElMessage.info('正在跳转微信授权...')
      const res = await getWechatBindUrl()
      console.log('微信绑定URL响应:', res)
      // 在弹窗中打开授权页面
      const bindUrl = res.bind_url || res.data?.bind_url
      if (bindUrl) {
        window.open(bindUrl, '微信绑定', 'width=800,height=600')
      } else {
        ElMessage.error('获取绑定链接失败')
      }
    } catch (error) {
      console.error('获取微信绑定URL失败:', error)
      ElMessage.error(error.response?.data?.detail || '获取绑定链接失败，请重试')
    }
  }
}

// 手机号绑定弹窗
const bindPhoneDialogVisible = ref(false)
const bindPhoneForm = ref({
  phone: '',
  code: ''
})
const sendingCode = ref(false)
const countdown = ref(0)

const showBindPhoneDialog = () => {
  bindPhoneForm.value = { phone: '', code: '' }
  countdown.value = 0
  bindPhoneDialogVisible.value = true
}

// 发送验证码
const sendCode = async () => {
  if (!bindPhoneForm.value.phone) {
    ElMessage.error('请输入手机号')
    return
  }
  
  if (!/^1[3-9]\d{9}$/.test(bindPhoneForm.value.phone)) {
    ElMessage.error('手机号格式不正确')
    return
  }
  
  try {
    sendingCode.value = true
    const res = await sendBindSmsCode(bindPhoneForm.value.phone)
    // 获取短信签名
    const smsSign = res.data?.sms_sign || '平台'
    ElMessage.success({
      message: `验证码发送成功，请留意签名为【${smsSign}】的验证码短信`,
      duration: 5000  // 显示5秒
    })
    
    // 开始倒计时
    countdown.value = 60
    const timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(timer)
      }
    }, 1000)
  } catch (error) {
    console.error('发送验证码失败:', error)
    // 显示错误信息
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else if (error.message) {
      ElMessage.error(error.message)
    } else {
      ElMessage.error('发送验证码失败，请稍后重试')
    }
  } finally {
    sendingCode.value = false
  }
}

// 确认绑定手机号
const confirmBindPhone = async () => {
  if (!bindPhoneForm.value.phone || !bindPhoneForm.value.code) {
    ElMessage.error('请输入手机号和验证码')
    return
  }
  
  try {
    await bindPhone(bindPhoneForm.value)
    ElMessage.success('绑定成功')
    bindPhoneDialogVisible.value = false
    
    // 重新加载用户信息
    await loadUserInfo()
  } catch (error) {
    console.error('绑定失败:', error)
  }
}

// 解绑账号
const handleUnbind = async (type) => {
  try {
    const typeText = {
      phone: '手机号',
      qq: 'QQ号',
      wechat: '微信号'
    }[type]
    
    await ElMessageBox.confirm(
      `确定要解绑${typeText}吗？解绑后将无法通过该方式登录。`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await unbindAccount(type)
    ElMessage.success('解绑成功')
    
    // 重新加载用户信息
    await loadUserInfo()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('解绑失败:', error)
    }
  }
}

onMounted(async () => {
  // 确保设置已加载完成
  if (!settingsStore.isLoaded) {
    await settingsStore.loadSettings()
  }
  
  loadUserInfo()
  loadStats()
  
  // 监听绑定成功消息
  window.addEventListener('message', handleBindMessage)
})

onBeforeUnmount(() => {
  window.removeEventListener('message', handleBindMessage)
})

// 处理绑定成功消息
const handleBindMessage = (event) => {
  if (event.data && event.data.type === 'bind_success') {
    ElMessage.success('绑定成功')
    // 重新加载用户信息
    loadUserInfo()
  }
}
</script>

<style scoped>
.profile-container {
  max-width: 1400px;
  margin: 0 auto;
}

.profile-card {
  text-align: center;
}

.avatar-section {
  position: relative;
  display: inline-block;
  margin-bottom: 20px;
}

.avatar-section:hover .avatar-overlay {
  opacity: 1;
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 14px;
  opacity: 0;
  transition: opacity 0.3s;
  cursor: pointer;
}

.avatar-overlay .el-icon {
  font-size: 24px;
  margin-bottom: 4px;
}

.user-name {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.user-phone {
  font-size: 14px;
  color: #999;
  margin-bottom: 24px;
}

.quick-stats {
  display: flex;
  justify-content: space-around;
  padding: 20px 0;
  border-top: 1px solid #f0f0f0;
}

.quick-stat-item {
  text-align: center;
}

.quick-stat-item .stat-label {
  font-size: 13px;
  color: #999;
  margin-bottom: 8px;
}

.quick-stat-item .stat-value {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.health-item {
  padding: 20px;
  background: #f9fafb;
  border-radius: 12px;
}

.health-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 12px;
}

.health-value {
  display: flex;
  align-items: baseline;
  margin-bottom: 8px;
}

.health-value .value {
  font-size: 32px;
  font-weight: 600;
  color: #333;
}

.health-value .unit {
  font-size: 14px;
  color: #999;
  margin-left: 8px;
}

.health-desc {
  font-size: 12px;
  color: #999;
}

/* 账号绑定样式 */
.account-bind-card :deep(.el-card__header) {
  padding: 16px 20px;
}

.account-bind-card h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.bind-items {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.bind-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f9fafb;
  border-radius: 12px;
  transition: all 0.3s;
}

.bind-item:hover {
  background: #f0f2f5;
}

.bind-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.bind-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.bind-label {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.bind-value {
  font-size: 13px;
  color: #999;
}
</style>
