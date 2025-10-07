#!/bin/bash

# Flask API项目初始化脚本

echo "🚀 开始初始化Flask API项目..."

# 检查conda是否安装
if ! command -v conda &> /dev/null; then
    echo "❌ Conda未安装，请先安装Anaconda或Miniconda"
    exit 1
fi

# 创建conda环境
echo "📦 创建conda环境..."
conda env create -f environment.yml

# 激活环境
echo "🔧 激活conda环境..."
conda activate flask-api-project

# 安装Python依赖
echo "📚 安装Python依赖..."
pip install -r requirements.txt

# 创建环境变量文件
if [ ! -f .env ]; then
    echo "⚙️ 创建环境变量文件..."
    cp env.example .env
    echo "✅ 已创建.env文件，请根据需要修改配置"
else
    echo "ℹ️ .env文件已存在，跳过创建"
fi

# 检查Docker是否安装
if command -v docker &> /dev/null; then
    echo "🐳 检测到Docker，可以启动数据库服务..."
    echo "运行以下命令启动数据库服务："
    echo "docker-compose up -d postgres mysql redis"
else
    echo "⚠️ 未检测到Docker，请手动安装和配置数据库服务"
fi

echo ""
echo "✅ 项目初始化完成！"
echo ""
echo "📋 下一步操作："
echo "1. 激活conda环境: conda activate flask-api-project"
echo "2. 配置.env文件中的数据库连接信息"
echo "3. 启动数据库服务（使用Docker或手动安装）"
echo "4. 运行应用: python run.py"
echo ""
echo "🌐 应用启动后访问: http://localhost:5000"
echo "📊 API健康检查: http://localhost:5000/api/health"
