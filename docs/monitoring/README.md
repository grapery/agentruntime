# 监控文档

Flask API项目的监控和运维指南。

## 目录

- [监控概述](#监控概述)
- [Prometheus监控](#prometheus监控)
- [Grafana仪表板](#grafana仪表板)
- [日志管理](#日志管理)
- [健康检查](#健康检查)
- [告警配置](#告警配置)
- [性能监控](#性能监控)

## 监控概述

项目提供完整的监控解决方案：

- **Prometheus**: 指标收集和存储
- **Grafana**: 数据可视化和仪表板
- **Elasticsearch**: 日志存储
- **Kibana**: 日志分析和可视化

### 监控架构

```
应用服务 → Prometheus → Grafana
    ↓
应用日志 → Elasticsearch → Kibana
```

## Prometheus监控

### 启动Prometheus

```bash
# 启动包含监控的部署
./deploy.sh deploy-monitoring

# 或手动启动
docker-compose -f docker-compose.prod.yml --profile monitoring up -d
```

### 访问Prometheus

- **URL**: http://localhost:9090
- **功能**: 查看指标、配置告警规则、查询数据

### 监控指标

#### 应用指标

- `http_requests_total`: HTTP请求总数
- `http_request_duration_seconds`: 请求处理时间
- `active_connections`: 活跃连接数
- `database_connections`: 数据库连接数

#### 系统指标

- `cpu_usage_percent`: CPU使用率
- `memory_usage_bytes`: 内存使用量
- `disk_usage_percent`: 磁盘使用率
- `network_io_bytes`: 网络IO

#### 数据库指标

- `postgres_connections`: PostgreSQL连接数
- `postgres_queries_per_second`: 查询频率
- `redis_connected_clients`: Redis连接数
- `redis_memory_usage`: Redis内存使用

### 查询示例

```promql
# 请求率
rate(http_requests_total[5m])

# 平均响应时间
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])

# 错误率
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])

# 数据库连接数
postgres_connections

# Redis内存使用
redis_memory_usage_bytes
```

## Grafana仪表板

### 启动Grafana

```bash
# 启动包含监控的部署
./deploy.sh deploy-monitoring

# 访问Grafana
# URL: http://localhost:3000
# 用户名: admin
# 密码: admin (默认)
```

### 预配置仪表板

项目包含以下预配置仪表板：

1. **应用概览**: 整体应用状态
2. **API性能**: API响应时间和吞吐量
3. **数据库监控**: 数据库性能指标
4. **系统资源**: CPU、内存、磁盘使用情况
5. **错误监控**: 错误率和异常情况

### 自定义仪表板

#### 创建新仪表板

1. 登录Grafana
2. 点击"+" → "Dashboard"
3. 添加面板
4. 配置数据源为Prometheus
5. 编写查询语句

#### 面板配置示例

```json
{
  "title": "API请求率",
  "type": "graph",
  "targets": [
    {
      "expr": "rate(http_requests_total[5m])",
      "legendFormat": "{{method}} {{endpoint}}"
    }
  ],
  "yAxes": [
    {
      "label": "请求/秒",
      "min": 0
    }
  ]
}
```

## 日志管理

### 启动日志服务

```bash
# 启动包含日志的部署
./deploy.sh deploy-logging

# 或手动启动
docker-compose -f docker-compose.prod.yml --profile logging up -d
```

### 访问Kibana

- **URL**: http://localhost:5601
- **功能**: 日志搜索、分析、可视化

### 日志配置

#### 应用日志

```python
# 在app.py中配置日志
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('应用启动')
```

#### 日志格式

```python
# 结构化日志
import json
import logging

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        return json.dumps(log_entry)

# 使用JSON格式化器
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
```

### 日志查询

#### Kibana查询示例

```json
# 查询错误日志
{
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "level": "ERROR"
          }
        }
      ]
    }
  }
}

# 查询特定用户的请求
{
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "user_id": "123"
          }
        }
      ]
    }
  }
}
```

## 健康检查

### 应用健康检查

```python
# 在routes.py中实现健康检查
@app.route('/api/health')
def health_check():
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {}
    }
    
    # 检查PostgreSQL
    try:
        db.engine.execute('SELECT 1')
        health_status['services']['postgresql'] = 'healthy'
    except Exception as e:
        health_status['services']['postgresql'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    # 检查Redis
    try:
        redis_client.ping()
        health_status['services']['redis'] = 'healthy'
    except Exception as e:
        health_status['services']['redis'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    return jsonify(health_status)
```

### Docker健康检查

```dockerfile
# 在Dockerfile中添加健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1
```

### 监控健康检查

```bash
# 检查服务健康状态
curl http://localhost:5000/api/health

# 使用Prometheus监控健康检查
# 指标: up{job="flask-app"}
```

## 告警配置

### Prometheus告警规则

```yaml
# monitoring/alerts.yml
groups:
  - name: flask-api-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "高错误率告警"
          description: "错误率超过10%，当前值: {{ $value }}"

      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "响应时间过长"
          description: "95%的请求响应时间超过1秒"

      - alert: DatabaseDown
        expr: up{job="postgres"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "数据库服务不可用"
          description: "PostgreSQL服务已停止"

      - alert: RedisDown
        expr: up{job="redis"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Redis服务不可用"
          description: "Redis服务已停止"
```

### 告警通知

#### 邮件通知

```yaml
# monitoring/alertmanager.yml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@yourdomain.com'
  smtp_auth_username: 'alerts@yourdomain.com'
  smtp_auth_password: 'your-app-password'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
  - name: 'web.hook'
    email_configs:
      - to: 'admin@yourdomain.com'
        subject: 'Flask API告警: {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          告警: {{ .Annotations.summary }}
          描述: {{ .Annotations.description }}
          时间: {{ .StartsAt }}
          {{ end }}
```

#### Slack通知

```yaml
receivers:
  - name: 'slack-notifications'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
        channel: '#alerts'
        title: 'Flask API告警'
        text: |
          {{ range .Alerts }}
          *告警*: {{ .Annotations.summary }}
          *描述*: {{ .Annotations.description }}
          *时间*: {{ .StartsAt }}
          {{ end }}
```

## 性能监控

### 应用性能指标

```python
# 在app.py中添加性能监控
from prometheus_client import Counter, Histogram, generate_latest
import time

# 定义指标
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    # 记录请求指标
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.endpoint,
        status=response.status_code
    ).inc()
    
    # 记录响应时间
    REQUEST_DURATION.observe(time.time() - request.start_time)
    
    return response

@app.route('/metrics')
def metrics():
    return generate_latest()
```

### 数据库性能监控

```python
# 数据库查询监控
from sqlalchemy import event
from prometheus_client import Counter, Histogram

DB_QUERY_COUNT = Counter('db_queries_total', 'Total database queries', ['operation'])
DB_QUERY_DURATION = Histogram('db_query_duration_seconds', 'Database query duration')

@event.listens_for(db.engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(db.engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - context._query_start_time
    DB_QUERY_DURATION.observe(total)
    DB_QUERY_COUNT.labels(operation=statement.split()[0].upper()).inc()
```

### 系统资源监控

```python
# 系统资源监控
import psutil
from prometheus_client import Gauge

# 系统指标
CPU_USAGE = Gauge('system_cpu_usage_percent', 'CPU usage percentage')
MEMORY_USAGE = Gauge('system_memory_usage_bytes', 'Memory usage in bytes')
DISK_USAGE = Gauge('system_disk_usage_percent', 'Disk usage percentage')

def update_system_metrics():
    """更新系统指标"""
    CPU_USAGE.set(psutil.cpu_percent())
    MEMORY_USAGE.set(psutil.virtual_memory().used)
    DISK_USAGE.set(psutil.disk_usage('/').percent)

# 定期更新指标
import threading
def start_metrics_collection():
    def collect():
        while True:
            update_system_metrics()
            time.sleep(10)
    
    thread = threading.Thread(target=collect)
    thread.daemon = True
    thread.start()
```

## 监控最佳实践

### 1. 指标设计原则

- 使用有意义的指标名称
- 添加适当的标签
- 避免高基数指标
- 定期清理无用指标

### 2. 告警配置原则

- 设置合理的阈值
- 避免告警风暴
- 使用告警分组
- 提供清晰的告警信息

### 3. 日志管理原则

- 使用结构化日志
- 设置合理的日志级别
- 定期轮转日志文件
- 避免记录敏感信息

### 4. 性能优化

- 使用采样减少指标数量
- 优化查询性能
- 定期清理历史数据
- 监控监控系统本身

## 故障排查

### 常见监控问题

#### 1. Prometheus无法收集指标

```bash
# 检查目标状态
curl http://localhost:9090/api/v1/targets

# 检查指标端点
curl http://localhost:5000/metrics

# 查看Prometheus日志
docker-compose logs prometheus
```

#### 2. Grafana无法连接数据源

```bash
# 检查数据源配置
# 确认Prometheus URL正确
# 检查网络连接
curl http://prometheus:9090/api/v1/query?query=up
```

#### 3. 日志无法收集

```bash
# 检查Elasticsearch状态
curl http://localhost:9200/_cluster/health

# 检查日志配置
docker-compose logs elasticsearch
docker-compose logs kibana
```

### 监控系统维护

```bash
# 清理Prometheus数据
docker-compose exec prometheus rm -rf /prometheus/*

# 重启监控服务
docker-compose restart prometheus grafana

# 备份监控配置
docker-compose exec prometheus tar -czf /backup/prometheus-config.tar.gz /etc/prometheus/
```
