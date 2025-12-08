#!/bin/bash

# 体重管理系统停止脚本

echo "========================================="
echo "      停止体重管理系统服务"
echo "========================================="

# 查找并停止后端进程
echo "正在停止后端服务..."
BACKEND_PID=$(ps aux | grep 'python main.py' | grep -v grep | awk '{print $2}')
if [ ! -z "$BACKEND_PID" ]; then
    kill $BACKEND_PID
    echo "✓ 后端服务已停止 (PID: $BACKEND_PID)"
else
    echo "后端服务未运行"
fi

# 查找并停止前端进程
echo "正在停止前端服务..."
FRONTEND_PID=$(ps aux | grep 'vite' | grep -v grep | awk '{print $2}')
if [ ! -z "$FRONTEND_PID" ]; then
    kill $FRONTEND_PID
    echo "✓ 前端服务已停止 (PID: $FRONTEND_PID)"
else
    echo "前端服务未运行"
fi

echo ""
echo "所有服务已停止"
