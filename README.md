# 体重管理系统  - 减肥自用

一个功能完整的体重管理系统，帮助用户记录和管理体重、运动、饮食等健康数据，并基于AI预测未来体重趋势。前后端代码完全由ai(qoder)编写  地址： https://piheqi.com/health

## ✨ 功能特性

### 用户认证
- 📱 手机号验证码登录
- 🔐 自动注册新用户
- 🎫 JWT Token 认证
- ⚡ Redis 会话管理

### 首页功能
- 📊 每日健康数据概览
- 🍽️ 饮食记录（早中晚餐 + 加餐）
- 💧 饮水记录与进度跟踪
- 🏃 运动打卡与图片上传
- 😴 睡眠质量记录
- 📈 BMI 和基础代谢计算

### 体重趋势分析
- 📉 历史体重变化图表
- 🔮 AI 预测未来体重趋势
- 📅 支持 7天/30天/90天 预测
- 📊 置信区间展示
- 📝 完整的历史记录管理

### 个人信息
- 👤 头像上传
- 📋 个人资料编辑
- 💪 健康指标展示
- 🎯 目标体重设置

## 🛠️ 技术栈

### 后端
- **框架**: FastAPI (Python 3.8+)
- **数据库**: MySQL 8.0+
- **缓存**: Redis 6.0+
- **ORM**: SQLAlchemy
- **机器学习**: scikit-learn (线性回归预测)
- **认证**: JWT + Redis

### 前端
- **框架**: Vue 3 + Vite
- **UI组件**: Element Plus
- **状态管理**: Pinia
- **图表**: ECharts 5
- **HTTP客户端**: Axios
- **日期处理**: Day.js

## 📦 项目结构

```
slimming/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/            # API路由
│   │   │   ├── deps.py     # 依赖注入
│   │   │   └── v1/         # API v1版本
│   │   │       ├── auth.py     # 认证接口
│   │   │       ├── user.py     # 用户接口
│   │   │       ├── weight.py   # 体重接口
│   │   │       ├── exercise.py # 运动接口
│   │   │       ├── diet.py     # 饮食接口
│   │   │       └── health.py   # 健康数据接口
│   │   ├── core/           # 核心配置
│   │   │   ├── config.py   # 配置管理
│   │   │   ├── database.py # 数据库连接
│   │   │   ├── redis.py    # Redis连接
│   │   │   └── security.py # 安全相关
│   │   ├── models/         # 数据库模型
│   │   ├── schemas/        # Pydantic模型
│   │   ├── services/       # 业务逻辑
│   │   │   └── ml_service.py # 机器学习服务
│   │   └── utils/          # 工具函数
│   ├── main.py             # 应用入口
│   ├── init_db.py          # 数据库初始化
│   ├── requirements.txt    # Python依赖
│   ├── .env.example        # 环境变量示例
│   └── start.sh            # 启动脚本
│
└── frontend/               # 前端应用
    ├── src/
    │   ├── api/            # API接口
    │   ├── assets/         # 静态资源
    │   ├── components/     # 组件
    │   │   ├── WeightDialog.vue
    │   │   ├── ExerciseDialog.vue
    │   │   ├── DietDialog.vue
    │   │   ├── WaterDialog.vue
    │   │   └── SleepDialog.vue
    │   ├── router/         # 路由配置
    │   ├── stores/         # 状态管理
    │   ├── utils/          # 工具函数
    │   ├── views/          # 页面组件
    │   │   ├── Login.vue   # 登录页
    │   │   ├── Layout.vue  # 布局
    │   │   ├── Home.vue    # 首页
    │   │   ├── Trend.vue   # 趋势页
    │   │   └── Profile.vue # 个人信息页
    │   ├── App.vue
    │   └── main.js
    ├── index.html
    ├── vite.config.js
    └── package.json
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- MySQL 8.0+
- Redis 6.0+

### 后端部署

1. **进入后端目录**
```bash
cd backend
```

2. **创建虚拟环境**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库和Redis连接信息
```

5. **初始化数据库**
```bash
# 先在MySQL中创建数据库
mysql -u root -p
CREATE DATABASE slimming_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# 初始化表结构
python init_db.py
```

6. **启动服务**
```bash
# 使用启动脚本
chmod +x start.sh
./start.sh

# 或直接运行
python main.py
```

后端服务将运行在 `http://localhost:8000`
API文档地址: `http://localhost:8000/docs`

### 前端部署

1. **进入前端目录**
```bash
cd frontend
```

2. **安装依赖**
```bash
npm install
```

3. **启动开发服务器**
```bash
npm run dev
```

前端应用将运行在 `http://localhost:3000`

4. **构建生产版本**
```bash
npm run build
```

## 📝 环境变量配置

### 后端 (.env)

```env
# MySQL配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=slimming_db

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# JWT配置
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# 应用配置
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True
```

## 🎯 核心功能说明

### 1. 智能体重预测

系统使用线性回归模型分析历史体重数据，预测未来的体重变化趋势。预测结果包含：
- 预测值
- 95% 置信区间
- 可视化图表展示

### 2. 健康数据管理

支持记录和管理：
- 体重和体脂率
- 运动类型、时长、消耗卡路里
- 饮食营养成分（卡路里、蛋白质、碳水、脂肪）
- 每日饮水量
- 睡眠时长和质量

### 3. 数据可视化

- ECharts 图表展示体重变化趋势
- 多维度数据对比
- 交互式图表操作

### 4. 用户体验优化

- 圆角卡片设计
- 友好的交互提示
- 响应式布局
- 流畅的动画效果

## 📱 使用说明

### 登录注册
1. 输入手机号
2. 点击"获取验证码"
3. 输入收到的验证码
4. 点击"登录/注册"（新用户自动注册）

### 记录数据
1. 在首页点击对应的快捷按钮
2. 填写相关信息
3. 保存记录

### 查看趋势
1. 进入"体重趋势"页面
2. 选择预测天数
3. 点击"生成预测"查看未来趋势

## 🔧 开发说明

### API接口

所有API接口都需要在请求头中携带token：
```
Authorization: Bearer <token>
```

3. 创建对应的页面或组件

## 📄 许可证

MIT License

### 页面截图
<img width="1915" height="1032" alt="sy1" src="https://github.com/user-attachments/assets/2ede98a9-45b8-4cbf-9252-e7eca159e558" />
<img width="1920" height="958" alt="xq" src="https://github.com/user-attachments/assets/a67bb0fb-ce08-4936-9f5d-f2d2c6670a12" />
<img width="1920" height="958" alt="sy" src="https://github.com/user-attachments/assets/78e116d2-1cc7-404d-814b-2b6ba5a89593" />
<img width="1920" height="958" alt="rl" src="https://github.com/user-attachments/assets/b8260ae2-2cf2-475e-8ca5-4e5dd5644237" />
<img width="1920" height="958" alt="fx" src="https://github.com/user-attachments/assets/cc0cb7ff-fefe-4fa6-846c-0c1cb2a4de85" />
<img width="1920" height="958" alt="ai" src="https://github.com/user-attachments/assets/ba973f84-8752-4887-92d2-6d7a6259014f" />
<img width="1920" height="958" alt="拉取" src="https://github.com/user-attachments/assets/7984d132-143e-4454-a39d-54549743f5bd" />
<img width="1920" height="958" alt="榜单" src="https://github.com/user-attachments/assets/17216fbd-5188-42ca-84a3-b27f17f924fc" />
<img width="1920" height="958" alt="趋势" src="https://github.com/user-attachments/assets/39866470-a5f9-460f-a315-627f02cd439c" />









