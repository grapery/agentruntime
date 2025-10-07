"""
API路由定义
提供用户、产品、订单等资源的CRUD操作
"""

from flask import Blueprint, request, jsonify
from models import db, User, Product, Order, LogEntry
import redis
from config import DatabaseConfig
from datetime import datetime
from typing import Dict, Any, Optional
import json

# 创建蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')

# 初始化Redis连接
redis_config = DatabaseConfig.get_redis_config()
redis_client = redis.Redis(**redis_config)

def log_request(level: str, message: str, user_id: Optional[int] = None):
    """记录请求日志到数据库"""
    try:
        log_entry = LogEntry(
            level=level,
            message=message,
            module=request.endpoint,
            user_id=user_id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        print(f"日志记录失败: {e}")

# 用户相关路由
@api_bp.route('/users', methods=['GET'])
def get_users():
    """获取所有用户列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        
        query = User.query
        if search:
            query = query.filter(
                (User.username.contains(search)) | 
                (User.email.contains(search)) |
                (User.full_name.contains(search))
            )
        
        users = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        log_request('INFO', f'获取用户列表，页码: {page}')
        
        return jsonify({
            'success': True,
            'data': [user.to_dict() for user in users.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': users.total,
                'pages': users.pages,
                'has_next': users.has_next,
                'has_prev': users.has_prev
            }
        })
        
    except Exception as e:
        log_request('ERROR', f'获取用户列表失败: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/users', methods=['POST'])
def create_user():
    """创建新用户"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['username', 'email']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'{field}是必填项'
                }), 400
        
        # 检查用户名和邮箱是否已存在
        if User.query.filter_by(username=data['username']).first():
            return jsonify({
                'success': False,
                'error': '用户名已存在'
            }), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({
                'success': False,
                'error': '邮箱已存在'
            }), 400
        
        # 创建新用户
        user = User(
            username=data['username'],
            email=data['email'],
            full_name=data.get('full_name'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(user)
        db.session.commit()
        
        # 缓存用户信息到Redis
        cache_key = f"user:{user.id}"
        redis_client.setex(cache_key, 3600, json.dumps(user.to_dict()))
        
        log_request('INFO', f'创建用户成功: {user.username}', user.id)
        
        return jsonify({
            'success': True,
            'data': user.to_dict(),
            'message': '用户创建成功'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        log_request('ERROR', f'创建用户失败: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id: int):
    """获取指定用户详情"""
    try:
        # 先从Redis缓存中查找
        cache_key = f"user:{user_id}"
        cached_user = redis_client.get(cache_key)
        
        if cached_user:
            log_request('INFO', f'从缓存获取用户: {user_id}')
            return jsonify({
                'success': True,
                'data': json.loads(cached_user),
                'from_cache': True
            })
        
        # 从数据库查找
        user = User.query.get_or_404(user_id)
        
        # 缓存到Redis
        redis_client.setex(cache_key, 3600, json.dumps(user.to_dict()))
        
        log_request('INFO', f'从数据库获取用户: {user_id}')
        
        return jsonify({
            'success': True,
            'data': user.to_dict(),
            'from_cache': False
        })
        
    except Exception as e:
        log_request('ERROR', f'获取用户失败: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id: int):
    """更新用户信息"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # 更新用户信息
        if 'username' in data:
            # 检查用户名是否已被其他用户使用
            existing_user = User.query.filter(
                User.username == data['username'],
                User.id != user_id
            ).first()
            if existing_user:
                return jsonify({
                    'success': False,
                    'error': '用户名已被其他用户使用'
                }), 400
            user.username = data['username']
        
        if 'email' in data:
            # 检查邮箱是否已被其他用户使用
            existing_user = User.query.filter(
                User.email == data['email'],
                User.id != user_id
            ).first()
            if existing_user:
                return jsonify({
                    'success': False,
                    'error': '邮箱已被其他用户使用'
                }), 400
            user.email = data['email']
        
        if 'full_name' in data:
            user.full_name = data['full_name']
        
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # 更新Redis缓存
        cache_key = f"user:{user_id}"
        redis_client.setex(cache_key, 3600, json.dumps(user.to_dict()))
        
        log_request('INFO', f'更新用户成功: {user.username}', user.id)
        
        return jsonify({
            'success': True,
            'data': user.to_dict(),
            'message': '用户更新成功'
        })
        
    except Exception as e:
        db.session.rollback()
        log_request('ERROR', f'更新用户失败: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id: int):
    """删除用户"""
    try:
        user = User.query.get_or_404(user_id)
        username = user.username
        
        # 删除用户的所有订单（可选，根据业务需求）
        Order.query.filter_by(user_id=user_id).delete()
        
        # 删除用户
        db.session.delete(user)
        db.session.commit()
        
        # 删除Redis缓存
        cache_key = f"user:{user_id}"
        redis_client.delete(cache_key)
        
        log_request('INFO', f'删除用户成功: {username}', user_id)
        
        return jsonify({
            'success': True,
            'message': '用户删除成功'
        })
        
    except Exception as e:
        db.session.rollback()
        log_request('ERROR', f'删除用户失败: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 产品相关路由
@api_bp.route('/products', methods=['GET'])
def get_products():
    """获取产品列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        category = request.args.get('category', '')
        search = request.args.get('search', '')
        
        query = Product.query
        if category:
            query = query.filter(Product.category == category)
        if search:
            query = query.filter(Product.name.contains(search))
        
        products = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        log_request('INFO', f'获取产品列表，页码: {page}')
        
        return jsonify({
            'success': True,
            'data': [product.to_dict() for product in products.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': products.total,
                'pages': products.pages,
                'has_next': products.has_next,
                'has_prev': products.has_prev
            }
        })
        
    except Exception as e:
        log_request('ERROR', f'获取产品列表失败: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/products', methods=['POST'])
def create_product():
    """创建新产品"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['name', 'price']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'{field}是必填项'
                }), 400
        
        # 创建新产品
        product = Product(
            name=data['name'],
            description=data.get('description'),
            price=data['price'],
            stock_quantity=data.get('stock_quantity', 0),
            category=data.get('category'),
            is_available=data.get('is_available', True)
        )
        
        db.session.add(product)
        db.session.commit()
        
        log_request('INFO', f'创建产品成功: {product.name}')
        
        return jsonify({
            'success': True,
            'data': product.to_dict(),
            'message': '产品创建成功'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        log_request('ERROR', f'创建产品失败: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Redis测试路由
@api_bp.route('/redis/test', methods=['GET'])
def test_redis():
    """测试Redis连接和操作"""
    try:
        # 设置测试数据
        test_key = 'test:connection'
        test_value = f'Redis连接测试 - {datetime.now().isoformat()}'
        
        redis_client.setex(test_key, 60, test_value)
        retrieved_value = redis_client.get(test_key)
        
        # 测试列表操作
        list_key = 'test:list'
        redis_client.lpush(list_key, 'item1', 'item2', 'item3')
        list_items = redis_client.lrange(list_key, 0, -1)
        
        # 测试哈希操作
        hash_key = 'test:hash'
        redis_client.hset(hash_key, mapping={
            'field1': 'value1',
            'field2': 'value2',
            'timestamp': datetime.now().isoformat()
        })
        hash_data = redis_client.hgetall(hash_key)
        
        # 清理测试数据
        redis_client.delete(test_key, list_key, hash_key)
        
        log_request('INFO', 'Redis连接测试成功')
        
        return jsonify({
            'success': True,
            'message': 'Redis连接正常',
            'test_results': {
                'string_operation': retrieved_value,
                'list_operation': list_items,
                'hash_operation': hash_data
            }
        })
        
    except Exception as e:
        log_request('ERROR', f'Redis连接测试失败: {str(e)}')
        return jsonify({
            'success': False,
            'error': f'Redis连接失败: {str(e)}'
        }), 500

# 健康检查路由
@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
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
