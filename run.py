"""
Python Learning Platform - Application Entry Point
"""

import os
from app import create_app
from config import DevelopmentConfig

# 创建应用实例
app = create_app(DevelopmentConfig)

if __name__ == '__main__':
    print("Python学习平台启动中...")
    print("访问 http://localhost:5000 开始学习")
    print("安全代码执行环境已启用")
    print("包含以下学习模块:")
    print("   - 变量和数据类型")
    print("   - 字符串操作")
    print("   - 元组")
    print("   - 列表和列表生成式")
    print("   - 流程控制")
    print("   - 函数")
    print("   - 异常和断言")
    print("   - 文件操作")
    print("   - 正则表达式")
    print("   - 工具页面")
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000
    )
