<template>
  <div class="add-exercise-page">
    <van-nav-bar title="添加运动" left-arrow @click-left="$router.back()" />
    
    <van-form @submit="onSubmit">
      <van-cell-group inset>
        <van-field
          v-model="formData.exerciseType"
          name="exerciseType"
          label="运动类型"
          placeholder="如：跑步、游泳"
          :rules="[{ required: true, message: '请输入运动类型' }]"
        />
        
        <van-field
          v-model="formData.duration"
          name="duration"
          label="时长"
          placeholder="请输入时长"
          type="number"
          :rules="[{ required: true, message: '请输入时长' }]"
        >
          <template #right-icon>
            <span class="unit-text">分钟</span>
          </template>
        </van-field>
        
        <van-field
          v-model="formData.distance"
          name="distance"
          label="距离"
          placeholder="选填"
          type="number"
        >
          <template #right-icon>
            <span class="unit-text">km</span>
          </template>
        </van-field>
        
        <van-field
          v-model="formData.calories"
          name="calories"
          label="消耗热量"
          placeholder="请输入热量"
          type="number"
        >
          <template #right-icon>
            <span class="unit-text">kcal</span>
          </template>
        </van-field>
      </van-cell-group>

      <div style="margin: 30px 16px;">
        <van-button round block type="primary" native-type="submit" :loading="loading">
          保存
        </van-button>
      </div>
    </van-form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { addExerciseRecord } from '@/api/exercise'

const router = useRouter()
const loading = ref(false)
const formData = ref({
  exerciseType: '',
  duration: '',
  distance: '',
  calories: ''
})

const onSubmit = async () => {
  loading.value = true
  try {
    await addExerciseRecord({
      exercise_type: formData.value.exerciseType,
      duration: parseInt(formData.value.duration),
      distance: parseFloat(formData.value.distance) || null,
      calories: parseFloat(formData.value.calories) || 0
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
.add-exercise-page {
  min-height: 100vh;
  background: #f7f8fa;
}

.unit-text {
  color: #969799;
  font-size: 14px;
}
</style>
