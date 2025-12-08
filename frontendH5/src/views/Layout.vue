<template>
  <div class="layout">
    <router-view class="content" />
    <van-tabbar v-model="active" route fixed placeholder>
      <van-tabbar-item to="/home" icon="home-o">首页</van-tabbar-item>
      <van-tabbar-item to="/record" icon="records">记录</van-tabbar-item>
      <van-tabbar-item to="/trend" icon="chart-trending-o">趋势</van-tabbar-item>
      <van-tabbar-item to="/profile" icon="user-o">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const active = ref(0)

// 根据路由更新tabbar激活状态
const tabMap = {
  '/home': 0,
  '/record': 1,
  '/trend': 2,
  '/profile': 3
}

watch(() => route.path, (path) => {
  active.value = tabMap[path] ?? 0
}, { immediate: true })
</script>

<style scoped>
.layout {
  width: 100%;
  min-height: 100vh;
  background: #f7f8fa;
}

.content {
  min-height: calc(100vh - 50px);
  padding-bottom: 50px;
}
</style>
