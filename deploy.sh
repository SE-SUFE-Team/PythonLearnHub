#!/bin/bash

# Python学习平台一键部署脚本
# 支持本地开发和生产环境部署

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    echo -e "${2}${1}${NC}"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 主菜单
show_menu() {
    echo
    print_message "🐍 Python学习平台部署脚本" $BLUE
    echo "=================================="
    echo "1. 本地开发环境运行"
    echo "2. 生产环境部署 (Gunicorn)"
    echo "3. Docker容器部署"
    echo "4. 停止服务"
    echo "5. 查看日志"
    echo "6. 退出"
    echo "=================================="
}

# 检查依赖
check_dependencies() {
    print_message "检查系统依赖..." $YELLOW
    
    if ! command_exists python3; then
        print_message "❌ Python3 未安装" $RED
        exit 1
    fi
    
    if ! command_exists pip; then
        print_message "❌ pip 未安装" $RED
        exit 1
    fi
    
    print_message "✅ 系统依赖检查通过" $GREEN
}

# 安装Python依赖
install_dependencies() {
    print_message "安装Python依赖..." $YELLOW
    pip install -r requirements.txt
    print_message "✅ 依赖安装完成" $GREEN
}

# 本地开发环境
dev_run() {
    print_message "启动开发环境..." $YELLOW
    check_dependencies
    install_dependencies
    
    print_message "🚀 启动Flask开发服务器..." $GREEN
    python app.py
}

# 生产环境部署
prod_deploy() {
    print_message "部署到生产环境..." $YELLOW
    check_dependencies
    install_dependencies
    
    # 安装Gunicorn
    if ! command_exists gunicorn; then
        print_message "安装Gunicorn..." $YELLOW
        pip install gunicorn
    fi
    
    # 创建日志目录
    mkdir -p logs
    
    # 启动Gunicorn
    print_message "🚀 启动Gunicorn服务器..." $GREEN
    gunicorn -c gunicorn.conf.py app:app --daemon
    
    print_message "✅ 生产环境部署完成" $GREEN
    print_message "访问地址: http://localhost:8000" $BLUE
}

# Docker部署
docker_deploy() {
    print_message "Docker容器部署..." $YELLOW
    
    if ! command_exists docker; then
        print_message "❌ Docker 未安装" $RED
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        print_message "❌ Docker Compose 未安装" $RED
        exit 1
    fi
    
    print_message "构建并启动Docker容器..." $YELLOW
    docker-compose up -d --build
    
    print_message "✅ Docker部署完成" $GREEN
    print_message "访问地址: http://localhost:8000" $BLUE
}

# 停止服务
stop_services() {
    print_message "停止服务..." $YELLOW
    
    # 停止Gunicorn进程
    if pgrep -f "gunicorn.*app:app" > /dev/null; then
        pkill -f "gunicorn.*app:app"
        print_message "✅ Gunicorn服务已停止" $GREEN
    fi
    
    # 停止Docker容器
    if command_exists docker-compose && [ -f docker-compose.yml ]; then
        docker-compose down
        print_message "✅ Docker容器已停止" $GREEN
    fi
}

# 查看日志
view_logs() {
    print_message "选择要查看的日志:" $YELLOW
    echo "1. 应用访问日志"
    echo "2. 应用错误日志"
    echo "3. Docker日志"
    echo "4. 返回主菜单"
    
    read -p "请选择 [1-4]: " log_choice
    
    case $log_choice in
        1)
            if [ -f logs/access.log ]; then
                tail -f logs/access.log
            else
                print_message "❌ 访问日志文件不存在" $RED
            fi
            ;;
        2)
            if [ -f logs/error.log ]; then
                tail -f logs/error.log
            else
                print_message "❌ 错误日志文件不存在" $RED
            fi
            ;;
        3)
            if command_exists docker-compose; then
                docker-compose logs -f
            else
                print_message "❌ Docker Compose 未安装" $RED
            fi
            ;;
        4)
            return
            ;;
        *)
            print_message "❌ 无效选择" $RED
            ;;
    esac
}

# 主循环
main() {
    while true; do
        show_menu
        read -p "请选择操作 [1-6]: " choice
        
        case $choice in
            1)
                dev_run
                ;;
            2)
                prod_deploy
                ;;
            3)
                docker_deploy
                ;;
            4)
                stop_services
                ;;
            5)
                view_logs
                ;;
            6)
                print_message "👋 再见!" $GREEN
                exit 0
                ;;
            *)
                print_message "❌ 无效选择，请重新输入" $RED
                ;;
        esac
        
        echo
        read -p "按回车键继续..."
    done
}

# 运行主程序
main