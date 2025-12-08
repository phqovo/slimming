<template>
  <div class="login-container">
    <div class="login-card rounded-card">
      <div class="login-header">
        <h1>体重管理平台</h1>
        <p>记录每一天，遇见更好的自己</p>
      </div>

      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" class="login-form">
        <el-form-item prop="phone">
          <el-input
            v-model="loginForm.phone"
            placeholder="请输入手机号"
            size="large"
            prefix-icon="Phone"
            maxlength="11"
          />
        </el-form-item>

        <el-form-item prop="code">
          <div class="code-input-wrapper">
            <el-input
              v-model="loginForm.code"
              placeholder="请输入验证码"
              size="large"
              prefix-icon="Message"
              maxlength="6"
            />
            <el-button
              :disabled="countdown > 0"
              @click="handleSendCode"
              class="send-code-btn"
              type="primary"
              size="large"
            >
              {{ countdown > 0 ? `${countdown}秒后重试` : '获取验证码' }}
            </el-button>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleLogin"
            class="login-btn"
          >
            登录 / 注册
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-tips">
        <p>首次登录将自动注册账号</p>
      </div>
      
      <!-- 第三方登录 -->
      <div class="oauth-login">
        <div class="oauth-divider">
          <span>或</span>
        </div>
        <div class="oauth-buttons">
          <el-button class="oauth-btn qq-btn" @click="handleQQLogin">
            <svg class="icon" viewBox="0 0 1024 1024" width="20" height="20">
              <path d="M824.8 613.2c-16-51.4-34.4-94.6-62.7-165.3C766.5 262.2 689.3 112 511.5 112 331.7 112 256.2 265.2 261 447.9c-28.4 70.8-46.7 113.7-62.7 165.3-34 109.5-23 154.8-14.6 155.8 18 2.2 70.1-82.4 70.1-82.4 0 49 25.2 112.9 79.8 159-26.4 8.1-85.7 29.9-71.6 53.8 11.4 19.3 196.2 12.3 249.5 6.3 53.3 6 238.1 13 249.5-6.3 14.1-23.8-45.3-45.7-71.6-53.8 54.6-46.2 79.8-110.1 79.8-159 0 0 52.1 84.6 70.1 82.4 8.5-1.1 19.5-46.4-14.5-155.8z" fill="currentColor"/>
            </svg>
            <span>QQ 登录</span>
          </el-button>
          <el-button class="oauth-btn wechat-btn" @click="handleWechatLogin">
            <svg class="icon" viewBox="0 0 1024 1024" width="20" height="20">
              <path d="M664.250054 368.541681c10.015098 0 19.892049 0.732687 29.67281 1.795902-26.647917-122.810047-159.358451-214.077703-310.826188-214.077703-169.353083 0-308.085774 114.232694-308.085774 259.274068 0 83.708494 46.165436 152.460344 123.281791 205.78483l-30.80868 91.730191 107.688651-53.455469c38.558178 7.53665 69.459249 15.308402 107.924753 15.308402 9.66308 0 19.230993-0.470721 28.752858-1.225921-6.025227-20.36584-9.521864-41.723264-9.521864-63.862493C402.328693 476.632491 517.908058 368.541681 664.250054 368.541681zM498.62897 285.87389c23.200398 0 38.557154 15.120012 38.557154 38.061874 0 22.846255-15.356756 38.156018-38.557154 38.156018-23.107492 0-46.260603-15.309763-46.260603-38.156018C452.368366 300.993902 475.522501 285.87389 498.62897 285.87389zM283.016307 362.090758c-23.107492 0-46.402843-15.309763-46.402843-38.156018 0-22.941862 23.295351-38.061874 46.402843-38.061874 23.081492 0 38.46301 15.120012 38.46301 38.061874C321.479317 346.780995 306.098822 362.090758 283.016307 362.090758zM945.448458 606.151333c0-121.888048-123.258255-221.236753-261.683954-221.236753-146.57838 0-262.015505 99.348706-262.015505 221.236753 0 122.06508 115.437126 221.200938 262.015505 221.200938 30.66644 0 61.617359-7.609305 92.423993-15.262354l84.513836 45.786813-23.178909-76.17082C899.379213 735.776599 945.448458 674.90216 945.448458 606.151333zM598.803483 567.994292c-15.332197 0-30.807704-15.096177-30.807704-30.501688 0-15.190034 15.475507-30.477129 30.807704-30.477129 23.295351 0 38.558178 15.287096 38.558178 30.477129C637.361661 552.898115 622.098834 567.994292 598.803483 567.994292zM768.25071 567.994292c-15.213011 0-30.594893-15.096177-30.594893-30.501688 0-15.190034 15.381882-30.477129 30.594893-30.477129 23.107492 0 38.558178 15.287096 38.558178 30.477129C806.808888 552.898115 791.358201 567.994292 768.25071 567.994292z" fill="currentColor"/>
            </svg>
            <span>微信登录</span>
          </el-button>
        </div>
      </div>
      
      <!-- 调试模式提示 -->
      <div v-if="debugMode" class="debug-notice">
        <p>⚠️ 当前为调试模式，不发送短信</p>
        <p v-if="debugCode" class="debug-code">验证码：<strong>{{ debugCode }}</strong></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useSettingsStore } from '@/stores/settings'
import { sendCode } from '@/api/user'
import request from '@/utils/request'

const router = useRouter()
const userStore = useUserStore()

const loginFormRef = ref(null)
const loading = ref(false)
const countdown = ref(0)
const debugMode = ref(false)
const debugCode = ref('')

const loginForm = reactive({
  phone: '',
  code: ''
})

const validatePhone = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入手机号'))
  } else if (!/^1[3-9]\d{9}$/.test(value)) {
    callback(new Error('请输入正确的手机号'))
  } else {
    callback()
  }
}

const rules = {
  phone: [{ validator: validatePhone, trigger: 'blur' }],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { min: 6, max: 6, message: '验证码为6位数字', trigger: 'blur' }
  ]
}

// 发送验证码
const handleSendCode = async () => {
  try {
    await loginFormRef.value.validateField('phone')
    
    const res = await sendCode(loginForm.phone)
    
    // 检查是否为调试模式
    if (res.data?.debug_mode) {
      debugMode.value = true
      debugCode.value = res.data.code
      ElMessage.warning('调试模式：未发送短信，验证码已显示在页面上')
    } else {
      debugMode.value = false
      debugCode.value = ''
      ElMessage.success('验证码已发送')
    }
    
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
  }
}

// 登录
const handleLogin = async () => {
  try {
    await loginFormRef.value.validate()
    
    loading.value = true
    const settingsStore = useSettingsStore()
    
    await userStore.handleLogin(loginForm.phone, loginForm.code)
    
    // 登录成功后，重新加载设置
    await settingsStore.reloadSettings()
    
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error) {
    console.error('登录失败:', error)
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else if (error.message) {
      ElMessage.error(error.message)
    } else {
      ElMessage.error('登录失败，请重试')
    }
  } finally {
    loading.value = false
  }
}

// QQ登录
const handleQQLogin = async () => {
  try {
    const res = await request.get('/oauth/qq/login-url')
    const width = 500
    const height = 600
    const left = (screen.width - width) / 2
    const top = (screen.height - height) / 2
    
    window.open(
      res.login_url,
      'qq_login',
      `width=${width},height=${height},left=${left},top=${top}`
    )
  } catch (error) {
    console.error('QQ登录失败:', error)
    ElMessage.error('获取QQ登录链接失败')
  }
}

// 微信登录
const handleWechatLogin = async () => {
  try {
    const res = await request.get('/oauth/wechat/login-url')
    const width = 500
    const height = 600
    const left = (screen.width - width) / 2
    const top = (screen.height - height) / 2
    
    window.open(
      res.login_url,
      'wechat_login',
      `width=${width},height=${height},left=${left},top=${top}`
    )
  } catch (error) {
    console.error('微信登录失败:', error)
    ElMessage.error('获取微信登录链接失败')
  }
}

// 监听OAuth登录成功消息
const handleOAuthMessage = (event) => {
  if (event.data.type === 'oauth_login_success') {
    // OAuth登录成功，跳转到首页
    router.push('/')
  }
}

onMounted(() => {
  window.addEventListener('message', handleOAuthMessage)
})

onUnmounted(() => {
  window.removeEventListener('message', handleOAuthMessage)
})
</script>

<style scoped>
.login-container {
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 420px;
  padding: 48px 40px;
  background: white;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-header h1 {
  font-size: 28px;
  color: #333;
  margin-bottom: 12px;
  font-weight: 600;
}

.login-header p {
  font-size: 14px;
  color: #999;
}

.login-form {
  margin-bottom: 20px;
}

.code-input-wrapper {
  display: flex;
  gap: 12px;
}

.code-input-wrapper .el-input {
  flex: 1;
}

.send-code-btn {
  min-width: 120px;
}

.login-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 8px;
}

.login-tips {
  text-align: center;
  font-size: 13px;
  color: #999;
}

.debug-notice {
  margin-top: 20px;
  padding: 12px 16px;
  background: #fff3e0;
  border: 1px solid #ff9800;
  border-radius: 8px;
  color: #e65100;
  font-size: 13px;
  text-align: center;
}

.debug-notice p {
  margin: 4px 0;
}

.debug-code {
  font-size: 16px;
  margin-top: 8px;
}

.debug-code strong {
  color: #d32f2f;
  font-size: 24px;
  letter-spacing: 2px;
}

/* 第三方登录样式 */
.oauth-login {
  margin-top: 30px;
}

.oauth-divider {
  text-align: center;
  position: relative;
  margin-bottom: 20px;
}

.oauth-divider::before,
.oauth-divider::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 40%;
  height: 1px;
  background: #e0e0e0;
}

.oauth-divider::before {
  left: 0;
}

.oauth-divider::after {
  right: 0;
}

.oauth-divider span {
  color: #999;
  font-size: 14px;
  padding: 0 16px;
  background: white;
}

.oauth-buttons {
  display: flex;
  gap: 16px;
}

.oauth-btn {
  flex: 1;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  transition: all 0.3s;
}

.oauth-btn .icon {
  flex-shrink: 0;
}

.qq-btn {
  background: #12b7f5;
  color: white;
  border: none;
}

.qq-btn:hover {
  background: #0da5de;
}

.wechat-btn {
  background: #09bb07;
  color: white;
  border: none;
}

.wechat-btn:hover {
  background: #08a006;
}
</style>
