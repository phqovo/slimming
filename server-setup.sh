#!/bin/bash

# ========================================
# 服务器环境初始化脚本
# 在服务器上运行此脚本准备部署环境
# ========================================

set -e

echo "========================================="
echo "服务器环境初始化"
echo "========================================="

# 更新系统包
echo "[1/8] 更新系统包..."
yum update -y || apt-get update -y

# 安装 Python3
echo "[2/8] 安装 Python3..."
if ! command -v python3 &> /dev/null; then
    yum install -y python3 python3-pip || apt-get install -y python3 python3-pip
    echo "✓ Python3 安装完成: $(python3 --version)"
else
    echo "✓ Python3 已安装: $(python3 --version)"
fi

# 升级 pip
echo "[3/8] 升级 pip..."
python3 -m pip install --upgrade pip
echo "✓ pip 版本: $(pip3 --version)"

# 安装 Node.js (食物搜索功能需要)
echo "[4/8] 检查 Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✓ Node.js 已安装: $NODE_VERSION"
else
    echo "⚠️  Node.js 未安装，正在安装..."
    # 使用 NodeSource 仓库安装 Node.js 16.x LTS
    if command -v yum &> /dev/null; then
        # CentOS/RHEL
        curl -fsSL https://rpm.nodesource.com/setup_16.x | bash -
        yum install -y nodejs
    elif command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        curl -fsSL https://deb.nodesource.com/setup_16.x | bash -
        apt-get install -y nodejs
    else
        echo "❌ 无法自动安装 Node.js，请手动安装"
        echo "安装方法: https://nodejs.org/"
        exit 1
    fi
    
    if command -v node &> /dev/null; then
        echo "✓ Node.js 安装完成: $(node --version)"
        echo "✓ npm 版本: $(npm --version)"
    else
        echo "❌ Node.js 安装失败"
        exit 1
    fi
fi

# 安装 lsof (用于检查端口占用)
echo "[5/8] 安装 lsof..."
yum install -y lsof || apt-get install -y lsof
echo "✓ lsof 已安装"

# 安装 MySQL 客户端 (如果需要)
echo "[6/8] 检查 MySQL..."
if command -v mysql &> /dev/null; then
    echo "✓ MySQL 客户端已安装"
else
    echo "⚠️  MySQL 客户端未安装，需要手动安装并配置数据库"
fi

# 安装 Redis (如果需要)
echo "[7/8] 检查 Redis..."
if command -v redis-server &> /dev/null; then
    echo "✓ Redis 已安装"
    # 检查 Redis 是否运行
    if pgrep -x "redis-server" > /dev/null; then
        echo "✓ Redis 正在运行"
    else
        echo "⚠️  Redis 未运行，启动 Redis..."
        redis-server --daemonize yes
    fi
else
    echo "⚠️  Redis 未安装，需要手动安装"
    echo "安装命令: yum install -y redis || apt-get install -y redis"
fi

# 创建项目目录
echo "[8/8] 创建项目目录..."
mkdir -p /usr/local/src/web/backend
mkdir -p /usr/local/src/web/frontend
echo "✓ 项目目录已创建"

echo ""
echo "========================================="
echo "环境初始化完成！"
echo "========================================="
echo ""
echo "请确保以下服务已配置："
echo "  1. MySQL 数据库 (slimming_db)"
echo "  2. Redis 服务"
echo "  3. Nginx 配置"
echo ""
echo "数据库配置文件位置: /usr/local/src/web/backend/.env"
echo ""
