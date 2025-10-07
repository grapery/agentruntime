#!/bin/bash

# Flask API项目部署脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Docker是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    log_success "Docker环境检查通过"
}

# 检查环境变量文件
check_env() {
    if [ ! -f .env ]; then
        log_warning ".env文件不存在，从模板创建..."
        cp env.example .env
        log_warning "请编辑.env文件配置数据库连接信息"
        exit 1
    fi
    log_success "环境变量文件检查通过"
}

# 构建Docker镜像
build_image() {
    log_info "构建Docker镜像..."
    
    # 获取Git信息
    GIT_COMMIT=$(git rev-parse --short HEAD)
    GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    
    # 构建镜像
    docker build -t flask-api:latest \
                 -t flask-api:${GIT_COMMIT} \
                 -t flask-api:${GIT_BRANCH}-${TIMESTAMP} \
                 --build-arg GIT_COMMIT=${GIT_COMMIT} \
                 --build-arg GIT_BRANCH=${GIT_BRANCH} \
                 .
    
    log_success "Docker镜像构建完成"
}

# 停止现有服务
stop_services() {
    local compose_file=${1:-docker-compose.prod.yml}
    log_info "停止现有服务..."
    docker-compose -f $compose_file down || true
    log_success "现有服务已停止"
}

# 启动服务
start_services() {
    local compose_file=${1:-docker-compose.prod.yml}
    local profiles=${2:-""}
    
    log_info "启动服务..."
    
    if [ -n "$profiles" ]; then
        docker-compose -f $compose_file --profile $profiles up -d
    else
        docker-compose -f $compose_file up -d
    fi
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 30
    
    # 检查服务状态
    check_services
}

# 检查服务状态
check_services() {
    log_info "检查服务状态..."
    
    # 检查Flask应用
    if curl -f http://localhost:5000/api/health > /dev/null 2>&1; then
        log_success "Flask应用运行正常"
    else
        log_error "Flask应用启动失败"
        docker-compose -f docker-compose.prod.yml logs flask-app
        exit 1
    fi
    
    # 检查Nginx
    if curl -f http://localhost/health > /dev/null 2>&1; then
        log_success "Nginx运行正常"
    else
        log_warning "Nginx可能未正常启动"
    fi
    
    # 检查数据库连接
    if docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
        log_success "PostgreSQL连接正常"
    else
        log_error "PostgreSQL连接失败"
    fi
    
    if docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
        log_success "Redis连接正常"
    else
        log_error "Redis连接失败"
    fi
}

# 数据库迁移
run_migrations() {
    log_info "运行数据库迁移..."
    docker-compose -f docker-compose.prod.yml exec flask-app python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('数据库表创建完成')
"
    log_success "数据库迁移完成"
}

# 清理旧镜像
cleanup_images() {
    log_info "清理旧Docker镜像..."
    docker image prune -f
    log_success "旧镜像清理完成"
}

# 显示服务信息
show_info() {
    log_success "部署完成！"
    echo ""
    echo "服务访问地址："
    echo "  - API服务: http://localhost:5000"
    echo "  - Web界面: http://localhost"
    echo "  - 健康检查: http://localhost/api/health"
    echo "  - Grafana监控: http://localhost:3000 (admin/admin)"
    echo "  - Prometheus: http://localhost:9090"
    echo ""
    echo "查看日志："
    echo "  docker-compose -f docker-compose.prod.yml logs -f flask-app"
    echo ""
    echo "停止服务："
    echo "  docker-compose -f docker-compose.prod.yml down"
}

# 主函数
main() {
    log_info "开始部署Flask API项目..."
    
    # 检查环境
    check_docker
    check_env
    
    # 构建和部署
    build_image
    stop_services
    start_services
    run_migrations
    
    # 清理和显示信息
    cleanup_images
    show_info
}

# 处理命令行参数
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "deploy-simple")
        check_docker
        check_env
        build_image
        stop_services "docker-compose.simple.yml"
        start_services "docker-compose.simple.yml"
        show_info
        ;;
    "deploy-full")
        check_docker
        check_env
        build_image
        stop_services "docker-compose.prod.yml"
        start_services "docker-compose.prod.yml"
        show_info
        ;;
    "deploy-monitoring")
        check_docker
        check_env
        build_image
        stop_services "docker-compose.prod.yml"
        start_services "docker-compose.prod.yml" "monitoring"
        show_info
        ;;
    "deploy-logging")
        check_docker
        check_env
        build_image
        stop_services "docker-compose.prod.yml"
        start_services "docker-compose.prod.yml" "logging"
        show_info
        ;;
    "build")
        check_docker
        build_image
        ;;
    "start")
        check_docker
        check_env
        start_services "${2:-docker-compose.prod.yml}"
        ;;
    "stop")
        stop_services "${2:-docker-compose.prod.yml}"
        ;;
    "restart")
        stop_services "${2:-docker-compose.prod.yml}"
        start_services "${2:-docker-compose.prod.yml}"
        ;;
    "status")
        check_services
        ;;
    "logs")
        docker-compose -f ${2:-docker-compose.prod.yml} logs -f ${3:-flask-app}
        ;;
    "cleanup")
        cleanup_images
        ;;
    *)
        echo "用法: $0 {deploy|deploy-simple|deploy-full|deploy-monitoring|deploy-logging|build|start|stop|restart|status|logs|cleanup}"
        echo ""
        echo "命令说明："
        echo "  deploy           - 完整部署（默认，使用docker-compose.prod.yml）"
        echo "  deploy-simple    - 简化部署（仅核心服务）"
        echo "  deploy-full      - 完整部署（包含所有服务）"
        echo "  deploy-monitoring- 部署包含监控服务"
        echo "  deploy-logging   - 部署包含日志服务"
        echo "  build            - 仅构建镜像"
        echo "  start [file]     - 启动服务"
        echo "  stop [file]      - 停止服务"
        echo "  restart [file]   - 重启服务"
        echo "  status           - 检查服务状态"
        echo "  logs [file] [service] - 查看日志"
        echo "  cleanup          - 清理旧镜像"
        echo ""
        echo "Docker Compose文件："
        echo "  docker-compose.simple.yml  - 简化配置（仅核心服务）"
        echo "  docker-compose.prod.yml    - 完整配置（包含可选服务）"
        exit 1
        ;;
esac
