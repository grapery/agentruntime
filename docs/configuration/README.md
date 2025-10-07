# 配置文档

Flask API项目的详细配置说明。

## 目录

- [环境变量配置](#环境变量配置)
- [数据库配置](#数据库配置)
- [Redis配置](#redis配置)
- [Flask应用配置](#flask应用配置)
- [Docker配置](#docker配置)
- [Nginx配置](#nginx配置)
- [监控配置](#监控配置)

## 环境变量配置

### 基础配置

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| `FLASK_ENV` | 运行环境 | `development` | 否 |
| `SECRET_KEY` | 应用密钥 | `dev-secret-key` | 是 |
| `PORT` | 服务端口 | `5000` | 否 |
| `LOG_LEVEL` | 日志级别 | `INFO` | 否 |

### 示例配置

```bash
# .env文件示例
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
PORT=5000
LOG_LEVEL=INFO
```

## 数据库配置

### PostgreSQL配置

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| `POSTGRES_HOST` | 主机地址 | `localhost` | 否 |
| `POSTGRES_PORT` | 端口号 | `5432` | 否 |
| `POSTGRES_DB` | 数据库名 | `flask_api_db` | 否 |
| `POSTGRES_USER` | 用户名 | `postgres` | 否 |
| `POSTGRES_PASSWORD` | 密码 | `password` | 是 |

### MySQL配置

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| `MYSQL_HOST` | 主机地址 | `localhost` | 否 |
| `MYSQL_PORT` | 端口号 | `3306` | 否 |
| `MYSQL_DB` | 数据库名 | `flask_api_db` | 否 |
| `MYSQL_USER` | 用户名 | `root` | 否 |
| `MYSQL_PASSWORD` | 密码 | `password` | 是 |

### 数据库连接示例

```bash
# PostgreSQL连接字符串
postgresql://username:password@host:port/database

# MySQL连接字符串
mysql+pymysql://username:password@host:port/database
```

## Redis配置

### Redis参数

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| `REDIS_HOST` | 主机地址 | `localhost` | 否 |
| `REDIS_PORT` | 端口号 | `6379` | 否 |
| `REDIS_DB` | 数据库编号 | `0` | 否 |
| `REDIS_PASSWORD` | 密码 | 无 | 否 |

### Redis配置示例

```python
# config.py中的Redis配置
REDIS_CONFIG = {
    'host': os.environ.get('REDIS_HOST', 'localhost'),
    'port': int(os.environ.get('REDIS_PORT', '6379')),
    'db': int(os.environ.get('REDIS_DB', '0')),
    'password': os.environ.get('REDIS_PASSWORD', None),
    'decode_responses': True
}
```

## Flask应用配置

### 应用配置类

```python
class Config:
    """基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:password@localhost/flask_api_db'

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:password@localhost/flask_api_dev'

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
```

### 配置选择

```python
# 根据环境变量选择配置
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

app.config.from_object(config[os.environ.get('FLASK_ENV', 'default')])
```

## Docker配置

### Dockerfile配置

```dockerfile
# 基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 设置环境变量
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
```

### Docker Compose配置

#### 开发环境配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  flask-app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
    volumes:
      - .:/app
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: flask_api_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

#### 生产环境配置

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  flask-app:
    image: flask-api:latest
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - POSTGRES_HOST=postgres
      - REDIS_HOST=redis
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

volumes:
  postgres_data:
  redis_data:
```

## Nginx配置

### 基础配置

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream flask_app {
        server flask-app:5000;
    }

    server {
        listen 80;
        server_name _;

        location / {
            proxy_pass http://flask_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### 高级配置

```nginx
# 完整nginx.conf
events {
    worker_connections 1024;
}

http {
    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log;

    # 基本配置
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    client_max_body_size 20M;

    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    upstream flask_app {
        server flask-app:5000;
    }

    server {
        listen 80;
        server_name _;

        # 健康检查
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }

        # API请求
        location / {
            proxy_pass http://flask_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # 超时设置
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }

        # 静态文件缓存
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            proxy_pass http://flask_app;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

## 监控配置

### Prometheus配置

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'flask-app'
    static_configs:
      - targets: ['flask-app:5000']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
```

### Grafana配置

#### 数据源配置

```yaml
# monitoring/grafana/datasources/prometheus.yml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
```

#### 仪表板配置

```yaml
# monitoring/grafana/dashboards/dashboard.yml
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
```

## 安全配置

### 环境变量安全

```bash
# 生产环境密钥生成
python -c "import secrets; print(secrets.token_hex(32))"

# 设置强密码
export SECRET_KEY="your-generated-secret-key"
export POSTGRES_PASSWORD="your-strong-password"
export REDIS_PASSWORD="your-redis-password"
```

### SSL/TLS配置

```nginx
# HTTPS配置
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;

    location / {
        proxy_pass http://flask_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 性能配置

### Gunicorn配置

```python
# gunicorn.conf.py
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

### 数据库连接池配置

```python
# config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'pool_recycle': 120,
    'pool_pre_ping': True,
    'max_overflow': 20
}
```

### Redis连接池配置

```python
# config.py
REDIS_POOL = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    max_connections=20,
    retry_on_timeout=True
)
```

## 配置验证

### 配置检查脚本

```python
# scripts/check_config.py
import os
import sys
from config import Config

def check_config():
    """检查配置是否正确"""
    errors = []
    
    # 检查必需的环境变量
    required_vars = ['SECRET_KEY', 'POSTGRES_PASSWORD']
    for var in required_vars:
        if not os.environ.get(var):
            errors.append(f"缺少必需的环境变量: {var}")
    
    # 检查数据库连接
    try:
        from app import db
        db.engine.execute('SELECT 1')
        print("✅ 数据库连接正常")
    except Exception as e:
        errors.append(f"数据库连接失败: {e}")
    
    # 检查Redis连接
    try:
        from app import redis_client
        redis_client.ping()
        print("✅ Redis连接正常")
    except Exception as e:
        errors.append(f"Redis连接失败: {e}")
    
    if errors:
        print("❌ 配置检查失败:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("✅ 所有配置检查通过")

if __name__ == '__main__':
    check_config()
```

### 运行配置检查

```bash
# 检查配置
python scripts/check_config.py

# 或在Docker中检查
docker-compose exec flask-app python scripts/check_config.py
```
