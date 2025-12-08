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
                  <span class="status-item">偏瘦</span>
                  <span class="status-item">正常</span>
                  <span class="status-item" :class="{ active: bodyData.weight, overweight: bodyData.weight }">超重</span>
                  <span class="status-item">肥胖</span>
                </div>
              </div>
            </div>
            <div class="indicator-item">
              <span class="indicator-label">BMI</span>
              <div class="indicator-content">
                <span class="indicator-value">{{ bodyData.bmi || '-' }}</span>
                <div class="status-indicator">
                  <span class="status-item">偏低</span>
                  <span class="status-item">标准</span>
                  <span class="status-item" :class="{ active: bodyData.bmi > 24, overweight: bodyData.bmi > 24 }">偏高</span>
                  <span class="status-item">过高</span>
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
                  <span class="status-item">偏瘦</span>
                  <span class="status-item">标准</span>
                  <span class="status-item">偏胖</span>
                  <span class="status-item" :class="{ active: bodyData.body_fat > 25, overweight: bodyData.body_fat > 25 }">肥胖</span>
                </div>
              </div>
            </div>
            <div class="indicator-item">
              <span class="indicator-label">心率</span>
              <div class="indicator-content">
                <span class="indicator-value">{{ bodyData.heart_rate ? bodyData.heart_rate + '次/分' : '-' }}</span>
                <div class="status-indicator">
                  <span class="status-item" :class="{ active: bodyData.heart_rate < 60, low: bodyData.heart_rate < 60 }">心动过缓</span>
                  <span class="status-item" :class="{ active: bodyData.heart_rate >= 60 && bodyData.heart_rate <= 100, normal: bodyData.heart_rate >= 60 && bodyData.heart_rate <= 100 }">正常</span>
                  <span class="status-item" :class="{ active: bodyData.heart_rate > 100, overweight: bodyData.heart_rate > 100 }">心动过速</span>
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
              <span class="status-item" :class="{ active: bodyData.water < 40, low: bodyData.water < 40 }">不足</span>
              <span class="status-item" :class="{ active: bodyData.water >= 40 && bodyData.water <= 50, normal: bodyData.water >= 40 && bodyData.water <= 50 }">标准</span>
              <span class="status-item" :class="{ active: bodyData.water > 50, normal: bodyData.water > 50 }">优</span>
            </div>
          </div>
          <div class="composition-item">
            <span class="item-label">蛋白质质量</span>
            <span class="item-value">{{ bodyData.protein ? bodyData.protein + 'kg' : '-' }}</span>
            <div class="status-indicator">
              <span class="status-item" :class="{ active: bodyData.protein < 10, low: bodyData.protein < 10 }">偏低</span>
              <span class="status-item" :class="{ active: bodyData.protein >= 10 && bodyData.protein <= 15, normal: bodyData.protein >= 10 && bodyData.protein <= 15 }">正常</span>
              <span class="status-item" :class="{ active: bodyData.protein > 15, overweight: bodyData.protein > 15 }">偏高</span>
            </div>
          </div>
          <div class="composition-item">
            <span class="item-label">脂肪量</span>
            <span class="item-value">{{ bodyData.fat_mass ? bodyData.fat_mass + 'kg' : '-' }}</span>
            <div class="status-indicator">
              <span class="status-item">偏瘦</span>
              <span class="status-item">标准</span>
              <span class="status-item">偏胖</span>
              <span class="status-item" :class="{ active: bodyData.fat_mass > 20, overweight: bodyData.fat_mass > 20 }">肥胖</span>
            </div>
          </div>
          <div class="composition-item">
            <span class="item-label">骨盐量</span>
            <span class="item-value">{{ bodyData.bone_mass ? bodyData.bone_mass + 'kg' : '-' }}</span>
            <div class="status-indicator">
              <span class="status-item">不足</span>
              <span class="status-item" :class="{ active: bodyData.bone_mass, normal: bodyData.bone_mass }">正常</span>
              <span class="status-item">正常</span>
            </div>
          </div>
          <div class="composition-item">
            <span class="item-label">肌肉量</span>
            <span class="item-value">{{ bodyData.muscle_mass ? bodyData.muscle_mass + 'kg' : '-' }}</span>
            <div class="status-indicator">
              <span class="status-item">偏低</span>
              <span class="status-item">正常</span>
              <span class="status-item" :class="{ active: bodyData.muscle_mass > 50, normal: bodyData.muscle_mass > 50 }">偏高</span>
            </div>
          </div>
          <div class="composition-item">
            <span class="item-label">内脏脂肪等级</span>
            <span class="item-value">{{ bodyData.visceral_fat || '-' }}</span>
            <div class="status-indicator">
              <span class="status-item" :class="{ active: bodyData.visceral_fat < 5, normal: bodyData.visceral_fat < 5 }">健康</span>
              <span class="status-item" :class="{ active: bodyData.visceral_fat >= 5 && bodyData.visceral_fat < 10, normal: bodyData.visceral_fat >= 5 && bodyData.visceral_fat < 10 }">警戒</span>
              <span class="status-item" :class="{ active: bodyData.visceral_fat >= 10, overweight: bodyData.visceral_fat >= 10 }">稍多</span>
              <span class="status-item">危险</span>
            </div>
          </div>
          <div class="composition-item">
            <span class="item-label">基础代谢率</span>
            <span class="item-value">{{ bodyData.bmr ? bodyData.bmr + 'kcal' : '-' }}</span>
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
                <div class="silhouette-icon">♂</div>
              </div>
              <div class="shape-type">倒三角型</div>
            </div>
            <div class="shape-right">
              <div class="coordinate-chart">
                <div class="chart-axis x-axis">
                  <span>10%</span>
                  <span>20%</span>
                </div>
                <div class="chart-axis y-axis">
                  <span>18.5</span>
                  <span>24.0</span>
                </div>
                <div class="chart-grid">
                  <div class="chart-cell">消瘦型</div>
                  <div class="chart-cell">标准型</div>
                  <div class="chart-cell">肌肉型</div>
                  <div class="chart-cell">隐性消瘦</div>
                  <div class="chart-cell">健康型</div>
                  <div class="chart-cell">运动员型</div>
                  <div class="chart-cell">隐性肥胖</div>
                  <div class="chart-cell">偏胖型</div>
                  <div class="chart-cell active overweight">肥胖</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 其他指标 -->
          <div class="other-indicators">
            <div class="indicator-pair">
              <span class="pair-label">腰臀比</span>
              <span class="pair-value">{{ bodyData.whr || '-' }}</span>
            </div>
            <div class="indicator-pair">
              <span class="pair-label">身体年龄</span>
              <span class="pair-value">{{ bodyData.body_age || '-' }}</span>
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

// 根据数值获取颜色（脂肪）
const getColor = (value, type = 'fat') => {
  if (!value) return '#E8E8E8'
  
  if (type === 'fat') {
    // 脂肪：值越高越橙色
    if (value < 1.5) return '#60A5FA'  // 偏低 - 蓝色
    if (value >= 1.5 && value < 3) return '#34D399'  // 正常 - 绿色
    return '#FFB443'  // 偏高 - 橙色
  } else {
    // 肌肉：值越高越绿色
    if (value < 3) return '#60A5FA'  // 偏低 - 蓝色
    if (value >= 3 && value < 8) return '#34D399'  // 正常 - 绿色
    return '#10B981'  // 偏高 - 深绿色
  }
}

// 获取躯干颜色
const getTrunkColor = (value, type = 'fat') => {
  if (!value) return '#E8E8E8'
  
  if (type === 'fat') {
    if (value < 8) return '#60A5FA'
    if (value >= 8 && value < 12) return '#34D399'
    return '#FFB443'
  } else {
    if (value < 20) return '#60A5FA'
    if (value >= 20 && value < 30) return '#34D399'
    return '#10B981'
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
  height: 120px;
  background-color: #FAFAFA;
  border-radius: 8px;
}

.chart-axis {
  position: absolute;
  display: flex;
  color: #888888;
  font-size: 12px;
}

.chart-axis.x-axis {
  bottom: 0;
  left: 30px;
  width: calc(100% - 30px);
  justify-content: space-between;
  padding: 0 10px;
}

.chart-axis.y-axis {
  top: 10px;
  left: 0;
  height: calc(100% - 10px);
  flex-direction: column;
  justify-content: space-between;
  padding: 10px 0;
}

.chart-grid {
  position: absolute;
  top: 10px;
  left: 30px;
  width: calc(100% - 40px);
  height: calc(100% - 20px);
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