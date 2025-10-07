# 开发文档

Flask API项目的开发指南和最佳实践。

## 目录

- [开发环境搭建](#开发环境搭建)
- [项目结构说明](#项目结构说明)
- [代码规范](#代码规范)
- [数据库设计](#数据库设计)
- [测试指南](#测试指南)
- [调试技巧](#调试技巧)
- [贡献指南](#贡献指南)

## 开发环境搭建

### 1. 环境要求

- Python 3.11+
- Conda 或 Miniconda
- Docker & Docker Compose
- Git

### 2. 快速搭建

```bash
# 克隆项目
git clone https://github.com/your-username/your-repo.git
cd your-repo

# 运行初始化脚本
./init.sh

# 或手动设置
conda env create -f environment.yml
conda activate flask-api-project
pip install -r requirements.txt
```

### 3. 开发环境启动

```bash
# 启动数据库服务
docker-compose up -d postgres mysql redis

# 启动应用
python run.py

# 或使用开发脚本
./start.sh
```

## 项目结构说明

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
├── monitoring/                 # 监控配置
└── docs/                       # 项目文档
```

### 核心文件说明

#### `app.py`
Flask应用的主入口文件，包含：
- 应用初始化
- 数据库配置
- Redis连接
- 基础路由

#### `models.py`
数据库模型定义，包含：
- User模型（用户）
- Product模型（产品）
- Order模型（订单）
- LogEntry模型（日志）

#### `routes.py`
API路由定义，包含：
- 用户管理接口
- 产品管理接口
- 系统接口（健康检查等）

#### `config.py`
数据库配置管理，包含：
- PostgreSQL配置
- MySQL配置
- Redis配置

## 代码规范

### 1. Python代码规范

#### 使用Black格式化代码

```bash
# 格式化所有Python文件
black .

# 检查格式
black --check .
```

#### 使用Flake8检查代码风格

```bash
# 检查代码风格
flake8 .

# 忽略特定错误
flake8 --ignore=E501,W503 .
```

#### 代码风格要求

- 使用4个空格缩进
- 行长度不超过88字符
- 使用有意义的变量名
- 添加适当的注释和文档字符串

### 2. 文件命名规范

- Python文件使用小写字母和下划线：`user_service.py`
- 类名使用大驼峰：`UserService`
- 函数和变量使用小写字母和下划线：`get_user_info`
- 常量使用大写字母和下划线：`MAX_RETRY_COUNT`

### 3. 注释规范

```python
def create_user(username: str, email: str) -> User:
    """
    创建新用户
    
    Args:
        username (str): 用户名
        email (str): 邮箱地址
        
    Returns:
        User: 创建的用户对象
        
    Raises:
        ValueError: 当用户名或邮箱格式不正确时
    """
    # 验证输入参数
    if not username or not email:
        raise ValueError("用户名和邮箱不能为空")
    
    # 创建用户对象
    user = User(username=username, email=email)
    
    return user
```

## 数据库设计

### 1. 数据库选择

- **PostgreSQL**: 主数据库，存储业务数据
- **MySQL**: 存储日志和缓存数据
- **Redis**: 缓存和会话存储

### 2. 模型设计原则

- 每个模型对应一个业务实体
- 使用合适的数据类型
- 添加必要的索引
- 设置外键关系

### 3. 数据库迁移

```bash
# 初始化迁移
flask db init

# 创建迁移文件
flask db migrate -m "添加用户表"

# 应用迁移
flask db upgrade

# 回滚迁移
flask db downgrade
```

### 4. 索引优化

```python
# 在模型中添加索引
class User(db.Model):
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
```

## 测试指南

### 1. 测试环境设置

```bash
# 安装测试依赖
pip install pytest pytest-flask pytest-cov

# 创建测试配置
cp env.example .env.test
```

### 2. 编写测试

```python
# tests/test_user_api.py
import pytest
from app import app, db
from models import User

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_create_user(client):
    """测试创建用户"""
    response = client.post('/api/users', json={
        'username': 'testuser',
        'email': 'test@example.com'
    })
    
    assert response.status_code == 201
    assert response.json['success'] == True
    assert response.json['data']['username'] == 'testuser'

def test_get_user(client):
    """测试获取用户"""
    # 先创建用户
    user = User(username='testuser', email='test@example.com')
    db.session.add(user)
    db.session.commit()
    
    # 获取用户
    response = client.get(f'/api/users/{user.id}')
    
    assert response.status_code == 200
    assert response.json['success'] == True
    assert response.json['data']['username'] == 'testuser'
```

### 3. 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_user_api.py

# 运行测试并生成覆盖率报告
pytest --cov=app --cov-report=html

# 运行测试并显示详细输出
pytest -v
```

### 4. 测试最佳实践

- 每个API端点都要有测试
- 测试正常情况和异常情况
- 使用fixture管理测试数据
- 保持测试的独立性
- 定期运行测试

## 调试技巧

### 1. 日志调试

```python
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def some_function():
    logger.debug("调试信息")
    logger.info("一般信息")
    logger.warning("警告信息")
    logger.error("错误信息")
```

### 2. Flask调试模式

```python
# 在app.py中启用调试模式
if __name__ == '__main__':
    app.run(debug=True)
```

### 3. 数据库调试

```python
# 启用SQL查询日志
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# 在代码中添加调试信息
def get_user(user_id):
    user = User.query.get(user_id)
    print(f"查询用户ID: {user_id}, 结果: {user}")
    return user
```

### 4. API调试

```bash
# 使用curl测试API
curl -X GET http://localhost:5000/api/health

# 使用Postman或Insomnia
# 导入API文档进行测试
```

## 贡献指南

### 1. 开发流程

1. Fork项目到自己的GitHub账户
2. 克隆Fork的项目到本地
3. 创建功能分支：`git checkout -b feature/new-feature`
4. 进行开发和测试
5. 提交更改：`git commit -m "Add new feature"`
6. 推送到Fork：`git push origin feature/new-feature`
7. 创建Pull Request

### 2. 提交规范

使用清晰的提交信息：

```bash
# 功能添加
git commit -m "feat: 添加用户注册功能"

# 错误修复
git commit -m "fix: 修复用户登录验证问题"

# 文档更新
git commit -m "docs: 更新API文档"

# 代码重构
git commit -m "refactor: 重构用户服务代码"
```

### 3. Pull Request规范

- 提供清晰的描述
- 包含相关的测试
- 确保代码通过所有检查
- 更新相关文档

### 4. 代码审查

- 检查代码风格
- 验证功能正确性
- 确保测试覆盖
- 检查安全性

## 性能优化

### 1. 数据库优化

```python
# 使用连接池
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)

# 使用索引
db.Index('idx_user_email', User.email)
```

### 2. 缓存优化

```python
# Redis缓存
import redis
from functools import wraps

def cache_result(expiration=3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            return result
        return wrapper
    return decorator

@cache_result(expiration=1800)
def get_user_profile(user_id):
    return User.query.get(user_id)
```

### 3. API优化

```python
# 分页查询
def get_users(page=1, per_page=10):
    return User.query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

# 批量操作
def create_users_batch(users_data):
    users = [User(**data) for data in users_data]
    db.session.add_all(users)
    db.session.commit()
    return users
```

## 安全最佳实践

### 1. 输入验证

```python
from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=20))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))

def create_user():
    schema = UserSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400
```

### 2. SQL注入防护

```python
# 使用参数化查询
user = User.query.filter_by(username=username).first()

# 避免直接拼接SQL
# 错误示例：User.query.filter(f"username = '{username}'")
```

### 3. 认证和授权

```python
from functools import wraps
from flask import request, jsonify

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': '缺少认证令牌'}), 401
        
        # 验证token
        user = verify_token(token)
        if not user:
            return jsonify({'error': '无效的认证令牌'}), 401
        
        return f(user, *args, **kwargs)
    return decorated_function
```
