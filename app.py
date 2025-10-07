"""
Flask API应用主文件
提供HTTP API接口，支持Redis、PostgreSQL、MySQL数据库操作
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import redis
import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# 加载环境变量
load_dotenv()

# 初始化Flask应用
app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 配置数据库连接
class Config:
    """应用配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # PostgreSQL配置
    POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = os.environ.get('POSTGRES_PORT', '5432')
    POSTGRES_DB = os.environ.get('POSTGRES_DB', 'flask_api_db')
    POSTGRES_USER = os.environ.get('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'password')
    
    # MySQL配置
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = os.environ.get('MYSQL_PORT', '3306')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'flask_api_db')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'password')
    
    # Redis配置
    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', '6379'))
    REDIS_DB = int(os.environ.get('REDIS_DB', '0'))
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', None)
    
    # 默认使用PostgreSQL作为主数据库
    SQLALCHEMY_DATABASE_URI = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

app.config.from_object(Config)

# 初始化数据库
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# 初始化Redis连接
redis_client = redis.Redis(
    host=app.config['REDIS_HOST'],
    port=app.config['REDIS_PORT'],
    db=app.config['REDIS_DB'],
    password=app.config['REDIS_PASSWORD'],
    decode_responses=True
)

# 测试数据库连接
@app.before_first_request
def test_connections():
    """测试所有数据库连接"""
    try:
        # 测试PostgreSQL连接
        db.engine.execute('SELECT 1')
        print("✅ PostgreSQL连接成功")
    except Exception as e:
        print(f"❌ PostgreSQL连接失败: {e}")
    
    try:
        # 测试Redis连接
        redis_client.ping()
        print("✅ Redis连接成功")
    except Exception as e:
        print(f"❌ Redis连接失败: {e}")

# 数据库模型
class User(db.Model):
    """用户模型 - 存储在PostgreSQL中"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# API路由
@app.route('/')
def index():
    """首页"""
    return jsonify({
        'message': 'Flask API服务运行中',
        'version': '1.0.0',
        'databases': ['PostgreSQL', 'Redis', 'MySQL']
    })

@app.route('/api/users', methods=['GET'])
def get_users():
    """获取所有用户"""
    try:
        users = User.query.all()
        return jsonify({
            'success': True,
            'data': [user.to_dict() for user in users],
            'count': len(users)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/users', methods=['POST'])
def create_user():
    """创建新用户"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('email'):
            return jsonify({
                'success': False,
                'error': '用户名和邮箱是必填项'
            }), 400
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=data['username']).first():
            return jsonify({
                'success': False,
                'error': '用户名已存在'
            }), 400
        
        # 创建新用户
        user = User(
            username=data['username'],
            email=data['email']
        )
        
        db.session.add(user)
        db.session.commit()
        
        # 将用户信息缓存到Redis
        redis_client.setex(
            f"user:{user.id}",
            3600,  # 1小时过期
            str(user.to_dict())
        )
        
        return jsonify({
            'success': True,
            'data': user.to_dict(),
            'message': '用户创建成功'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id: int):
    """获取指定用户"""
    try:
        # 先从Redis缓存中查找
        cached_user = redis_client.get(f"user:{user_id}")
        if cached_user:
            return jsonify({
                'success': True,
                'data': eval(cached_user),  # 注意：生产环境中应使用json.loads
                'from_cache': True
            })
        
        # 从PostgreSQL中查找
        user = User.query.get_or_404(user_id)
        
        # 缓存到Redis
        redis_client.setex(
            f"user:{user_id}",
            3600,
            str(user.to_dict())
        )
        
        return jsonify({
            'success': True,
            'data': user.to_dict(),
            'from_cache': False
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/redis/test', methods=['GET'])
def test_redis():
    """测试Redis连接和操作"""
    try:
        # 设置测试数据
        redis_client.set('test_key', 'Hello Redis!')
        value = redis_client.get('test_key')
        
        return jsonify({
            'success': True,
            'message': 'Redis连接正常',
            'test_value': value
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Redis连接失败: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    health_status = {
        'status': 'healthy',
        'timestamp': db.func.current_timestamp(),
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

if __name__ == '__main__':
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    # 启动应用
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('FLASK_ENV') == 'development'
    )
