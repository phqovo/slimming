<template>
  <div class="body-composition-report" v-loading="loading">
    <!-- 暂无数据提示 -->
    <div v-if="!bodyData && !loading" class="no-data">
      <el-empty description="暂无体重数据，请先同步数据" />
    </div>

    <!-- 有数据时显示报告 -->
    <template v-if="bodyData">
    <!-- 页面顶部 -->
    <div class="page-header">
      <h1 class="main-title">人体成分分析报告</h1>
      <div class="user-info">
        <span>姓名: {{ userInfo.nickname || userInfo.username || '-' }}</span>
        <span>性别: {{ userInfo.gender === 'male' ? '男' : userInfo.gender === 'female' ? '女' : '-' }}</span>
        <span>年龄: {{ userInfo.age || '-' }}</span>
        <span>身高: {{ userInfo.height ? userInfo.height + 'cm' : '-' }}</span>
        <span>测量时间: {{ formatDate(bodyData.measure_date) }}</span>
      </div>
    </div>

    <!-- 身体指标得分卡片 -->
    <div class="card score-card">
      <h2 class="card-title">身体指标得分</h2>
      <div class="score-content">
        <div class="score-main">
          <div class="score-number">
            <span class="big-number">{{ bodyData.body_score || '-' }}</span>
            <span class="score-unit">分</span>
          </div>
          <div class="score-advice">
            BMI{{ bodyData.bmi > 24 ? '偏高' : '正常' }}，建议每周坚持运动锻炼，控制饮食摄入，保持良好的作息习惯。
          </div>
        </div>
        <div class="score-indicators">
          <div class="indicator-row">
            <div class="indicator-item">
              <span class="indicator-label">体重</span>
              <div class="indicator-content">
                <span class="indicator-value">{{ bodyData.weight ? bodyData.weight + 'KG' : '-' }}</span>
                <div class="status-indicator">
                  <span class="status-item" :class="{ active: isActive('bmi', bodyData.bmi, 'low'), low: isActive('bmi', bodyData.bmi, 'low') }">偏瘦</span>
                  <span class="status-item" :class="{ active: isActive('bmi', bodyData.bmi, 'normal'), normal: isActive('bmi', bodyData.bmi, 'normal') }">正常</span>
                  <span class="status-item" :class="{ active: isActive('bmi', bodyData.bmi, 'high'), overweight: isActive('bmi', bodyData.bmi, 'high') }">超重</span>
                  <span class="status-item" :class="{ active: isActive('bmi', bodyData.bmi, 'very_high'), overweight: isActive('bmi', bodyData.bmi, 'very_high') }">肥胖</span>
                </div>
              </div>
            </div>
            <div class="indicator-item">
              <span class="indicator-label">BMI</span>
              <div class="indicator-content">
                <span class="indicator-value">{{ bodyData.bmi || '-' }}</span>
                <div class="status-indicator">
                  <span class="status-item" :class="{ active: isActive('bmi', bodyData.bmi, 'low'), low: isActive('bmi', bodyData.bmi, 'low') }">偏低</span>
                  <span class="status-item" :class="{ active: isActive('bmi', bodyData.bmi, 'normal'), normal: isActive('bmi', bodyData.bmi, 'normal') }">标准</span>
                  <span class="status-item" :class="{ active: isActive('bmi', bodyData.bmi, 'high'), overweight: isActive('bmi', bodyData.bmi, 'high') }">偏高</span>
                  <span class="status-item" :class="{ active: isActive('bmi', bodyData.bmi, 'very_high'), overweight: isActive('bmi', bodyData.bmi, 'very_high') }">过高</span>
                </div>
              </div>
            </div>
          </div>
          <div class="indicator-row">
            <div class="indicator-item">
              <span class="indicator-label">体脂率</span>
              <div class="indicator-content">
                <span class="indicator-value">{{ bodyData.body_fat ? bodyData.body_fat + '%' : '-' }}</span>
                <div class="status-indicator">
                  <span class="status-item" :class="{ active: isActive('body_fat', bodyData.body_fat, 'low'), low: isActive('body_fat', bodyData.body_fat, 'low') }">偏瘦</span>
                  <span class="status-item" :class="{ active: isActive('body_fat', bodyData.body_fat, 'normal'), normal: isActive('body_fat', bodyData.body_fat, 'normal') }">标准</span>
                  <span class="status-item" :class="{ active: isActive('body_fat', bodyData.body_fat, 'high'), overweight: isActive('body_fat', bodyData.body_fat, 'high') }">偏胖</span>
                  <span class="status-item" :class="{ active: isActive('body_fat', bodyData.body_fat, 'very_high'), overweight: isActive('body_fat', bodyData.body_fat, 'very_high') }">肥胖</span>
                </div>
              </div>
            </div>
            <div class="indicator-item">
              <span class="indicator-label">心率</span>
              <div class="indicator-content">
                <span class="indicator-value">{{ bodyData.heart_rate ? bodyData.heart_rate + '次/分' : '-' }}</span>
                <div class="status-indicator">
                  <span class="status-item" :class="{ active: isActive('heart_rate', bodyData.heart_rate, 'low'), low: isActive('heart_rate', bodyData.heart_rate, 'low') }">心动过缓</span>
                  <span class="status-item" :class="{ active: isActive('heart_rate', bodyData.heart_rate, 'normal'), normal: isActive('heart_rate', bodyData.heart_rate, 'normal') }">正常</span>
                  <span class="status-item" :class="{ active: isActive('heart_rate', bodyData.heart_rate, 'high'), overweight: isActive('heart_rate', bodyData.heart_rate, 'high') }">心动过速</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 身体成分分析与评估指标（双列布局） -->
    <div class="double-column">
      <!-- 左侧卡片：身体成分分析 -->
      <div class="card composition-card">
        <h2 class="card-title">身体成分分析</h2>
        <div class="composition-list">
          <div class="composition-item">
            <span class="item-label">体水分量</span>
            <span class="item-value">{{ bodyData.water ? bodyData.water + 'kg' : '-' }}</span>
            <div class="status-indicator">
              <span class="status-item" :class="{ active: isActive('water', bodyData.water, 'low'), low: isActive('water', bodyData.water, 'low') }">偏低</span>
              <span class="status-item" :class="{ active: isActive('water', bodyData.water, 'normal'), normal: isActive('water', bodyData.water, 'normal') }">标准</span>
              <span class="status-item" :class="{ active: isActive('water', bodyData.water, 'high'), normal: isActive('water', bodyData.water, 'high') }">优秀</span>
            </div>
          </div>
          <div class="composition-item">
            <span class="item-label">蛋白质质量</span>
            <span class="item-value">{{ bodyData.protein ? bodyData.protein + 'kg' : '-' }}</span>
            <div class="status-indicator">
              <span class="status-item" :class="{ active: isActive('protein', bodyData.protein, 'low'), low: isActive('protein', bodyData.protein, 'low') }">不足</span>
              <span class="status-item" :class="{ active: isActive('protein', bodyData.protein, 'normal'), normal: isActive('protein', bodyData.protein, 'normal') }">标准</span>
              <span class="status-item" :class="{ active: isActive('protein', bodyData.protein, 'high'), normal: isActive('protein', bodyData.protein, 'high') }">优秀</span>
            </div>
          </div>
          <div class="composition-item">
            <span class="item-label">脂肪量</span>
            <span class="item-value">{{ bodyData.fat_mass ? bodyData.fat_mass + 'kg' : '-' }}</span>
            <div class="status-indicator">
              <span class="status-item" :class="{ active: isActive('fat_mass', bodyData.fat_mass, 'low'), low: isActive('fat_mass', bodyData.fat_mass, 'low') }">偏瘦</span>
              <span class="status-item" :class="{ active: isActive('fat_mass', bodyData.fat_mass, 'normal'), normal: isActive('fat_mass', bodyData.fat_mass, 'normal') }">标准</span>
              <span class="status-item" :class="{ active: isActive('fat_mass', bodyData.fat_mass, 'high'), overweight: isActive('fat_mass', bodyData.fat_mass, 'high') }">偏胖</span>
              <span class="status-item" :class="{ active: isActive('fat_mass', bodyData.fat_mass, 'very_high'), overweight: isActive('fat_mass', bodyData.fat_mass, 'very_high') }">肥胖</span>
            </div>
          </div>
          <div class="composition-item">
            <span class="item-label">骨盐量</span>
            <span class="item-value">{{ bodyData.bone_mass ? bodyData.bone_mass + 'kg' : '-' }}</span>
            <div class="status-indicator">
              <span class="status-item" :class="{ active: isActive('bone_mass', bodyData.bone_mass, 'low'), low: isActive('bone_mass', bodyData.bone_mass, 'low') }">不足</span>
              <span class="status-item" :class="{ active: isActive('bone_mass', bodyData.bone_mass, 'normal'), normal: isActive('bone_mass', bodyData.bone_mass, 'normal') }">标准</span>
            </div>
          </div>
          <div class="composition-item">
            <span class="item-label">肌肉量</span>
            <span class="item-value">{{ bodyData.muscle_mass ? bodyData.muscle_mass + 'kg' : '-' }}</span>
            <div class="status-indicator">
              <span class="status-item" :class="{ active: isActive('muscle_mass', bodyData.muscle_mass, 'low'), low: isActive('muscle_mass', bodyData.muscle_mass, 'low') }">不足</span>
              <span class="status-item" :class="{ active: isActive('muscle_mass', bodyData.muscle_mass, 'normal'), normal: isActive('muscle_mass', bodyData.muscle_mass, 'normal') }">标准</span>
              <span class="status-item" :class="{ active: isActive('muscle_mass', bodyData.muscle_mass, 'high'), normal: isActive('muscle_mass', bodyData.muscle_mass, 'high') }">优秀</span>
            </div>
          </div>
          <div class="composition-item">
            <span class="item-label">内脏脂肪等级</span>
            <span class="item-value">{{ bodyData.visceral_fat || '-' }}</span>
            <div class="status-indicator">
              <span class="status-item" :class="{ active: isActive('visceral_fat', bodyData.visceral_fat, 'normal'), normal: isActive('visceral_fat', bodyData.visceral_fat, 'normal') }">标准</span>
              <span class="status-item" :class="{ active: isActive('visceral_fat', bodyData.visceral_fat, 'high'), overweight: isActive('visceral_fat', bodyData.visceral_fat, 'high') }">偏高</span>
              <span class="status-item" :class="{ active: isActive('visceral_fat', bodyData.visceral_fat, 'very_high'), overweight: isActive('visceral_fat', bodyData.visceral_fat, 'very_high') }">危险</span>
            </div>
          </div>
          <div class="composition-item">
            <span class="item-label">基础代谢率</span>
            <span class="item-value">{{ bodyData.bmr ? bodyData.bmr + 'kcal' : '-' }}</span>
            <div class="status-indicator">
              <span class="status-item" :class="{ active: isActive('bmr', bodyData.bmr, 'low'), low: isActive('bmr', bodyData.bmr, 'low') }">偏低</span>
              <span class="status-item" :class="{ active: isActive('bmr', bodyData.bmr, 'normal'), normal: isActive('bmr', bodyData.bmr, 'normal') }">达标</span>
              <span class="status-item" :class="{ active: isActive('bmr', bodyData.bmr, 'high'), normal: isActive('bmr', bodyData.bmr, 'high') }">优秀</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧卡片：评估指标 -->
      <div class="card assessment-card">
        <h2 class="card-title">评估指标</h2>
        <div class="assessment-content">
          <!-- 身体形态 -->
          <div class="body-shape">
            <div class="shape-left">
              <div class="body-silhouette">
                <div class="scan-point top-left"></div>
                <div class="scan-point top-right"></div>
                <div class="scan-point bottom-left"></div>
                <div class="scan-point bottom-right"></div>
                <div class="silhouette-icon">{{ userInfo.gender === 'female' ? '♀' : '♂' }}</div>
              </div>
              <div class="shape-type">{{ currentBodyShapeIndex >= 0 ? bodyShapeTypes[currentBodyShapeIndex].name : '未知' }}</div>
            </div>
            <div class="shape-right">
              <div class="coordinate-chart">
                <div class="chart-axis x-axis">
                  <span>{{ userInfo.gender === 'female' ? '20%' : '10%' }}</span>
                  <span>{{ userInfo.gender === 'female' ? '30%' : '20%' }}</span>
                </div>
                <div class="chart-axis y-axis">
                  <span>18.5</span>
                  <span>24.0</span>
                </div>
                <div class="chart-grid">
                  <div 
                    v-for="(type, index) in bodyShapeTypes" 
                    :key="index"
                    class="chart-cell"
                    :class="{ 
                      active: index === currentBodyShapeIndex,
                      [type.status]: index === currentBodyShapeIndex
                    }"
                  >
                    {{ type.name }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 其他指标 -->
          <div class="other-indicators">
            <div class="indicator-pair">
              <span class="pair-label">腰臀比</span>
              <div class="pair-right">
                <span class="pair-value">{{ bodyData.whr || '-' }}</span>
                <span v-if="bodyData.whr" class="mini-tag" :class="evaluateIndicator('whr', bodyData.whr)">
                  {{ evaluateIndicator('whr', bodyData.whr) === 'normal' ? '标准' : (evaluateIndicator('whr', bodyData.whr) === 'low' ? '优秀' : '偏高') }}
                </span>
              </div>
            </div>
            <div class="indicator-pair">
              <span class="pair-label">身体年龄</span>
              <div class="pair-right">
                <span class="pair-value">{{ bodyData.body_age || '-' }}</span>
                <span v-if="bodyData.body_age" class="mini-tag" :class="evaluateIndicator('body_age', bodyData.body_age)">
                  {{ evaluateIndicator('body_age', bodyData.body_age) === 'normal' ? '标准' : (evaluateIndicator('body_age', bodyData.body_age) === 'low' ? '年轻' : '偏大') }}
                </span>
              </div>
            </div>
            <div class="indicator-pair">
              <span class="pair-label">骨骼肌指数</span>
              <span class="pair-value">{{ bodyData.limbs_skeletal_muscle_index || '-' }}</span>
            </div>
            <div class="indicator-pair">
              <span class="pair-label">建议热量摄入</span>
              <span class="pair-value">{{ bodyData.recommended_calories_intake ? bodyData.recommended_calories_intake + 'kcal' : '-' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { getLatestWeightData } from '@/api/external-data'
import { useUserStore } from '@/stores/user'
import dayjs from 'dayjs'
import { ElMessage } from 'element-plus'
import bodyOutlineImg from '@/assets/body-outline.png'

const userStore = useUserStore()
const loading = ref(false)
const bodyData = ref(null)

// 获取用户信息
const userInfo = computed(() => userStore.userInfo || {})

// 格式化日期
const formatDate = (date) => {
  return date ? dayjs(date).format('YYYY-MM-DD') : '-'
}

// 身体体型定义
const bodyShapeTypes = [
  { name: '消瘦型', status: 'low' },
  { name: '标准型', status: 'normal' },
  { name: '肌肉型', status: 'normal' },
  { name: '隐性消瘦', status: 'low' },
  { name: '健康型', status: 'normal' },
  { name: '运动员型', status: 'normal' },
  { name: '隐性肥胖', status: 'overweight' },
  { name: '偏胖型', status: 'overweight' },
  { name: '肥胖', status: 'overweight' }
]

// 计算当前体型
const currentBodyShapeIndex = computed(() => {
  if (!bodyData.value) return -1
  
  const bmi = bodyData.value.bmi || 0
  const fat = bodyData.value.body_fat || 0
  const gender = userInfo.value.gender || 'male'
  
  // BMI Level (0: <18.5, 1: 18.5-24, 2: >24)
  let bmiLevel = 0
  if (bmi < 18.5) bmiLevel = 0
  else if (bmi < 24) bmiLevel = 1
  else bmiLevel = 2
  
  // Fat Level (0: Low, 1: Normal, 2: High)
  let fatLevel = 0
  if (gender === 'female') {
     // 女性: <20% 偏低, 20-30% 正常, >30% 偏高
     if (fat < 20) fatLevel = 0
     else if (fat < 30) fatLevel = 1
     else fatLevel = 2
  } else {
     // 男性: <10% 偏低, 10-20% 正常, >20% 偏高
     if (fat < 10) fatLevel = 0
     else if (fat < 20) fatLevel = 1
     else fatLevel = 2
  }
  
  // Grid Index = Fat Level * 3 + BMI Level
  return fatLevel * 3 + bmiLevel
})

// 指标评估逻辑
const evaluateIndicator = (type, value) => {
  if (value === null || value === undefined) return null
  
  const gender = userInfo.value.gender || 'male' // 默认为男性
  const weight = bodyData.value?.weight || 0
  const height = userInfo.value.height || 170
  const age = userInfo.value.age || 30
  
  // 辅助函数：计算百分比
  const getRate = (val) => weight > 0 ? (val / weight * 100) : 0

  switch (type) {
    case 'weight': // 体重（使用BMI评估）
    case 'bmi':
      // BMI标准：<18.5 偏瘦, 18.5-24 正常, 24-28 超重, >28 肥胖
      if (value < 18.5) return 'low'
      if (value < 24) return 'normal'
      if (value < 28) return 'high'
      return 'very_high'

    case 'body_fat': // 体脂率 %
      // 女性标准：20-30% 正常
      // 男性标准：10-20% 正常
      if (gender === 'female') {
        if (value < 20) return 'low'
        if (value < 30) return 'normal'
        if (value < 35) return 'high'
        return 'very_high'
      } else {
        if (value < 10) return 'low'
        if (value < 20) return 'normal'
        if (value < 25) return 'high'
        return 'very_high'
      }

    case 'heart_rate': // 心率
      // 正常静息心率：60-100次/分
      if (value < 60) return 'low'
      if (value <= 100) return 'normal'
      return 'high'

    case 'water': // 水分率 % (输入可能是kg，需转换)
      // 如果输入值大于 30，假设是 kg，转换为 %
      let waterRate = value
      if (value > 30 && weight > 0) {
        waterRate = (value / weight) * 100
      }
      
      // 女性标准：45-60% 正常
      // 男性标准：55-65% 正常
      if (gender === 'female') {
        if (waterRate < 45) return 'low'
        if (waterRate <= 60) return 'normal'
        return 'high'
      } else {
        if (waterRate < 55) return 'low'
        if (waterRate <= 65) return 'normal'
        return 'high'
      }

    case 'protein': // 蛋白质率 %
      // 同上，如果是kg则转换
      let proteinRate = value
      if (value > 5 && weight > 0) {
        proteinRate = (value / weight) * 100
      }
      
      // 一般标准：16-20% 正常
      if (proteinRate < 16) return 'low'
      if (proteinRate <= 20) return 'normal'
      return 'high'

    case 'fat_mass': // 脂肪量
      // 建议直接使用体脂率评估
      return evaluateIndicator('body_fat', bodyData.value?.body_fat)

    case 'bone_mass': // 骨量 (简易标准)
      // 女性 < 1.8kg 不足
      // 男性 < 2.5kg 不足
      if (gender === 'female') {
        if (value < 1.8) return 'low'
        return 'normal'
      } else {
        if (value < 2.5) return 'low'
        return 'normal'
      }

    case 'muscle_mass': // 肌肉率 %
      let muscleRate = value
      if (value > 30 && weight > 0) {
        muscleRate = (value / weight) * 100
      }
      
      // 女性标准：30-50%
      // 男性标准：40-60%
      if (gender === 'female') {
        if (muscleRate < 30) return 'low'
        if (muscleRate <= 50) return 'normal'
        return 'high'
      } else {
        if (muscleRate < 40) return 'low'
        if (muscleRate <= 60) return 'normal'
        return 'high'
      }

    case 'visceral_fat': // 内脏脂肪等级
      // 1-9 正常, 10-14 偏高, >=15 危险
      if (value < 10) return 'normal'
      if (value < 15) return 'high'
      return 'very_high'

    case 'bmr': // 基础代谢率
      // 使用 Mifflin-St Jeor 公式计算标准 BMR
      let standardBmr = 0
      if (gender === 'male') {
        standardBmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
      } else {
        standardBmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
      }
      
      // 允许 ±10% 的误差
      if (value < standardBmr * 0.9) return 'low' // 偏低
      if (value > standardBmr * 1.1) return 'high' // 优
      return 'normal' // 达标

    case 'whr': // 腰臀比
      // 男性 > 0.9 肥胖
      // 女性 > 0.85 肥胖
      if (gender === 'female') {
        if (value < 0.8) return 'low'
        if (value <= 0.85) return 'normal'
        return 'high'
      } else {
        if (value < 0.85) return 'low'
        if (value <= 0.9) return 'normal'
        return 'high'
      }

    case 'body_age': // 身体年龄
      // 与实际年龄比较
      const diff = value - age
      if (diff < -2) return 'low' // 年轻 (优)
      if (diff <= 2) return 'normal' // 标准
      return 'high' // 偏大

    default:
      return 'normal'
  }
}

// 辅助函数：判断是否激活
const isActive = (type, value, targetLevel) => {
  const currentLevel = evaluateIndicator(type, value)
  return currentLevel === targetLevel
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const data = await getLatestWeightData({ data_source: 'xiaomi_sport' })
    if (data) {
      bodyData.value = data
    } else {
      ElMessage.warning('暂无体重数据，请先同步数据')
    }
  } catch (error) {
    console.error('加载体重数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.body-composition-report {
  background-color: #f5f7fa;
  min-height: 100vh;
  padding: 15px;
  font-family: 'PingFang SC', 'Source Han Sans', sans-serif;
}

.no-data {
  background: white;
  border-radius: 16px;
  padding: 60px 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.page-header {
  text-align: center;
  margin-bottom: 15px;
  background: white;
  border-radius: 12px;
  padding: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.main-title {
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 12px 0;
}

.user-info {
  display: flex;
  justify-content: center;
  gap: 20px;
  font-size: 13px;
  color: #666;
  flex-wrap: wrap;
}

.user-info span {
  padding: 4px 12px;
  background: #F7F8FA;
  border-radius: 20px;
  font-weight: 500;
}

.card {
  background-color: #FFFFFF;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  padding: 15px;
  margin-bottom: 15px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
}

.card-title {
  font-size: 16px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #667eea;
  display: inline-block;
}

/* 身体指标得分卡片 */
.score-card .card-title {
  margin-bottom: 12px;
}

.score-content {
  display: flex;
  flex-direction: column;
}

.score-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #EEEEEE;
}

.score-number {
  position: relative;
}

.big-number {
  font-size: 48px;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.score-unit {
  font-size: 14px;
  color: #999;
  position: absolute;
  bottom: 10px;
  right: -25px;
  font-weight: 600;
}

.score-advice {
  font-size: 14px;
  color: #333333;
  line-height: 1.5;
  max-width: 60%;
}

.score-indicators {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.indicator-row {
  display: flex;
  justify-content: space-between;
}

.indicator-item {
  flex: 1;
  margin-right: 15px;
}

.indicator-item:last-child {
  margin-right: 0;
}

.indicator-label {
  font-size: 13px;
  color: #333333;
  display: block;
  margin-bottom: 4px;
}

.indicator-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.indicator-value {
  font-size: 16px;
  font-weight: bold;
  color: #000000;
  white-space: nowrap;
}

.status-indicator {
  display: inline-flex;
  gap: 5px;
  align-items: center;
}

.status-item {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  background-color: #EEEEEE;
  color: #888888;
  position: relative;
}

.status-item.active {
  color: #FFFFFF;
}

.status-item.active.overweight {
  background: linear-gradient(135deg, #FF6B6B, #FFB443);
  box-shadow: 0 4px 12px rgba(255, 180, 67, 0.4);
}

.status-item.active.normal {
  background: linear-gradient(135deg, #10B981, #34D399);
  box-shadow: 0 4px 12px rgba(52, 211, 153, 0.4);
}

.status-item.active.low {
  background: linear-gradient(135deg, #3B82F6, #60A5FA);
  box-shadow: 0 4px 12px rgba(96, 165, 250, 0.4);
}

.status-item.active::before {
  content: '';
  position: absolute;
  top: -6px;
  left: 50%;
  transform: translateX(-50%);
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-bottom: 6px solid currentColor;
}

/* 双列布局 */
.double-column {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
}

.double-column .card {
  flex: 1;
  margin-bottom: 0;
}

/* 身体成分分析 */
.composition-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.composition-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s ease;
}

.composition-item:hover {
  background-color: #fafafa;
  border-radius: 8px;
  padding-left: 8px;
  padding-right: 8px;
}

.composition-item:last-child {
  border-bottom: none;
}

.item-label {
  font-size: 13px;
  color: #333333;
  flex: 1;
  text-align: left;
}

.item-value {
  font-size: 14px;
  font-weight: bold;
  color: #000000;
  text-align: center;
  min-width: 80px;
}

.status-indicator {
  display: flex;
  gap: 5px;
  flex: 1;
  justify-content: flex-end;
}

/* 评估指标 */
.assessment-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.body-shape {
  display: flex;
  gap: 15px;
  padding-bottom: 12px;
  border-bottom: 1px solid #EEEEEE;
}

.shape-left {
  flex: 1;
  text-align: center;
}

.body-silhouette {
  width: 80px;
  height: 120px;
  background-color: #EEEEEE;
  border-radius: 8px;
  position: relative;
  margin: 0 auto 8px;
}

.scan-point {
  position: absolute;
  width: 6px;
  height: 6px;
  background-color: #888888;
}

.scan-point.top-left {
  top: 8px;
  left: 8px;
}

.scan-point.top-right {
  top: 8px;
  right: 8px;
}

.scan-point.bottom-left {
  bottom: 8px;
  left: 8px;
}

.scan-point.bottom-right {
  bottom: 8px;
  right: 8px;
}

.silhouette-icon {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 36px;
  color: #888888;
}

.shape-type {
  font-size: 13px;
  color: #333333;
}

.shape-right {
  flex: 2;
}

.coordinate-chart {
  position: relative;
  width: 100%;
  height: 140px; /* 增加高度以容纳X轴标签 */
  background-color: #FAFAFA;
  border-radius: 8px;
  padding: 10px 10px 25px 35px; /* 上 右 下 左 padding，给坐标轴留空间 */
  box-sizing: border-box;
}

.chart-axis {
  position: absolute;
  color: #888888;
  font-size: 11px;
}

.chart-axis.x-axis {
  bottom: 5px; /* 距离底部5px */
  left: 35px; /* 对应 grid 的 left padding */
  width: calc(100% - 45px); /* 总宽度减去左padding(35)和右padding(10) */
  display: flex;
  justify-content: space-evenly; /* 均匀分布，对齐网格线 */
  padding: 0;
}

.chart-axis.y-axis {
  top: 10px; /* 对应 grid 的 top padding */
  left: 5px; /* 靠左显示 */
  height: calc(100% - 35px); /* 总高度减去上padding(10)和下padding(25) */
  display: flex;
  flex-direction: column;
  justify-content: space-evenly; /* 均匀分布 */
  padding: 0;
  width: 30px; /* 限制宽度 */
  align-items: flex-end; /* 右对齐 */
}

.chart-grid {
  position: relative; /* 相对定位，由 padding 决定位置 */
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(3, 1fr);
  gap: 2px;
}

.chart-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #888888;
  background-color: #FFFFFF;
  border-radius: 4px;
}

.chart-cell.active.overweight {
  background-color: #FFB443;
  color: #FFFFFF;
  font-weight: bold;
}

.chart-cell.active.normal {
  background-color: #10B981;
  color: #FFFFFF;
  font-weight: bold;
}

.chart-cell.active.low {
  background-color: #3B82F6;
  color: #FFFFFF;
  font-weight: bold;
}

.other-indicators {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.indicator-pair {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
}

.pair-label {
  font-size: 13px;
  color: #333333;
}

.pair-value {
  font-size: 14px;
  font-weight: bold;
  color: #000000;
}

/* 节段分析 */
.legend {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #EEEEEE;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  color: #333333;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-color.low {
  background: linear-gradient(135deg, #3B82F6, #60A5FA);
  box-shadow: 0 2px 8px rgba(96, 165, 250, 0.3);
}

.legend-color.normal {
  background: linear-gradient(135deg, #10B981, #34D399);
  box-shadow: 0 2px 8px rgba(52, 211, 153, 0.3);
}

.legend-color.overweight {
  background: linear-gradient(135deg, #FF6B6B, #FFB443);
  box-shadow: 0 2px 8px rgba(255, 180, 67, 0.3);
}

.segment-content {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.segment-visual {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 16px;
  padding: 20px;
}

.body-image-container {
  position: relative;
  width: 280px;
  height: 480px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.body-outline-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.15));
  transition: transform 0.3s ease;
}

.pair-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.mini-tag {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  color: white;
  background-color: #ccc;
}

.mini-tag.normal {
  background-color: #10B981;
}

.mini-tag.low {
  background-color: #3B82F6; /* Blue for low/excellent */
}

.mini-tag.high {
  background-color: #FFB443; /* Orange for high */
}

.mini-tag.very_high {
  background-color: #FF6B6B; /* Red for very high */
}

.body-outline-image:hover {
  transform: scale(1.03);
}

.data-overlays {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.data-marker {
  position: absolute;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  pointer-events: auto;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(4px);
}

.data-marker:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
}

.data-marker .marker-value {
  display: block;
  white-space: nowrap;
}

/* 各部位标注位置 */
.data-marker.left-arm {
  top: 25%;
  left: 5%;
}

.data-marker.right-arm {
  top: 25%;
  right: 5%;
}

.data-marker.trunk {
  top: 35%;
  left: 50%;
  transform: translateX(-50%);
}

.data-marker.left-leg {
  top: 60%;
  left: 20%;
}

.data-marker.right-leg {
  top: 60%;
  right: 20%;
}

.body-model {
  width: 240px;
  height: 500px;
  filter: drop-shadow(0 8px 16px rgba(0, 0, 0, 0.15));
  transition: transform 0.3s ease;
}

.body-model:hover {
  transform: scale(1.05);
}

.segment-data {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.data-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.data-label {
  font-size: 16px;
  color: #333333;
}

.data-value {
  font-size: 16px;
  font-weight: bold;
}

.data-value.low {
  color: #3B82F6;
  text-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
}

.data-value.normal {
  color: #10B981;
  text-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
}

.data-value.overweight {
  color: #FF6B6B;
  text-shadow: 0 2px 4px rgba(255, 107, 107, 0.2);
}

.balance-assessment {
  display: flex;
  justify-content: space-around;
  padding-top: 15px;
  border-top: 1px solid #EEEEEE;
}

.balance-item {
  font-size: 14px;
  color: #333333;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .double-column {
    flex-direction: column;
  }
  
  .body-shape {
    flex-direction: column;
  }
  
  .shape-right {
    margin-top: 20px;
  }
  
  .segment-content {
    flex-direction: column;
  }
  
  .indicator-row {
    flex-direction: column;
    gap: 15px;
  }
  
  .indicator-item {
    margin-right: 0;
  }
  
  .score-main {
    flex-direction: column;
    text-align: center;
  }
  
  .score-advice {
    max-width: 100%;
    margin-top: 15px;
  }
  
  .other-indicators {
    grid-template-columns: 1fr;
  }
}
</style>