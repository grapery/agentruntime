# 部署文档

Flask API项目的详细部署指南。

## 目录

- [部署概述](#部署概述)
- [Docker部署](#docker部署)
- [环境配置](#环境配置)
- [部署脚本使用](#部署脚本使用)
- [生产环境部署](#生产环境部署)
- [故障排除](#故障排除)

## 部署概述

项目支持多种部署方式：

1. **Docker Compose部署**（推荐）
2. **传统服务器部署**
3. **云平台部署**

## Docker部署

### 快速部署

使用部署脚本进行一键部署：

```bash
# 简化部署（推荐新手）
./deploy.sh deploy-simple

# 完整部署
./deploy.sh deploy-full
```

### 手动部署

#### 1. 构建镜像

```bash
# 构建Docker镜像
docker build -t flask-api:latest .

# 查看镜像
docker images | grep flask-api
```

#### 2. 配置环境变量

```bash
# 复制环境变量模板
cp env.example .env

# 编辑配置文件
nano .env
```

#### 3. 启动服务

```bash
# 启动简化版本（仅核心服务）
docker-compose -f docker-compose.simple.yml up -d

# 启动完整版本（包含监控）
docker-compose -f docker-compose.prod.yml up -d
```

### Docker Compose配置说明

#### 简化配置 (`docker-compose.simple.yml`)

包含核心服务：
- Flask应用
- PostgreSQL数据库
- MySQL数据库
- Redis缓存
- Nginx反向代理

#### 完整配置 (`docker-compose.prod.yml`)

包含所有服务：
- 核心服务（同上）
- Prometheus监控（可选）
- Grafana仪表板（可选）
- Elasticsearch日志（可选）
- Kibana日志可视化（可选）

## 环境配置

### 必需环境变量

```bash
# Flask应用配置
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
PORT=5000

# PostgreSQL配置
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=flask_api_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-postgres-password

# MySQL配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=flask_api_db
MYSQL_USER=root
MYSQL_PASSWORD=your-mysql-password

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your-redis-password
```

### 可选环境变量

```bash
# 监控配置
GRAFANA_PASSWORD=your-grafana-password

# 日志配置
LOG_LEVEL=INFO
```

## 部署脚本使用

### 基本命令

```bash
# 查看帮助
./deploy.sh

# 简化部署
./deploy.sh deploy-simple

# 完整部署
./deploy.sh deploy-full

# 包含监控服务
./deploy.sh deploy-monitoring

# 包含日志服务
./deploy.sh deploy-logging
```

### 管理命令

```bash
# 构建镜像
./deploy.sh build

# 启动服务
./deploy.sh start [compose-file]

# 停止服务
./deploy.sh stop [compose-file]

# 重启服务
./deploy.sh restart [compose-file]

# 检查状态
./deploy.sh status

# 查看日志
./deploy.sh logs [compose-file] [service-name]

# 清理旧镜像
./deploy.sh cleanup
```

### 快速启动脚本

```bash
# 交互式启动
./quick-start.sh
```

## 生产环境部署

### 服务器要求

- **操作系统**: Ubuntu 20.04+ / CentOS 8+ / macOS
- **内存**: 最少2GB，推荐4GB+
- **存储**: 最少10GB可用空间
- **网络**: 开放80、443、5000端口

### 部署步骤

#### 1. 准备服务器

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. 部署应用

```bash
# 克隆项目
git clone https://github.com/your-username/your-repo.git
cd your-repo

# 配置环境变量
cp env.example .env
nano .env

# 部署应用
./deploy.sh deploy-simple
```

#### 3. 配置域名和SSL

```bash
# 配置Nginx（如果需要）
sudo nano /etc/nginx/sites-available/your-domain
sudo ln -s /etc/nginx/sites-available/your-domain /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# 配置SSL证书（使用Let's Encrypt）
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 监控和日志

#### 启用监控服务

```bash
# 启动包含监控的部署
./deploy.sh deploy-monitoring

# 访问监控界面
# Grafana: http://your-domain:3000
# Prometheus: http://your-domain:9090
```

#### 启用日志服务

```bash
# 启动包含日志的部署
./deploy.sh deploy-logging

# 访问日志界面
# Kibana: http://your-domain:5601
```

## 故障排除

### 常见问题

#### 1. Docker服务启动失败

```bash
# 检查Docker状态
sudo systemctl status docker

# 重启Docker服务
sudo systemctl restart docker

# 查看Docker日志
sudo journalctl -u docker.service
```

#### 2. 数据库连接失败

```bash
# 检查数据库容器状态
docker-compose ps

# 查看数据库日志
docker-compose logs postgres
docker-compose logs mysql

# 测试数据库连接
docker-compose exec postgres pg_isready -U postgres
```

#### 3. 端口冲突

```bash
# 查看端口占用
sudo netstat -tlnp | grep :5000

# 修改端口配置
nano .env
# 修改 PORT=5001

# 重启服务
./deploy.sh restart
```

#### 4. 内存不足

```bash
# 查看内存使用
free -h
docker stats

# 清理Docker资源
docker system prune -a

# 调整服务配置
nano docker-compose.prod.yml
# 减少worker数量或调整资源限制
```

### 日志查看

```bash
# 查看应用日志
docker-compose logs -f flask-app

# 查看所有服务日志
docker-compose logs -f

# 查看特定时间段的日志
docker-compose logs --since="2024-01-01T00:00:00" flask-app

# 查看错误日志
docker-compose logs flask-app | grep ERROR
```

### 性能优化

#### 1. 数据库优化

```bash
# 连接PostgreSQL
docker-compose exec postgres psql -U postgres -d flask_api_db

# 创建索引
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
```

#### 2. Redis优化

```bash
# 连接Redis
docker-compose exec redis redis-cli

# 查看内存使用
INFO memory

# 设置过期策略
CONFIG SET maxmemory-policy allkeys-lru
```

#### 3. Nginx优化

```bash
# 编辑Nginx配置
nano nginx.conf

# 启用gzip压缩
gzip on;
gzip_types text/plain application/json;

# 设置缓存
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 备份和恢复

#### 数据库备份

```bash
# 备份PostgreSQL
docker-compose exec postgres pg_dump -U postgres flask_api_db > backup.sql

# 备份MySQL
docker-compose exec mysql mysqldump -u root -p flask_api_db > mysql_backup.sql

# 备份Redis
docker-compose exec redis redis-cli BGSAVE
```

#### 数据恢复

```bash
# 恢复PostgreSQL
docker-compose exec -T postgres psql -U postgres flask_api_db < backup.sql

# 恢复MySQL
docker-compose exec -i mysql mysql -u root -p flask_api_db < mysql_backup.sql
```

### 安全配置

#### 1. 防火墙设置

```bash
# 配置UFW防火墙
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 5000
```

#### 2. SSL证书配置

```bash
# 自动续期SSL证书
sudo crontab -e
# 添加: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### 3. 定期更新

```bash
# 创建更新脚本
nano update.sh
#!/bin/bash
git pull
./deploy.sh build
./deploy.sh restart

# 设置定时任务
crontab -e
# 添加: 0 2 * * 0 /path/to/update.sh
```
