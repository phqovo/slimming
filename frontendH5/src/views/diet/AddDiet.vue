<template>
  <div class="add-diet-page">
    <van-nav-bar title="添加饮食" left-arrow @click-left="$router.back()" />
    
    <van-form @submit="onSubmit">
      <van-cell-group inset>
        <van-field
          v-model="formData.foodName"
          name="foodName"
          label="食物"
          placeholder="请输入食物名称"
          :rules="[{ required: true, message: '请输入食物名称' }]"
        />
        
        <van-field
          v-model="mealTypeLabel"
          is-link
          readonly
          name="mealType"
          label="餐次"
          placeholder="选择餐次"
          @click="showMealPicker = true"
        />
        
        <van-field
          v-model="formData.calories"
          name="calories"
          label="热量"
          placeholder="请输入热量"
          type="number"
        >
          <template #right-icon>
            <span class="unit-text">kcal</span>
          </template>
        </van-field>
        
        <van-field
          v-model="formData.portion"
          name="portion"
          label="份量"
          placeholder="如：1碗、100g"
        />
      </van-cell-group>

      <div style="margin: 30px 16px;">
        <van-button round block type="primary" native-type="submit" :loading="loading">
          保存
        </van-button>
      </div>
    </van-form>

    <van-popup v-model:show="showMealPicker" position="bottom">
      <van-picker
        :columns="mealColumns"
        @confirm="onMealConfirm"
        @cancel="showMealPicker = false"
      />
    </van-popup>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { addDietRecord } from '@/api/diet'

const router = useRouter()
const loading = ref(false)
const showMealPicker = ref(false)
const mealTypeLabel = ref('早餐')
const formData = ref({
  foodName: '',
  mealType: 'breakfast',
  calories: '',
  portion: ''
})

const mealColumns = [
  { text: '早餐', value: 'breakfast' },
  { text: '午餐', value: 'lunch' },
  { text: '晚餐', value: 'dinner' },
  { text: '加餐', value: 'snack' }
]

const onMealConfirm = ({ selectedOptions }) => {
  mealTypeLabel.value = selectedOptions[0].text
  formData.value.mealType = selectedOptions[0].value
  showMealPicker.value = false
}

const onSubmit = async () => {
  loading.value = true
  try {
    await addDietRecord({
      food_name: formData.value.foodName,
      meal_type: formData.value.mealType,
      calories: parseFloat(formData.value.calories) || 0,
      portion: formData.value.portion
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
.add-diet-page {
  min-height: 100vh;
  background: #f7f8fa;
}

.unit-text {
  color: #969799;
  font-size: 14px;
}
</style>
