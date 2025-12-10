#!/bin/bash

# ========================================
# 体重管理系统自动化部署脚本
# ========================================

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 加载配置文件
CONFIG_FILE="$(dirname "$0")/deploy.config"

if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}[错误]${NC} 配置文件不存在: $CONFIG_FILE"
    echo -e "${YELLOW}请复制 deploy.config.example 为 deploy.config 并填入真实配置${NC}"
    echo -e "${YELLOW}命令: cp deploy.config.example deploy.config${NC}"
    exit 1
fi

# 读取配置文件
source "$CONFIG_FILE"

# 验证必需配置
if [ -z "$SERVER_IP" ] || [ -z "$SERVER_USER" ]; then
    echo -e "${RED}[错误]${NC} 配置文件缺少必需参数"
    echo -e "${YELLOW}请检查 deploy.config 中的 SERVER_IP 和 SERVER_USER${NC}"
    exit 1
fi

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[信息]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[成功]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[警告]${NC} $1"
}

print_error() {
    echo -e "${RED}[错误]${NC} $1"
}

print_step() {
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}========================================${NC}\n"
}

# 检查依赖
check_dependencies() {
    print_step "步骤 1: 检查本地依赖"
    
    # 检查 Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js 未安装，请先安装 Node.js"
        exit 1
    fi
    print_success "Node.js 已安装: $(node --version)"
    
    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安装，请先安装 Python3"
        exit 1
    fi
    print_success "Python3 已安装: $(python3 --version)"
    
    # 检查 SSH 连接
    print_info "检查 SSH 连接..."
    if ! command -v ssh &> /dev/null; then
        print_error "SSH 未安装"
        exit 1
    fi
    print_success "SSH 已安装"
}

# 构建前端
build_frontend() {
    print_step "步骤 2: 构建前端项目"
    
    cd $LOCAL_FRONTEND_DIR
    
    print_info "安装依赖..."
    npm install
    print_success "依赖安装完成"
    
    print_info "开始生产环境构建..."
    NODE_ENV=production npm run build
    print_success "前端构建完成"
    
    cd ..
}

# 打包后端
prepare_backend() {
    print_step "步骤 3: 准备后端文件"
    
    print_info "检查后端依赖文件..."
    if [ ! -f "$LOCAL_BACKEND_DIR/requirements.txt" ]; then
        print_error "requirements.txt 不存在"
        exit 1
    fi
    print_success "后端文件准备完成"
}

# 连接服务器测试
test_connection() {
    print_step "步骤 4: 测试服务器连接"
    
    print_info "连接到 $SERVER_USER@$SERVER_IP ..."
    
    ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 $SERVER_USER@$SERVER_IP "echo '连接成功'" || {
        print_error "无法连接到服务器"
        print_warning "请确保已配置 SSH 密钥认证，或者手动输入密码"
        exit 1
    }
    
    print_success "服务器连接正常"
}

# 创建服务器目录
create_server_dirs() {
    print_step "步骤 5: 创建服务器目录"
    
    print_info "创建后端目录..."
    ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "
        mkdir -p $SERVER_BACKEND_DIR
        mkdir -p $SERVER_FRONTEND_DIR
    " || {
        print_error "创建目录失败"
        exit 1
    }
    
    print_success "服务器目录创建完成"
}

# 上传前端文件
upload_frontend() {
    print_step "步骤 6: 上传前端文件到服务器"
    
    print_info "清空并重新创建前端目录..."
    ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "
        rm -rf $SERVER_FRONTEND_DIR/*
        mkdir -p $SERVER_FRONTEND_DIR
    " || {
        print_error "清理前端目录失败"
        exit 1
    }
    
    print_info "上传前端 dist 目录..."
    cd $LOCAL_FRONTEND_DIR/dist
    tar czf - . | ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "cd $SERVER_FRONTEND_DIR && tar xzf -" || {
        print_error "前端文件上传失败"
        exit 1
    }
    cd - > /dev/null
    
    print_success "前端文件上传完成"
    
    # 验证上传
    print_info "验证前端文件..."
    ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "
        if [ -f $SERVER_FRONTEND_DIR/index.html ]; then
            echo '前端文件验证成功'
        else
            echo '前端文件验证失败'
            exit 1
        fi
    "
    print_success "前端文件验证通过"
    
    # 添加：清理 Nginx 缓存
    print_info "清理 Nginx 缓存..."
    ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "
        # 重载 Nginx 配置
        if command -v nginx &> /dev/null; then
            nginx -s reload && echo 'Nginx 配置重载成功' || echo 'Nginx 配置重载失败，请手动重载'
        fi
    "
    print_success "Nginx 缓存清理完成"
}

# 上传后端文件
upload_backend() {
    print_step "步骤 7: 上传后端文件到服务器"
    
    print_info "清空并重新创建后端目录..."
    ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "
        rm -rf $SERVER_BACKEND_DIR/*
        mkdir -p $SERVER_BACKEND_DIR
    " || {
        print_error "清理后端目录失败"
        exit 1
    }
    
    print_info "打包后端代码（排除缓存和日志）..."
    cd $LOCAL_BACKEND_DIR
    
    # 使用 tar 打包，排除不必要的文件（保留 .env）
    tar czf - \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='*.pyo' \
        --exclude='*.pyd' \
        --exclude='.pytest_cache' \
        --exclude='logs' \
        --exclude='uploads' \
        --exclude='.git' \
        --exclude='venv' \
        --exclude='*.egg-info' \
        . | ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "cd $SERVER_BACKEND_DIR && tar xzf -" || {
        print_error "后端文件上传失败"
        exit 1
    }
    cd - > /dev/null
    
    print_success "后端文件上传完成"
}

# 停止旧的后端进程
stop_backend() {
    print_step "步骤 8: 停止旧的后端进程"
    
    print_info "查找运行在端口 $SERVER_PORT 的进程..."
    
    ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "
        # 查找并杀死占用端口的进程
        PID=\$(lsof -ti:$SERVER_PORT)
        if [ -n \"\$PID\" ]; then
            echo \"找到进程 PID: \$PID\"
            kill -9 \$PID
            echo \"已杀死进程 \$PID\"
        else
            echo \"没有找到运行在端口 $SERVER_PORT 的进程\"
        fi
        
        # 额外：杀死所有 uvicorn 进程（如果有）
        pkill -9 -f 'uvicorn.*main:app' || echo '没有找到 uvicorn 进程'
    " || {
        print_warning "停止进程时出现警告（可能没有运行的进程）"
    }
    
    print_success "旧进程已停止"
}

# 安装后端依赖
install_backend_deps() {
    print_step "步骤 9: 安装后端依赖"
    
    print_info "在服务器上安装 Python 依赖..."
    
    ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "
        cd $SERVER_BACKEND_DIR
        
        # 检查 Node.js 是否安装（食物搜索功能需要）
        echo '检查 Node.js...'
        if command -v node &> /dev/null; then
            echo "✓ Node.js 已安装: \\$(node --version)"
        else
            echo '⚠️  Node.js 未安装，正在安装...'
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
                echo '❌ 无法自动安装 Node.js'
                echo '请手动安装 Node.js 16.x 或更高版本'
                echo '安装方法: https://nodejs.org/'
            fi
            
            # 验证安装
            if command -v node &> /dev/null; then
                echo "✓ Node.js 安装完成: \\$(node --version)"
            else
                echo '⚠️  Node.js 安装失败，食物搜索功能将无法使用'
            fi
        fi
        
        # 检查 Python 版本
        PYTHON_VERSION=\$(python3 --version 2>&1 | awk '{print \$2}' | cut -d. -f1,2)
        echo "Python 版本: \$PYTHON_VERSION"
        
        # 检查是否为 Python 3.6
        if [[ \"\$PYTHON_VERSION\" == \"3.6\" ]]; then
            echo '检测到 Python 3.6，需要升级到 Python 3.8+'
            echo '正在安装 Python 3.8...'
            
            # CentOS/RHEL 系统
            if command -v yum &> /dev/null; then
                yum install -y python38 python38-pip || {
                    echo '尝试安装 Python 3.9...'
                    yum install -y python39 python39-pip
                }
            # Debian/Ubuntu 系统
            elif command -v apt-get &> /dev/null; then
                apt-get update
                apt-get install -y python3.8 python3.8-pip || {
                    echo '尝试安装 Python 3.9...'
                    apt-get install -y python3.9 python3.9-pip
                }
            fi
            
            # 检查是否安装成功
            if command -v python3.8 &> /dev/null; then
                alias python3=python3.8
                alias pip3=pip3.8
                echo 'Python 3.8 安装成功'
            elif command -v python3.9 &> /dev/null; then
                alias python3=python3.9
                alias pip3=pip3.9
                echo 'Python 3.9 安装成功'
            else
                echo '无法安装 Python 3.8+，将使用国内镜像源安装依赖'
            fi
        fi
        
        # 使用国内镜像源升级 pip
        echo '升级 pip...'
        python3 -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
        
        # 使用国内镜像源安装依赖（增加超时时间和重试）
        echo '安装项目依赖...'
        pip3 install -r requirements.txt \
            -i https://pypi.tuna.tsinghua.edu.cn/simple \
            --default-timeout=200 \
            --retries 5 || {
            echo '使用清华镜像失败，尝试使用阿里云镜像...'
            pip3 install -r requirements.txt \
                -i https://mirrors.aliyun.com/pypi/simple/ \
                --default-timeout=200 \
                --retries 5
        }
        
        # 验证关键包是否安装
        echo '验证依赖包...'
        python3 -c 'import fastapi; import pydantic; import uvicorn; import pydantic_settings' || {
            echo '关键依赖包缺失，尝试单独安装...'
            pip3 install pydantic==2.10.4 pydantic-settings==2.7.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
        }
    " || {
        print_error "安装后端依赖失败"
        print_warning "如果是 Python 版本问题，请手动升级服务器 Python 到 3.8+"
        exit 1
    }
    
    print_success "后端依赖安装完成"
}

# 启动后端服务
start_backend() {
    print_step "步骤 10: 启动后端服务"
    
    print_info "启动 FastAPI 服务..."
    
    ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "
        cd $SERVER_BACKEND_DIR
        
        # 创建日志目录
        mkdir -p logs
        
        # 后台启动服务（添加 --root-path 参数）
        nohup python3 -m uvicorn main:app --host 0.0.0.0 --port $SERVER_PORT --root-path /health --reload > logs/app.log 2>&1 &
        
        # 等待服务启动
        sleep 3
        
        # 检查服务是否启动
        if lsof -ti:$SERVER_PORT > /dev/null; then
            echo \"后端服务已启动，监听端口: $SERVER_PORT\"
            echo \"进程 PID: \$(lsof -ti:$SERVER_PORT)\"
        else
            echo \"后端服务启动失败\"
            exit 1
        fi
    " || {
        print_error "启动后端服务失败"
        exit 1
    }
    
    print_success "后端服务启动成功"
}

# 验证部署
verify_deployment() {
    print_step "步骤 11: 验证部署"
    
    print_info "检查后端 API..."
    
    # 等待几秒让服务完全启动
    sleep 2
    
    ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_IP "
        # 检查端口
        if lsof -ti:$SERVER_PORT > /dev/null; then
            echo '✓ 后端端口 $SERVER_PORT 正在监听'
        else
            echo '✗ 后端端口 $SERVER_PORT 未监听'
            exit 1
        fi
        
        # 检查前端文件
        if [ -f $SERVER_FRONTEND_DIR/index.html ]; then
            echo '✓ 前端文件存在'
        else
            echo '✗ 前端文件不存在'
            exit 1
        fi
    " || {
        print_error "部署验证失败"
        exit 1
    }
    
    print_success "部署验证通过"
}

# 显示部署信息
show_deployment_info() {
    print_step "部署完成"
    
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}部署信息${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "服务器IP:    ${BLUE}$SERVER_IP${NC}"
    echo -e "后端端口:    ${BLUE}$SERVER_PORT${NC}"
    echo -e "后端目录:    ${BLUE}$SERVER_BACKEND_DIR${NC}"
    echo -e "前端目录:    ${BLUE}$SERVER_FRONTEND_DIR${NC}"
    echo -e ""
    echo -e "访问地址:    ${GREEN}http://$SERVER_IP/health/${NC}"
    echo -e "API地址:     ${GREEN}http://$SERVER_IP/health/api/${NC}"
    echo -e ""
    echo -e "查看后端日志: ${YELLOW}ssh $SERVER_USER@$SERVER_IP 'tail -f $SERVER_BACKEND_DIR/logs/app.log'${NC}"
    echo -e "重启后端:     ${YELLOW}ssh $SERVER_USER@$SERVER_IP 'cd $SERVER_BACKEND_DIR && pkill -9 -f uvicorn && nohup python3 -m uvicorn main:app --host 0.0.0.0 --port $SERVER_PORT --root-path /health --reload > logs/app.log 2>&1 &'${NC}"
    echo -e "${GREEN}========================================${NC}"
}

# 主流程
main() {
    print_info "开始部署体重管理系统..."
    print_info "目标服务器: $SERVER_USER@$SERVER_IP"
    echo ""
    
    # 执行部署步骤
    check_dependencies
    build_frontend
    prepare_backend
    test_connection
    create_server_dirs
    upload_frontend
    upload_backend
    stop_backend
    install_backend_deps
    start_backend
    verify_deployment
    show_deployment_info
    
    print_success "🎉 部署完成！"
}

# 运行主流程
main
