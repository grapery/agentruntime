"""
Flask应用启动脚本
支持开发和生产环境启动
"""

import os
from app import app, db
from models import User, Product, Order, LogEntry
from routes import api_bp

# 注册蓝图
app.register_blueprint(api_bp)

def init_database():
    """初始化数据库"""
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 创建示例数据（仅开发环境）
        if os.environ.get('FLASK_ENV') == 'development':
            create_sample_data()

def create_sample_data():
    """创建示例数据"""
    try:
        # 检查是否已有数据
        if User.query.first():
            print("数据库已有数据，跳过示例数据创建")
            return
        
        # 创建示例用户
        sample_users = [
            User(username='admin', email='admin@example.com', full_name='管理员'),
            User(username='user1', email='user1@example.com', full_name='用户1'),
            User(username='user2', email='user2@example.com', full_name='用户2')
        ]
        
        for user in sample_users:
            db.session.add(user)
        
        db.session.commit()
        
        # 创建示例产品
        sample_products = [
            Product(name='笔记本电脑', description='高性能笔记本电脑', price=5999.99, stock_quantity=10, category='电子产品'),
            Product(name='无线鼠标', description='蓝牙无线鼠标', price=99.99, stock_quantity=50, category='电子产品'),
            Product(name='机械键盘', description='青轴机械键盘', price=299.99, stock_quantity=20, category='电子产品')
        ]
        
        for product in sample_products:
            db.session.add(product)
        
        db.session.commit()
        
        print("✅ 示例数据创建成功")
        
    except Exception as e:
        print(f"❌ 示例数据创建失败: {e}")
        db.session.rollback()

if __name__ == '__main__':
    # 初始化数据库
    init_database()
    
    # 启动应用
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🚀 Flask API服务启动中...")
    print(f"📍 访问地址: http://localhost:{port}")
    print(f"🔧 调试模式: {'开启' if debug else '关闭'}")
    print(f"📊 API文档: http://localhost:{port}/api/health")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
