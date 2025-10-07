# Flask API 项目

这是一个基于Flask框架的HTTP API项目，支持PostgreSQL、MySQL和Redis数据库。

## 功能特性

- 🚀 Flask 3.0框架
- 🗄️ 多数据库支持（PostgreSQL、MySQL、Redis）
- 📊 RESTful API设计
- 🔄 数据库迁移支持
- 📝 请求日志记录
- 🐳 Docker容器化部署
- 🔧 环境配置管理
- 📚 完整的项目文档

## 📖 文档导航

### 快速开始
- [快速启动指南](#快速启动)
- [一键部署](#一键部署)

### 详细文档
- [📋 API文档](docs/api/README.md) - 完整的API接口说明
- [🚀 部署文档](docs/deployment/README.md) - 详细的部署指南
- [💻 开发文档](docs/development/README.md) - 开发指南和最佳实践
- [⚙️ 配置文档](docs/configuration/README.md) - 详细的配置说明
- [📊 监控文档](docs/monitoring/README.md) - 监控和运维指南

## 项目结构

```
.
├── app.py                      # Flask应用主文件
├── models.py                   # 数据库模型定义
├── routes.py                   # API路由定义
├── config.py                   # 数据库配置
├── run.py                      # 应用启动脚本
├── requirements.txt            # Python依赖
├── environment.yml             # Conda环境配置
├── Dockerfile                  # Docker镜像构建
├── docker-compose.yml          # 开发环境Docker编排
├── docker-compose.simple.yml   # 简化生产环境配置
├── docker-compose.prod.yml     # 完整生产环境配置
├── nginx.conf                  # Nginx配置文件
├── deploy.sh                   # 部署脚本
├── quick-start.sh              # 快速启动脚本
├── start.sh                    # 开发环境启动脚本
├── init.sh                     # 项目初始化脚本
├── env.example                 # 环境变量模板
├── .dockerignore               # Docker忽略文件
├── .gitignore                  # Git忽略文件
├── .github/                    # GitHub Actions配置
│   ├── workflows/
│   │   ├── ci.yml              # CI/CD工作流
│   │   └── release.yml         # 发布工作流
│   ├── ISSUE_TEMPLATE/         # Issue模板
│   └── pull_request_template.md # PR模板
├── monitoring/                 # 监控配置
│   ├── prometheus.yml          # Prometheus配置
│   └── grafana/                # Grafana配置
└── README.md                   # 项目说明
```

## 快速启动

### 一键部署

```bash
# 使用快速启动脚本（推荐新手）
./quick-start.sh

# 或使用部署脚本
./deploy.sh deploy-simple
```

### 开发环境

```bash
# 1. 创建conda环境
conda env create -f environment.yml
conda activate flask-api-project

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp env.example .env

# 4. 启动数据库服务
docker-compose up -d postgres mysql redis

# 5. 运行应用
python run.py
```

> 📖 详细的安装和配置说明请参考 [开发文档](docs/development/README.md)

## API接口

### 主要接口

- `GET /` - 服务状态
- `GET /api/health` - 健康检查
- `GET /api/users` - 用户管理
- `GET /api/products` - 产品管理

> 📖 完整的API文档请参考 [API文档](docs/api/README.md)

## 数据库配置

项目支持多种数据库：

- **PostgreSQL**: 主数据库
- **MySQL**: 日志存储
- **Redis**: 缓存和会话

> 📖 详细的数据库配置请参考 [配置文档](docs/configuration/README.md)

## Docker部署

### 部署模式

```bash
# 简化部署（推荐）
./deploy.sh deploy-simple

# 完整部署（包含监控）
./deploy.sh deploy-full

# 包含监控服务
./deploy.sh deploy-monitoring

# 包含日志服务
./deploy.sh deploy-logging
```

### 服务访问

- **API服务**: http://localhost:5000
- **Web界面**: http://localhost
- **健康检查**: http://localhost/api/health

> 📖 详细的部署指南请参考 [部署文档](docs/deployment/README.md)

## Git版本控制

```bash
# 初始化Git仓库
git init
git add .
git commit -m "Initial commit: Flask API project setup"

# 配置远程仓库
git remote add origin https://github.com/your-username/your-repo.git
git push -u origin main
```

项目已配置完整的`.gitignore`文件，自动忽略编译文件、环境变量、日志等。

## 开发指南

```bash
# 数据库迁移
flask db init
flask db migrate -m "描述信息"
flask db upgrade

# 代码格式化
black .
flake8 .

# 运行测试
pytest
```

> 📖 详细的开发指南请参考 [开发文档](docs/development/README.md)

## 环境变量

主要环境变量：

- `FLASK_ENV`: 运行环境 (development/production)
- `SECRET_KEY`: 应用密钥
- `POSTGRES_PASSWORD`: PostgreSQL密码
- `MYSQL_PASSWORD`: MySQL密码
- `REDIS_PASSWORD`: Redis密码

> 📖 完整的环境变量配置请参考 [配置文档](docs/configuration/README.md)

## 故障排除

### 常见问题

1. **数据库连接失败** - 检查服务状态和配置
2. **Redis连接失败** - 验证Redis配置和网络
3. **端口占用** - 更改PORT环境变量或停止占用进程

> 📖 详细的故障排除指南请参考 [部署文档](docs/deployment/README.md)

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

> 📖 详细的贡献指南请参考 [开发文档](docs/development/README.md)

## CI/CD自动化

项目包含完整的GitHub Actions CI/CD流程：

- **代码质量检查** (flake8, black)
- **单元测试** (pytest)
- **Docker镜像构建**
- **安全扫描** (Trivy)
- **自动部署**

> 📖 详细的CI/CD配置请参考 [部署文档](docs/deployment/README.md)

## 监控和运维

### 服务监控

- **Grafana仪表板**: http://localhost:3000 (admin/admin)
- **Prometheus指标**: http://localhost:9090
- **Kibana日志**: http://localhost:5601

> 📖 详细的监控配置请参考 [监控文档](docs/monitoring/README.md)

## 许可证

MIT License
