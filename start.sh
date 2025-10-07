#!/bin/bash

# Flask API项目启动脚本

echo "🚀 启动Flask API项目..."

# 检查conda环境是否存在
if [ ! -d "$HOME/miniconda3/envs/flask-api-project" ]; then
    echo "❌ conda环境不存在，请先运行: conda env create -f environment.yml"
    exit 1
fi

# 设置环境变量
export FLASK_ENV=development
export FLASK_APP=run.py

# 使用conda环境的Python运行应用
echo "📍 使用conda环境启动应用..."
echo "🌐 访问地址: http://localhost:5000"
echo "📊 API健康检查: http://localhost:5000/api/health"
echo ""

$HOME/miniconda3/envs/flask-api-project/bin/python run.py
