#!/bin/bash

# Flask API项目快速启动脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Flask API项目快速启动${NC}"
echo ""

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}❌ Docker未安装，请先安装Docker${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}❌ Docker Compose未安装，请先安装Docker Compose${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker环境检查通过${NC}"

# 创建环境变量文件
if [ ! -f .env ]; then
    echo -e "${YELLOW}📝 创建环境变量文件...${NC}"
    cp env.example .env
    echo -e "${YELLOW}⚠️  请根据需要编辑.env文件中的配置${NC}"
fi

# 选择部署模式
echo ""
echo "请选择部署模式："
echo "1) 简化部署（仅核心服务）"
echo "2) 完整部署（包含监控和日志）"
echo "3) 仅启动数据库服务"
echo "4) 开发模式"
echo ""

read -p "请输入选择 (1-4): " choice

case $choice in
    1)
        echo -e "${BLUE}🔧 启动简化部署...${NC}"
        docker-compose -f docker-compose.simple.yml up -d
        ;;
    2)
        echo -e "${BLUE}🔧 启动完整部署...${NC}"
        docker-compose -f docker-compose.prod.yml up -d
        ;;
    3)
        echo -e "${BLUE}🔧 启动数据库服务...${NC}"
        docker-compose -f docker-compose.simple.yml up -d postgres mysql redis
        echo -e "${YELLOW}💡 数据库服务已启动，可以运行: python run.py${NC}"
        ;;
    4)
        echo -e "${BLUE}🔧 启动开发环境...${NC}"
        docker-compose up -d
        ;;
    *)
        echo -e "${YELLOW}❌ 无效选择，使用默认简化部署${NC}"
        docker-compose -f docker-compose.simple.yml up -d
        ;;
esac

echo ""
echo -e "${GREEN}✅ 服务启动完成！${NC}"
echo ""
echo "🌐 访问地址："
echo "  - API服务: http://localhost:5000"
echo "  - Web界面: http://localhost"
echo "  - 健康检查: http://localhost/api/health"
echo ""

if [ "$choice" = "2" ]; then
    echo "📊 监控服务："
    echo "  - Grafana: http://localhost:3000 (admin/admin)"
    echo "  - Prometheus: http://localhost:9090"
    echo "  - Kibana: http://localhost:5601"
    echo ""
fi

echo "🔧 常用命令："
echo "  - 查看日志: docker-compose logs -f flask-app"
echo "  - 停止服务: docker-compose down"
echo "  - 重启服务: docker-compose restart"
echo "  - 查看状态: docker-compose ps"
echo ""

echo -e "${GREEN}🎉 项目启动成功！${NC}"
