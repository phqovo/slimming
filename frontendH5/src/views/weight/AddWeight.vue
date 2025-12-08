<template>
  <div class="add-weight-page">
    <van-nav-bar title="记录体重" left-arrow @click-left="$router.back()" />
    
    <van-form @submit="onSubmit">
      <van-cell-group inset>
        <van-field
          v-model="formData.weight"
          name="weight"
          label="体重"
          placeholder="请输入体重"
          type="number"
          :rules="[{ required: true, message: '请输入体重' }]"
        >
          <template #right-icon>
            <span class="unit-text">kg</span>
          </template>
        </van-field>
        
        <van-field
          v-model="formData.date"
          is-link
          readonly
          name="date"
          label="日期"
          placeholder="选择日期"
          @click="showDatePicker = true"
        />
      </van-cell-group>

      <div style="margin: 30px 16px;">
        <van-button round block type="primary" native-type="submit" :loading="loading">
          保存
        </van-button>
      </div>
    </van-form>

    <van-popup v-model:show="showDatePicker" position="bottom">
      <van-date-picker
        v-model="currentDate"
        @confirm="onDateConfirm"
        @cancel="showDatePicker = false"
      />
    </van-popup>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { addWeightRecord } from '@/api/weight'
import dayjs from 'dayjs'

const router = useRouter()
const loading = ref(false)
const showDatePicker = ref(false)
const currentDate = ref(new Date())
const formData = ref({
  weight: '',
  date: dayjs().format('YYYY-MM-DD')
})

const onDateConfirm = () => {
  formData.value.date = dayjs(currentDate.value).format('YYYY-MM-DD')
  showDatePicker.value = false
}

const onSubmit = async () => {
  loading.value = true
  try {
    await addWeightRecord({
      weight: parseFloat(formData.value.weight),
      record_date: formData.value.date
    })
    showToast('保存成功')
    router.back()
  } catch (error) {
    showToast(error.response?.data?.detail || '保存失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.add-weight-page {
  min-height: 100vh;
  background: #f7f8fa;
}

.unit-text {
  color: #969799;
  font-size: 14px;
}
</style>
