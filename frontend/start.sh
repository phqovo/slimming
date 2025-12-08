#!/bin/bash

# 前端启动脚本

echo "========================================="
echo "   体重管理平台前端应用启动脚本"
echo "========================================="

# 检查Node.js环境
if ! command -v node &> /dev/null; then
    echo "错误: 未找到Node.js，请先安装Node.js"
    exit 1
fi

# 检查npm
if ! command -v npm &> /dev/null; then
    echo "错误: 未找到npm，请先安装npm"
    exit 1
fi

# 检查node_modules
if [ ! -d "node_modules" ]; then
    echo "未找到依赖，正在安装..."
    npm install
fi

# 启动开发服务器
echo "启动前端开发服务器..."
echo "服务将运行在 http://localhost:3000"
npm run dev
