"""
Configuration settings for Python Learning Platform
"""

import os
from datetime import timedelta


class Config:
    """基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'python_learning_platform_2024_secure_key'
    
    # 应用配置
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5000
    
    # 安全配置
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # 会话配置
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # 代码执行配置
    MAX_CODE_LENGTH = 10000
    EXECUTION_TIMEOUT = 30
    
    # 静态文件配置
    STATIC_FOLDER = 'app/static'
    TEMPLATE_FOLDER = 'app/templates'


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    PORT = 5000


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    PORT = 80


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DEBUG = True
    PORT = 5001


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
