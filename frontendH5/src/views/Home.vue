<template>
  <div class="home-page">
    <!-- 顶部用户信息 -->
    <div class="header-card">
      <div class="user-info">
        <van-image
          round
          width="50"
          height="50"
          :src="userInfo?.avatar || 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg'"
        />
        <div class="user-text">
          <div class="nickname">{{ userInfo?.nickname || '用户' }}</div>
          <div class="slogan">健康生活，从记录开始</div>
        </div>
      </div>
    </div>

    <!-- 今日数据汇总 -->
    <div class="today-summary">
      <div class="summary-title">今日数据</div>
      <van-grid :column-num="3" :border="false">
        <van-grid-item>
          <template #icon>
            <div class="data-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)">
              <van-icon name="balance-o" size="24" color="#fff" />
            </div>
          </template>
          <template #text>
            <div class="data-value">{{ todayWeight || '--' }}</div>
            <div class="data-label">体重(kg)</div>
          </template>
        </van-grid-item>
        <van-grid-item>
          <template #icon>
            <div class="data-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%)">
              <van-icon name="fire-o" size="24" color="#fff" />
            </div>
          </template>
          <template #text>
            <div class="data-value">{{ todayCalories || 0 }}</div>
            <div class="data-label">摄入(kcal)</div>
          </template>
        </van-grid-item>
        <van-grid-item>
          <template #icon>
            <div class="data-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)">
              <van-icon name="underway-o" size="24" color="#fff" />
            </div>
          </template>
          <template #text>
            <div class="data-value">{{ todayExercise || 0 }}</div>
            <div class="data-label">消耗(kcal)</div>
          </template>
        </van-grid-item>
      </van-grid>
    </div>

    <!-- 快捷操作 -->
    <div class="quick-actions">
      <div class="section-title">快捷记录</div>
      <van-grid :column-num="3" :border="false">
        <van-grid-item icon="balance-pay" text="记录体重" @click="goTo('/weight/add')" />
        <van-grid-item icon="food-o" text="添加饮食" @click="goTo('/diet/add')" />
        <van-grid-item icon="play-circle-o" text="添加运动" @click="goTo('/exercise/add')" />
      </van-grid>
    </div>

    <!-- 今日饮食记录 -->
    <div class="today-records">
      <div class="section-title">
        <span>今日饮食</span>
        <van-button size="small" type="primary" plain @click="goTo('/record')">查看更多</van-button>
      </div>
      <van-empty v-if="!dietRecords.length" description="暂无记录" />
      <div v-else class="record-list">
        <div v-for="record in dietRecords" :key="record.id" class="record-item">
          <div class="record-left">
            <div class="meal-tag">{{ getMealName(record.meal_type) }}</div>
            <div class="food-name">{{ record.food_name }}</div>
          </div>
          <div class="record-right">
            <div class="calories">{{ record.calories }} kcal</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 今日运动记录 -->
    <div class="today-records">
      <div class="section-title">
        <span>今日运动</span>
      </div>
      <van-empty v-if="!exerciseRecords.length" description="暂无记录" />
      <div v-else class="record-list">
        <div v-for="record in exerciseRecords" :key="record.id" class="record-item">
          <div class="record-left">
            <van-icon name="play-circle" color="#1989fa" />
            <div class="exercise-name">{{ record.exercise_type }}</div>
          </div>
          <div class="record-right">
            <div class="duration">{{ record.duration }}分钟</div>
            <div class="calories">{{ record.calories }} kcal</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { getTodayDashboard } from '@/api/home'
import dayjs from 'dayjs'

const router = useRouter()
const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || '{}'))
const todayWeight = ref(null)
const todayCalories = ref(0)
const todayExercise = ref(0)
const dietRecords = ref([])
const exerciseRecords = ref([])

// 获取今日数据
const fetchTodayData = async () => {
  try {
    const res = await getTodayDashboard()
    todayWeight.value = res.latest_weight?.weight
    todayCalories.value = res.today_calories || 0
    todayExercise.value = res.today_exercise_calories || 0
    dietRecords.value = res.today_diet_records || []
    exerciseRecords.value = res.today_exercise_records || []
  } catch (error) {
    console.error('获取数据失败', error)
  }
}

// 餐次名称映射
const getMealName = (type) => {
  const mealMap = {
    breakfast: '早餐',
    lunch: '午餐',
    dinner: '晚餐',
    snack: '加餐'
  }
  return mealMap[type] || type
}

// 跳转
const goTo = (path) => {
  router.push(path)
}

onMounted(() => {
  fetchTodayData()
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: #f7f8fa;
  padding-bottom: 20px;
}

.header-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px 16px 30px;
  color: white;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-text {
  flex: 1;
}

.nickname {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 4px;
}

.slogan {
  font-size: 13px;
  opacity: 0.9;
}

.today-summary {
  background: white;
  margin: -20px 16px 12px;
  border-radius: 12px;
  padding: 16px 0;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.summary-title {
  font-size: 16px;
  font-weight: bold;
  padding: 0 16px 12px;
}

.data-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 8px;
}

.data-value {
  font-size: 20px;
  font-weight: bold;
  color: #323233;
  margin: 4px 0;
}

.data-label {
  font-size: 12px;
  color: #969799;
}

.quick-actions,
.today-records {
  background: white;
  margin: 12px 16px;
  border-radius: 12px;
  padding: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.record-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.record-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f7f8fa;
  border-radius: 8px;
}

.record-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.meal-tag {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.food-name,
.exercise-name {
  font-size: 14px;
  color: #323233;
}

.record-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.duration {
  font-size: 12px;
  color: #969799;
}

.calories {
  font-size: 14px;
  color: #f5576c;
  font-weight: bold;
}
</style>
