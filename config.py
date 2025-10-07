"""
数据库配置文件
支持PostgreSQL、MySQL和Redis的配置管理
"""

import os
from typing import Dict, Any

class DatabaseConfig:
    """数据库配置类"""
    
    @staticmethod
    def get_postgres_config() -> Dict[str, Any]:
        """获取PostgreSQL配置"""
        return {
            'host': os.environ.get('POSTGRES_HOST', 'localhost'),
            'port': int(os.environ.get('POSTGRES_PORT', '5432')),
            'database': os.environ.get('POSTGRES_DB', 'flask_api_db'),
            'user': os.environ.get('POSTGRES_USER', 'postgres'),
            'password': os.environ.get('POSTGRES_PASSWORD', 'password'),
            'uri': f"postgresql://{os.environ.get('POSTGRES_USER', 'postgres')}:{os.environ.get('POSTGRES_PASSWORD', 'password')}@{os.environ.get('POSTGRES_HOST', 'localhost')}:{os.environ.get('POSTGRES_PORT', '5432')}/{os.environ.get('POSTGRES_DB', 'flask_api_db')}"
        }
    
    @staticmethod
    def get_mysql_config() -> Dict[str, Any]:
        """获取MySQL配置"""
        return {
            'host': os.environ.get('MYSQL_HOST', 'localhost'),
            'port': int(os.environ.get('MYSQL_PORT', '3306')),
            'database': os.environ.get('MYSQL_DB', 'flask_api_db'),
            'user': os.environ.get('MYSQL_USER', 'root'),
            'password': os.environ.get('MYSQL_PASSWORD', 'password'),
            'uri': f"mysql+pymysql://{os.environ.get('MYSQL_USER', 'root')}:{os.environ.get('MYSQL_PASSWORD', 'password')}@{os.environ.get('MYSQL_HOST', 'localhost')}:{os.environ.get('MYSQL_PORT', '3306')}/{os.environ.get('MYSQL_DB', 'flask_api_db')}"
        }
    
    @staticmethod
    def get_redis_config() -> Dict[str, Any]:
        """获取Redis配置"""
        return {
            'host': os.environ.get('REDIS_HOST', 'localhost'),
            'port': int(os.environ.get('REDIS_PORT', '6379')),
            'db': int(os.environ.get('REDIS_DB', '0')),
            'password': os.environ.get('REDIS_PASSWORD', None),
            'decode_responses': True
        }
