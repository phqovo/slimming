<template>
  <div class="leaderboard-container">
    <div class="page-header">
      <h1 class="title">
        <el-icon style="margin-right: 8px;"><TrophyBase /></el-icon>
        减肥榜
      </h1>
      <p class="subtitle">坚持就是胜利，一起见证彼此的蜕变</p>
    </div>

    <el-card class="leaderboard-card" shadow="never" v-loading="loading">
      <!-- 前三名特殊展示 -->
      <div class="podium" v-if="topThree.length > 0">
        <div 
          class="podium-item second" 
          :class="{ 'clickable': topThree[1]?.data_public }"
          v-if="topThree[1]"
          @click="handleUserClick(topThree[1])"
        >
          <div class="medal-wrapper">
            <div class="medal silver">2</div>
          </div>
          <el-avatar :size="60" :src="topThree[1].avatar || defaultAvatar" class="avatar" />
          <div class="user-name">
            {{ topThree[1].nickname || topThree[1].username }}
            <el-icon v-if="!topThree[1].data_public" class="lock-icon" title="用户未公开数据"><Lock /></el-icon>
          </div>
          <div class="weight-loss">
            <span class="number">{{ topThree[1].weight_lost }}</span>
            <span class="unit">斤</span>
          </div>
          <div class="days">{{ topThree[1].days }}天</div>
        </div>

        <div 
          class="podium-item first" 
          :class="{ 'clickable': topThree[0]?.data_public }"
          v-if="topThree[0]"
          @click="handleUserClick(topThree[0])"
        >
          <div class="medal-wrapper">
            <div class="medal gold">
              <el-icon style="font-size: 24px;"><Trophy /></el-icon>
            </div>
          </div>
          <el-avatar :size="80" :src="topThree[0].avatar || defaultAvatar" class="avatar" />
          <div class="user-name champion">
            {{ topThree[0].nickname || topThree[0].username }}
            <el-icon v-if="!topThree[0].data_public" class="lock-icon" title="用户未公开数据"><Lock /></el-icon>
          </div>
          <div class="weight-loss">
            <span class="number">{{ topThree[0].weight_lost }}</span>
            <span class="unit">斤</span>
          </div>
          <div class="days">{{ topThree[0].days }}天</div>
        </div>

        <div 
          class="podium-item third" 
          :class="{ 'clickable': topThree[2]?.data_public }"
          v-if="topThree[2]"
          @click="handleUserClick(topThree[2])"
        >
          <div class="medal-wrapper">
            <div class="medal bronze">3</div>
          </div>
          <el-avatar :size="60" :src="topThree[2].avatar || defaultAvatar" class="avatar" />
          <div class="user-name">
            {{ topThree[2].nickname || topThree[2].username }}
            <el-icon v-if="!topThree[2].data_public" class="lock-icon" title="用户未公开数据"><Lock /></el-icon>
          </div>
          <div class="weight-loss">
            <span class="number">{{ topThree[2].weight_lost }}</span>
            <span class="unit">斤</span>
          </div>
          <div class="days">{{ topThree[2].days }}天</div>
        </div>
      </div>

      <!-- 其他排名列表 -->
      <div class="ranking-list" v-if="otherRankings.length > 0">
        <div 
          class="ranking-item" 
          v-for="(item, index) in otherRankings" 
          :key="item.user_id"
          :class="{ 'is-current': item.is_current_user, 'clickable': item.data_public }"
          @click="handleUserClick(item)"
        >
          <div class="rank-number">{{ index + 4 }}</div>
          <el-avatar :size="50" :src="item.avatar || defaultAvatar" class="avatar" />
          <div class="user-info">
            <div class="user-name">
              {{ item.nickname || item.username }}
              <el-tag v-if="item.is_current_user" size="small" type="success">我</el-tag>
              <el-icon v-if="!item.data_public" class="lock-icon" title="用户未公开数据"><Lock /></el-icon>
            </div>
            <div class="user-stats">
              <span class="stat-item">
                <el-icon><TrendCharts /></el-icon>
                减重 <strong>{{ item.weight_lost }}</strong> 斤
              </span>
              <span class="stat-item">
                <el-icon><Calendar /></el-icon>
                坚持 <strong>{{ item.days }}</strong> 天
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <el-empty v-if="!loading && rankings.length === 0" description="暂无数据">
        <el-button type="primary" @click="$router.push('/weight')">开始记录体重</el-button>
      </el-empty>
    </el-card>
    
    <!-- 用户详情弹窗 -->
    <UserProfileDialog v-model="showProfileDialog" :user-id="selectedUserId" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Trophy, TrophyBase, TrendCharts, Calendar, InfoFilled, Lock } from '@element-plus/icons-vue'
import request from '@/utils/request'
import UserProfileDialog from '@/components/UserProfileDialog.vue'

const loading = ref(false)
const rankings = ref([])
const showProfileDialog = ref(false)
const selectedUserId = ref(null)
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

const topThree = computed(() => rankings.value.slice(0, 3))
const otherRankings = computed(() => rankings.value.slice(3))

onMounted(() => {
  fetchLeaderboard()
})

const fetchLeaderboard = async () => {
  loading.value = true
  try {
    const response = await request.get('/leaderboard')
    rankings.value = response.data || []
  } catch (error) {
    ElMessage.error('获取排行榜失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleUserClick = (item) => {
  if (item.data_public) {
    // 打开用户详情弹窗
    selectedUserId.value = item.user_id
    showProfileDialog.value = true
  } else {
    ElMessage.warning('该用户未公开数据，无法查看详情')
  }
}
</script>

<style scoped>
.leaderboard-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.title {
  font-size: 32px;
  font-weight: bold;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 0 10px 0;
}

.subtitle {
  font-size: 14px;
  color: #999;
  margin: 0;
}

.leaderboard-card {
  border-radius: 20px;
  overflow: hidden;
  border: none;
  background: linear-gradient(to bottom, #f8f9ff 0%, #ffffff 100%);
}

/* 前三名领奖台 */
.podium {
  display: flex;
  justify-content: center;
  align-items: flex-end;
  gap: 30px;
  padding: 40px 20px;
  background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
  border-radius: 16px;
  margin-bottom: 30px;
}

.podium-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 0 0 200px;
  padding: 20px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  position: relative;
}

.podium-item.clickable {
  cursor: pointer;
}

.podium-item.clickable:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

.podium-item.first {
  flex: 0 0 220px;
  padding: 30px 20px;
  background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
  color: white;
}

.podium-item.second {
  margin-bottom: 20px;
}

.podium-item.third {
  margin-bottom: 20px;
}

.medal-wrapper {
  position: absolute;
  top: -15px;
  left: 50%;
  transform: translateX(-50%);
}

.medal {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 18px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.medal.gold {
  background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
  color: #8b4513;
  width: 50px;
  height: 50px;
}

.medal.silver {
  background: linear-gradient(135deg, #c0c0c0 0%, #e8e8e8 100%);
  color: #666;
}

.medal.bronze {
  background: linear-gradient(135deg, #cd7f32 0%, #e8b482 100%);
  color: white;
}

.podium-item .avatar {
  margin: 20px 0 15px 0;
  border: 4px solid white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.podium-item.first .avatar {
  border-color: #ffd700;
}

.podium-item .user-name {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 10px;
  color: #333;
}

.podium-item.first .user-name {
  color: white;
  font-size: 18px;
}

.podium-item .weight-loss {
  margin-bottom: 5px;
}

.podium-item .weight-loss .number {
  font-size: 28px;
  font-weight: bold;
  color: #667eea;
}

.podium-item.first .weight-loss .number {
  font-size: 32px;
  color: white;
}

.podium-item .weight-loss .unit {
  font-size: 14px;
  color: #999;
  margin-left: 4px;
}

.podium-item.first .weight-loss .unit {
  color: rgba(255, 255, 255, 0.8);
}

.podium-item .days {
  font-size: 12px;
  color: #999;
}

.podium-item.first .days {
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
}

/* 排名列表 */
.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ranking-item {
  display: flex;
  align-items: center;
  padding: 20px;
  background: white;
  border-radius: 16px;
  border: 2px solid #f0f0f0;
  transition: all 0.3s ease;
}

.ranking-item.clickable {
  cursor: pointer;
}

.ranking-item.clickable:hover {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
  transform: translateX(5px);
}

.ranking-item.is-current {
  background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
  border-color: #667eea;
}

.rank-number {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 18px;
  margin-right: 20px;
  flex-shrink: 0;
}

.ranking-item .avatar {
  margin-right: 20px;
  flex-shrink: 0;
  border: 3px solid #f0f0f0;
}

.user-info {
  flex: 1;
}

.user-info .user-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.lock-icon {
  color: #999;
  font-size: 14px;
}

.user-stats {
  display: flex;
  gap: 20px;
  font-size: 14px;
  color: #666;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.stat-item strong {
  color: #667eea;
  font-size: 16px;
  margin: 0 2px;
}

.stat-item .el-icon {
  color: #999;
  font-size: 16px;
}

/* 响应式 */
@media (max-width: 768px) {
  .podium {
    flex-direction: column;
    align-items: center;
  }

  .podium-item.second,
  .podium-item.third {
    margin-bottom: 0;
  }

  .podium-item.first {
    order: -1;
  }

  .user-stats {
    flex-direction: column;
    gap: 8px;
  }
}
</style>
