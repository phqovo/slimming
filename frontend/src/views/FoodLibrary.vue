<template>
  <div class="food-library">
    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input
        v-model="keyword"
        placeholder="搜索食物名称（如：鸡胸肉、米饭）"
        class="search-input"
        clearable
        @keyup.enter="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-button type="primary" @click="handleSearch" :loading="loading">
        搜索
      </el-button>
    </div>

    <!-- 搜索结果 -->
    <div v-if="searchResults.length > 0" class="results-container">
      <div class="results-header" v-if="sourceText">
        <span>{{ sourceText }}</span>
        <span class="result-count">共 {{ searchResults.length }} 条结果</span>
      </div>
      
      <div class="food-grid" :class="{ 'animate-scroll': showAnimation }">
        <div
          v-for="(food, index) in searchResults"
          :key="food.id || food.external_id"
          class="food-card"
          :class="{ 'card-animate': showAnimation }"
          :style="showAnimation ? { animationDelay: `${index * 0.05}s` } : {}"
          @click="viewDetail(food)"
        >
          <div class="food-image">
            <img :src="food.image_url || defaultImage" :alt="food.name" />
          </div>
          <div class="food-info">
            <h3 class="food-name">{{ food.name }}</h3>
            <p class="food-calories">{{ food.calories }} 千卡/100g</p>
            <el-tag v-if="food.category" size="small" type="info">
              {{ food.category }}
            </el-tag>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <el-empty
      v-else-if="!loading && searched"
      description="未找到相关食物"
    />

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      :title="currentFood?.name"
      width="600px"
      class="food-detail-dialog"
    >
      <div v-if="currentFood" class="detail-content">
        <div class="detail-image">
          <img :src="currentFood.image_url || defaultImage" :alt="currentFood.name" />
        </div>
        
        <div class="nutrition-info">
          <h3>营养成分表 (每100g)</h3>
          <el-row :gutter="20" class="nutrition-grid">
            <el-col :span="12">
              <div class="nutrition-item">
                <span class="label">热量</span>
                <span class="value">{{ currentFood.calories }} 千卡</span>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="nutrition-item">
                <span class="label">蛋白质</span>
                <span class="value">{{ currentFood.protein || 0 }} g</span>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="nutrition-item">
                <span class="label">碳水化合物</span>
                <span class="value">{{ currentFood.carbs || 0 }} g</span>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="nutrition-item">
                <span class="label">脂肪</span>
                <span class="value">{{ currentFood.fat || 0 }} g</span>
              </div>
            </el-col>
          </el-row>
          
          <div class="detail-meta">
            <el-tag v-if="currentFood.category">{{ currentFood.category }}</el-tag>
            <el-tag type="info">{{ currentFood.source === 'local' ? '本地数据' : '在线数据' }}</el-tag>
          </div>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { searchFoodOnline, getFoodDetail, getLocalFoods } from '@/api/food'
import { ElMessage } from 'element-plus'

const keyword = ref('')
const loading = ref(false)
const searched = ref(false)
const searchResults = ref([])
const sourceText = ref('')
const defaultImage = '/default-food.png'
const showAnimation = ref(false)

const detailVisible = ref(false)
const currentFood = ref(null)

// 页面加载时获取随机本地数据
onMounted(async () => {
  await loadInitialData()
})

const loadInitialData = async () => {
  try {
    loading.value = true
    // 获取本地食物库的随机20条数据
    const res = await getLocalFoods({ page: 1, page_size: 20, random: true })
    if (res.items && res.items.length > 0) {
      searchResults.value = res.items
      // 启动动画效果
      showAnimation.value = true
      // 3秒后关闭动画(避免后续操作受影响)
      setTimeout(() => {
        showAnimation.value = false
      }, 3000)
    }
  } catch (error) {
    console.error('加载初始数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 搜索食物
const handleSearch = async () => {
  if (!keyword.value.trim()) {
    ElMessage.warning('请输入食物名称')
    return
  }
  
  loading.value = true
  searched.value = true
  showAnimation.value = false // 搜索时关闭动画
  
  try {
    const res = await searchFoodOnline(keyword.value)
    searchResults.value = res.data
    sourceText.value = `共查询到 ${res.data.length} 条数据`
    
    if (res.data.length === 0) {
      ElMessage.info('未找到相关食物')
    }
  } catch (error) {
    ElMessage.error('搜索失败：' + (error.message || '未知错误'))
    searchResults.value = []
  } finally {
    loading.value = false
  }
}

// 查看详情
const viewDetail = (food) => {
  // 直接使用搜索接口返回的数据显示详情
  currentFood.value = food
  detailVisible.value = true
}
</script>

<style scoped>
.food-library {
  padding: 20px;
  min-height: calc(100vh - 120px);
}

.search-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 30px;
}

.search-input {
  max-width: 600px;
}

.results-container {
  margin-top: 24px;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-size: 14px;
  color: #606266;
}

.result-count {
  color: #909399;
}

.food-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.food-card {
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  transition: all 0.3s;
}

.food-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
}

/* 初始加载动画效果 */
.card-animate {
  opacity: 0;
  transform: translateY(30px) scale(0.95);
  animation: cardSlideIn 0.6s ease-out forwards;
}

@keyframes cardSlideIn {
  0% {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  60% {
    transform: translateY(-5px) scale(1.02);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 整体网格滚动效果 */
.animate-scroll {
  animation: gridFadeIn 0.5s ease-out;
}

@keyframes gridFadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.food-image {
  width: 100%;
  height: 150px;
  overflow: hidden;
  background: #f5f7fa;
}

.food-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.food-info {
  padding: 12px;
}

.food-name {
  font-size: 16px;
  font-weight: 500;
  margin: 0 0 8px;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.food-calories {
  font-size: 14px;
  color: #409eff;
  font-weight: 600;
  margin: 8px 0;
}

/* 详情对话框 */
.detail-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-image {
  width: 100%;
  height: 200px;
  border-radius: 12px;
  overflow: hidden;
  background: #f5f7fa;
}

.detail-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.nutrition-info h3 {
  font-size: 18px;
  margin-bottom: 16px;
  color: #303133;
}

.nutrition-grid {
  margin-bottom: 20px;
}

.nutrition-item {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.nutrition-item .label {
  font-size: 14px;
  color: #606266;
}

.nutrition-item .value {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.detail-meta {
  display: flex;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}
</style>
