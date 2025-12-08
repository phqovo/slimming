# 体重管理系统 - 移动端H5

基于 Vue 3 + Vant 4 的移动端H5应用

## 📱 功能特性

### 核心功能
- ✅ 手机号验证码登录/注册
- ✅ 体重记录与趋势分析
- ✅ 饮食记录（早中晚餐+加餐）
- ✅ 运动记录
- ✅ 数据可视化（ECharts图表）
- ✅ 个人中心设置

### 页面结构
```
/login          - 登录页面
/home           - 首页（今日数据汇总 + 快捷入口）
/record         - 记录页面（饮食/运动/体重记录）
/trend          - 趋势页面（体重&热量趋势图）
/profile        - 个人中心
/weight/add     - 添加体重
/diet/add       - 添加饮食
/exercise/add   - 添加运动
```

## 🚀 快速开始

### 安装依赖
```bash
cd frontendH5
npm install
```

### 启动开发服务器
```bash
npm run dev
```
访问：http://localhost:5174

### 构建生产版本
```bash
npm run build
```

## 🛠 技术栈

- **框架**: Vue 3 (Composition API)
- **UI组件**: Vant 4
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **HTTP客户端**: Axios
- **图表**: ECharts 5
- **构建工具**: Vite 4
- **日期处理**: Day.js

## 📂 目录结构

```
frontendH5/
├── src/
│   ├── api/              # API接口定义
│   │   ├── auth.js       # 认证
│   │   ├── user.js       # 用户
│   │   ├── weight.js     # 体重
│   │   ├── diet.js       # 饮食
│   │   ├── exercise.js   # 运动
│   │   └── home.js       # 首页数据
│   ├── assets/           # 静态资源
│   ├── components/       # 公共组件
│   ├── router/           # 路由配置
│   │   └── index.js      # 路由表（含底部Tabbar）
│   ├── stores/           # Pinia状态管理
│   │   ├── settings.js   # 设置（体重单位等）
│   │   └── user.js       # 用户信息
│   ├── utils/            # 工具函数
│   │   └── request.js    # Axios封装
│   ├── views/            # 页面组件
│   │   ├── Layout.vue    # 布局（含底部导航）
│   │   ├── Login.vue     # 登录页
│   │   ├── Home.vue      # 首页
│   │   ├── Record.vue    # 记录页
│   │   ├── Trend.vue     # 趋势页
│   │   ├── Profile.vue   # 个人中心
│   │   ├── diet/
│   │   │   └── AddDiet.vue      # 添加饮食
│   │   ├── exercise/
│   │   │   └── AddExercise.vue  # 添加运动
│   │   └── weight/
│   │       └── AddWeight.vue    # 添加体重
│   ├── App.vue           # 根组件
│   └── main.js           # 入口文件
├── index.html            # HTML模板
├── vite.config.js        # Vite配置
└── package.json          # 项目配置
```

## 🎨 UI特点

### 移动端优化
- ✅ 响应式设计，适配各种手机屏幕
- ✅ 触摸友好的交互设计
- ✅ 底部Tabbar导航
- ✅ 下拉刷新 + 上拉加载
- ✅ 适配移动端的表单组件
- ✅ 优化的图表展示

### 视觉设计
- 渐变色主题（紫色系）
- 圆角卡片设计
- 清晰的视觉层级
- 统一的色彩规范

## 🔗 与PC端的关系

### 独立性
- ✅ **完全独立的项目**，不依赖PC端代码
- ✅ 独立的端口（5174）
- ✅ 独立的UI框架（Vant vs Element Plus）
- ✅ 可独立部署

### 共享资源
- ✅ 共享同一个后端API
- ✅ 复用API接口定义（从PC端复制）
- ✅ 复用工具函数和状态管理
- ✅ 共享数据库和用户体系

## 🌐 API代理配置

开发环境：
```javascript
proxy: {
  '/health': {
    target: 'http://localhost:8000',
    changeOrigin: true
  }
}
```

生产环境：
```javascript
baseURL: 'https://piheqi.com/health/api/v1'
```

## 📱 移动端适配

### viewport配置
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black">
```

### 兼容性
- iOS Safari 10+
- Android Chrome 60+
- 微信浏览器
- 支持添加到主屏幕

## 🚀 部署

### Nginx配置示例
```nginx
server {
    listen 80;
    server_name h5.yourdomain.com;
    
    location / {
        root /path/to/frontendH5/dist;
        try_files $uri $uri/ /index.html;
    }
    
    location /health {
        proxy_pass http://localhost:8000;
    }
}
```

## 📝 开发说明

### 添加新页面
1. 在 `src/views/` 创建页面组件
2. 在 `src/router/index.js` 添加路由
3. 如需要底部导航，将路由作为 Layout 的子路由

### 调用API
```javascript
import { getDietRecords } from '@/api/diet'

const fetchData = async () => {
  const res = await getDietRecords({ page: 1, page_size: 20 })
  console.log(res)
}
```

### 状态管理
```javascript
import { useSettingsStore } from '@/stores/settings'

const settingsStore = useSettingsStore()
const unit = settingsStore.weightUnit
```

## 🎯 与PC端功能对比

| 功能 | PC端 | H5端 |
|------|------|------|
| 登录注册 | ✅ | ✅ |
| 体重记录 | ✅ | ✅ |
| 饮食记录 | ✅ | ✅ |
| 运动记录 | ✅ | ✅ |
| 数据趋势 | ✅ | ✅ |
| 个人中心 | ✅ | ✅ |
| 减肥榜 | ✅ | 🚧 待开发 |
| 食物库 | ✅ | 🚧 待开发 |
| 数据同步 | ✅ | 🚧 待开发 |
| 人体报告 | ✅ | 🚧 待开发 |
| 营养分析 | ✅ | 🚧 待开发 |

## 💡 后续优化方向

1. **功能完善**
   - [ ] 添加减肥榜H5页面
   - [ ] 添加食物库H5页面
   - [ ] 添加数据同步H5页面
   - [ ] 添加人体报告H5版本

2. **体验优化**
   - [ ] 添加骨架屏加载
   - [ ] 图片懒加载
   - [ ] 离线缓存支持
   - [ ] PWA支持

3. **性能优化**
   - [ ] 路由懒加载
   - [ ] 组件按需引入优化
   - [ ] 图片压缩优化

## 📄 License

MIT
