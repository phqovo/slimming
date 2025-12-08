<template>
  <div class="login-page">
    <div class="login-header">
      <h1>体重管理</h1>
      <p>健康生活，从记录开始</p>
    </div>

    <van-form @submit="onSubmit" class="login-form">
      <van-cell-group inset>
        <van-field
          v-model="formData.phone"
          name="phone"
          label="手机号"
          placeholder="请输入手机号"
          :rules="[{ required: true, message: '请输入手机号' }]"
          type="tel"
          maxlength="11"
        />
        <van-field
          v-model="formData.code"
          center
          clearable
          label="验证码"
          placeholder="请输入验证码"
          :rules="[{ required: true, message: '请输入验证码' }]"
        >
          <template #button>
            <van-button
              size="small"
              type="primary"
              :disabled="countdown > 0"
              @click="sendCode"
            >
              {{ countdown > 0 ? `${countdown}秒后重试` : '发送验证码' }}
            </van-button>
          </template>
        </van-field>
      </van-cell-group>

      <div style="margin: 30px 16px;">
        <van-button round block type="primary" native-type="submit" :loading="loading">
          登录
        </van-button>
      </div>
    </van-form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { sendVerificationCode, login } from '@/api/auth'

const router = useRouter()
const loading = ref(false)
const countdown = ref(0)
const formData = ref({
  phone: '',
  code: ''
})

// 发送验证码
const sendCode = async () => {
  if (!formData.value.phone || formData.value.phone.length !== 11) {
    showToast('请输入正确的手机号')
    return
  }

  try {
    await sendVerificationCode({ phone: formData.value.phone })
    showToast('验证码已发送')
    countdown.value = 60
    
    const timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(timer)
      }
    }, 1000)
  } catch (error) {
    showToast(error.response?.data?.detail || '发送失败')
  }
}

// 登录
const onSubmit = async () => {
  loading.value = true
  try {
    const res = await login(formData.value)
    localStorage.setItem('token', res.token)
    localStorage.setItem('userInfo', JSON.stringify(res.user))
    showToast('登录成功')
    router.push('/home')
  } catch (error) {
    showToast(error.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 60px 0;
}

.login-header {
  text-align: center;
  color: white;
  margin-bottom: 60px;
}

.login-header h1 {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 10px;
}

.login-header p {
  font-size: 14px;
  opacity: 0.9;
}

.login-form {
  padding: 0 16px;
}
</style>
