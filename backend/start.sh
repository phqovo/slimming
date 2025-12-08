#!/bin/bash

# 体重管理平台 - 后端启动脚本

echo "========================================="
echo "   体重管理平台后端服务启动脚本"
echo "========================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "未找到虚拟环境，正在创建..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "检查并安装依赖..."
pip install -r requirements.txt

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "未找到.env文件，从.env.example复制..."
    cp .env.example .env
    echo "请编辑.env文件，配置数据库和Redis连接信息"
    echo "配置完成后，请重新运行此脚本"
    exit 0
fi

# 初始化数据库
echo "初始化数据库..."
python init_db.py

# 启动服务
echo "启动后端服务..."
echo "服务将运行在 http://localhost:8000"
echo "API文档地址: http://localhost:8000/docs"
python main.py
