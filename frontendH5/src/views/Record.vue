<template>
  <div class="record-page">
    <van-nav-bar title="我的记录" />
    
    <van-tabs v-model:active="activeTab" @change="onTabChange">
      <van-tab title="饮食记录" name="diet">
        <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
          <van-list
            v-model:loading="loading"
            :finished="finished"
            finished-text="没有更多了"
            @load="onLoad"
          >
            <div class="record-list">
              <div v-for="item in list" :key="item.date" class="date-group">
                <div class="date-header">{{ item.date }}</div>
                <div class="meal-group" v-for="meal in item.meals" :key="meal.meal_type">
                  <div class="meal-header">
                    <van-tag :type="getMealType(meal.meal_type)">{{ getMealName(meal.meal_type) }}</van-tag>
                    <span class="total-calories">{{ meal.total_calories }} kcal</span>
                  </div>
                  <div class="food-list">
                    <div v-for="food in meal.foods" :key="food.id" class="food-item">
                      <span class="food-name">{{ food.food_name }}</span>
                      <span class="food-portion" v-if="food.portion">{{ food.portion }}</span>
                      <span class="food-calories">{{ food.calories }} kcal</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </van-list>
        </van-pull-refresh>
      </van-tab>

      <van-tab title="运动记录" name="exercise">
        <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
          <van-list
            v-model:loading="loading"
            :finished="finished"
            finished-text="没有更多了"
            @load="onLoad"
          >
            <div class="record-list">
              <div v-for="item in list" :key="item.date" class="date-group">
                <div class="date-header">{{ item.date }}</div>
                <div class="exercise-list">
                  <div v-for="exercise in item.exercises" :key="exercise.id" class="exercise-item">
                    <van-icon name="play-circle" color="#1989fa" />
                    <div class="exercise-info">
                      <div class="exercise-name">{{ exercise.exercise_type }}</div>
                      <div class="exercise-detail">
                        {{ exercise.duration }}分钟
                        <span v-if="exercise.distance"> · {{ exercise.distance }}km</span>
                      </div>
                    </div>
                    <div class="exercise-calories">{{ exercise.calories }} kcal</div>
                  </div>
                </div>
              </div>
            </div>
          </van-list>
        </van-pull-refresh>
      </van-tab>

      <van-tab title="体重记录" name="weight">
        <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
          <van-list
            v-model:loading="loading"
            :finished="finished"
            finished-text="没有更多了"
            @load="onLoad"
          >
            <div class="weight-list">
              <van-cell-group inset>
                <van-cell v-for="item in list" :key="item.id">
                  <template #title>
                    <span class="weight-value">{{ item.weight }} kg</span>
                  </template>
                  <template #label>
                    {{ item.record_date }}
                  </template>
                  <template #right-icon>
                    <van-tag v-if="item.change" :type="item.change > 0 ? 'danger' : 'success'">
                      {{ item.change > 0 ? '+' : '' }}{{ item.change }} kg
                    </van-tag>
                  </template>
                </van-cell>
              </van-cell-group>
            </div>
          </van-list>
        </van-pull-refresh>
      </van-tab>
    </van-tabs>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { showToast } from 'vant'
import { getDietRecords } from '@/api/diet'
import { getExerciseRecords } from '@/api/exercise'
import { getWeightHistory } from '@/api/weight'

const activeTab = ref('diet')
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)
const list = ref([])
const page = ref(1)
const pageSize = ref(20)

// 获取数据
const fetchData = async (isRefresh = false) => {
  if (isRefresh) {
    page.value = 1
    list.value = []
    finished.value = false
  }

  try {
    let res
    let newData = []
    
    if (activeTab.value === 'diet') {
      res = await getDietRecords({ page: page.value, page_size: pageSize.value })
      // 后端直接返回数组，不是 { items: [] }
      const items = Array.isArray(res) ? res : (res.items || [])
      newData = formatDietData(items)
    } else if (activeTab.value === 'exercise') {
      res = await getExerciseRecords({ page: page.value, page_size: pageSize.value })
      const items = Array.isArray(res) ? res : (res.items || [])
      newData = formatExerciseData(items)
    } else {
      res = await getWeightHistory({ page: page.value, page_size: pageSize.value })
      newData = Array.isArray(res) ? res : (res.items || [])
    }

    // 合并数据
    if (isRefresh) {
      list.value = newData
    } else {
      list.value = [...list.value, ...newData]
    }

    // 判断是否还有更多数据
    const actualItems = Array.isArray(res) ? res : (res.items || [])
    if (actualItems.length === 0 || actualItems.length < pageSize.value) {
      finished.value = true
    }
    
    return true
  } catch (error) {
    console.error('获取数据失败:', error)
    showToast('获取失败')
    return false
  }
}

// 格式化饮食数据（按日期和餐次分组）
const formatDietData = (items) => {
  const grouped = {}
  items.forEach(item => {
    const date = item.record_date
    if (!grouped[date]) {
      grouped[date] = { date, meals: {} }
    }
    const mealType = item.meal_type
    if (!grouped[date].meals[mealType]) {
      grouped[date].meals[mealType] = {
        meal_type: mealType,
        foods: [],
        total_calories: 0
      }
    }
    grouped[date].meals[mealType].foods.push(item)
    grouped[date].meals[mealType].total_calories += parseFloat(item.calories || 0)
  })

  return Object.values(grouped).map(item => ({
    ...item,
    meals: Object.values(item.meals)
  }))
}

// 格式化运动数据（按日期分组）
const formatExerciseData = (items) => {
  const grouped = {}
  items.forEach(item => {
    const date = item.record_date
    if (!grouped[date]) {
      grouped[date] = { date, exercises: [] }
    }
    grouped[date].exercises.push(item)
  })
  return Object.values(grouped)
}

// 餐次映射
const getMealName = (type) => {
  const map = { breakfast: '早餐', lunch: '午餐', dinner: '晚餐', snack: '加餐' }
  return map[type] || type
}

const getMealType = (type) => {
  const map = { breakfast: 'success', lunch: 'warning', dinner: 'primary', snack: 'default' }
  return map[type] || 'default'
}

// 下拉刷新
const onRefresh = async () => {
  refreshing.value = true
  page.value = 1
  finished.value = false
  await fetchData(true)
  refreshing.value = false
}

// 上拉加载
const onLoad = async () => {
  if (finished.value) {
    loading.value = false
    return
  }
  
  const success = await fetchData()
  loading.value = false
  
  // 只有加载成功才增加页码
  if (success && !finished.value) {
    page.value++
  }
}

// 切换标签
const onTabChange = () => {
  list.value = []
  page.value = 1
  finished.value = false
  fetchData()
}
</script>

<style scoped>
.record-page {
  min-height: 100vh;
  background: #f7f8fa;
}

.record-list {
  padding: 16px;
}

.date-group {
  margin-bottom: 20px;
}

.date-header {
  font-size: 14px;
  color: #969799;
  margin-bottom: 12px;
  padding-left: 8px;
}

.meal-group {
  background: white;
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 12px;
}

.meal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px dashed #ebedf0;
}

.total-calories {
  font-size: 14px;
  color: #f5576c;
  font-weight: bold;
}

.food-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.food-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.food-name {
  flex: 1;
  color: #323233;
}

.food-portion {
  font-size: 12px;
  color: #969799;
  background: #f7f8fa;
  padding: 2px 8px;
  border-radius: 4px;
}

.food-calories {
  color: #f5576c;
}

.exercise-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.exercise-item {
  background: white;
  border-radius: 12px;
  padding: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.exercise-info {
  flex: 1;
}

.exercise-name {
  font-size: 14px;
  color: #323233;
  font-weight: bold;
  margin-bottom: 4px;
}

.exercise-detail {
  font-size: 12px;
  color: #969799;
}

.exercise-calories {
  font-size: 14px;
  color: #1989fa;
  font-weight: bold;
}

.weight-list {
  padding: 16px;
}

.weight-value {
  font-size: 18px;
  font-weight: bold;
  color: #323233;
}
</style>
