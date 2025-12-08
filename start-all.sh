#!/bin/bash

# 体重管理系统一键启动脚本

echo "========================================="
echo "      体重管理系统 - 一键启动"
echo "========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 检查环境
echo "检查运行环境..."

# 检查 Python
if ! command_exists python3; then
    echo -e "${RED}错误: 未找到 Python3，请先安装 Python 3.8+${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python3 已安装${NC}"

# 检查 Node.js
if ! command_exists node; then
    echo -e "${RED}错误: 未找到 Node.js，请先安装 Node.js 16+${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Node.js 已安装${NC}"

# 检查 MySQL
if ! command_exists mysql; then
    echo -e "${YELLOW}警告: 未找到 MySQL 客户端${NC}"
    echo "请确保 MySQL 服务正在运行"
fi

# 检查 Redis
if ! command_exists redis-cli; then
    echo -e "${YELLOW}警告: 未找到 Redis 客户端${NC}"
    echo "请确保 Redis 服务正在运行"
fi

echo ""
echo "========================================="
echo "启动后端服务..."
echo "========================================="

cd backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建 Python 虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装 Python 依赖..."
pip install -r requirements.txt -q

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}警告: 未找到 .env 文件${NC}"
    echo "正在从 .env.example 创建 .env 文件..."
    cp .env.example .env
    echo -e "${YELLOW}请编辑 backend/.env 文件，配置数据库和 Redis 连接信息${NC}"
    echo "按 Enter 继续..."
    read
fi

# 初始化数据库
echo "初始化数据库..."
python init_db.py

# 启动后端服务（后台运行）
echo "启动后端服务..."
nohup python main.py > backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✓ 后端服务已启动 (PID: $BACKEND_PID)${NC}"
echo "  访问地址: http://localhost:8000"
echo "  API 文档: http://localhost:8000/docs"

cd ..

echo ""
echo "========================================="
echo "启动前端服务..."
echo "========================================="

cd frontend

# 安装依赖
if [ ! -d "node_modules" ]; then
    echo "安装 Node.js 依赖..."
    npm install
fi

# 启动前端服务（后台运行）
echo "启动前端服务..."
nohup npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✓ 前端服务已启动 (PID: $FRONTEND_PID)${NC}"
echo "  访问地址: http://localhost:3000"

cd ..

echo ""
echo "========================================="
echo "          启动完成！"
echo "========================================="
echo ""
echo "后端服务: http://localhost:8000"
echo "前端应用: http://localhost:3000"
echo "API 文档: http://localhost:8000/docs"
echo ""
echo "进程信息:"
echo "  后端 PID: $BACKEND_PID"
echo "  前端 PID: $FRONTEND_PID"
echo ""
echo "日志文件:"
echo "  后端日志: backend/backend.log"
echo "  前端日志: frontend/frontend.log"
echo ""
echo "停止服务:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "或使用以下命令:"
echo "  ./stop.sh"
echo ""
echo -e "${GREEN}祝您使用愉快！${NC}"
