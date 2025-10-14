"""
Python Learning Platform - Flask Application Factory
统一的Python学习平台Flask应用
"""

from flask import Flask
from config import Config
from datetime import datetime


def create_app(config_class=Config):
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 注册蓝图
    from app.views.main import main_bp
    from app.views.variables import variables_bp
    from app.views.strings import strings_bp
    from app.views.tuples import tuples_bp
    from app.views.lists import lists_bp
    from app.views.flow_control import flow_control_bp
    from app.views.functions import functions_bp
    from app.views.exceptions import exceptions_bp
    from app.views.files import files_bp
    from app.views.regex import regex_bp
    from app.views.tools import tools_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(variables_bp, url_prefix='/variables')
    app.register_blueprint(strings_bp, url_prefix='/strings')
    app.register_blueprint(tuples_bp, url_prefix='/tuples')
    app.register_blueprint(lists_bp, url_prefix='/lists')
    app.register_blueprint(flow_control_bp, url_prefix='/flow-control')
    app.register_blueprint(functions_bp, url_prefix='/functions')
    app.register_blueprint(exceptions_bp, url_prefix='/exceptions')
    app.register_blueprint(files_bp, url_prefix='/files')
    app.register_blueprint(regex_bp, url_prefix='/regex')
    app.register_blueprint(tools_bp, url_prefix='/tools')
    
    # 注册错误处理器
    from app.views.main import register_error_handlers
    register_error_handlers(app)
    
    # 全局上下文处理器
    @app.context_processor
    def inject_navigation():
        """注入导航数据到所有模板"""
        from app.utils.content_manager import MODULE_NAVIGATION
        return dict(
            navigation_modules=MODULE_NAVIGATION,
            current_year=datetime.now().year
        )
    
    return app
