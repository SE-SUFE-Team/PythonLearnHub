"""
Functions views
函数模块的视图
"""

from flask import Blueprint, render_template, request, jsonify
from app.utils.content_manager import FUNCTION_CONTENT
from app.utils.safe_executor import executor

# 创建函数蓝图
functions_bp = Blueprint('functions', __name__)


@functions_bp.route('/')
def index():
    """函数主页"""
    return render_template('modules/functions.html', content=FUNCTION_CONTENT)


@functions_bp.route('/execute', methods=['POST'])
def execute_code():
    """执行代码"""
    code = request.json.get('code', '')
    
    # 检查代码安全性
    if not code.strip():
        return jsonify({"error": "代码不能为空"})
    
    # 执行代码
    result = executor.execute_code(code)
    return jsonify(result)


@functions_bp.route('/debug')
def debug():
    """调试页面"""
    return render_template('modules/functions_debug.html')


@functions_bp.route('/api/examples')
def get_examples():
    """获取函数示例"""
    examples = [
        {
            'title': '基本函数定义',
            'code': '''# 基本函数定义
def greet(name):
    """问候函数"""
    return f"你好, {name}!"

# 调用函数
message = greet("张三")
print(message)

# 带默认参数的函数
def introduce(name, age=18):
    return f"我叫{name}, 今年{age}岁"

print(introduce("李四"))
print(introduce("王五", 25))''',
            'description': '函数的基本定义和调用'
        },
        {
            'title': '函数参数类型',
            'code': '''# 多种参数类型
def flexible_func(pos_arg, default_arg="默认值", *args, **kwargs):
    print(f"位置参数: {pos_arg}")
    print(f"默认参数: {default_arg}")
    print(f"可变参数: {args}")
    print(f"关键字参数: {kwargs}")

# 调用示例
flexible_func("必需参数", "修改默认值", "额外1", "额外2", key1="值1", key2="值2")''',
            'description': '不同类型的函数参数'
        },
        {
            'title': '递归函数',
            'code': '''# 递归函数示例
def factorial(n):
    """计算阶乘"""
    if n <= 1:
        return 1
    else:
        return n * factorial(n - 1)

# 测试递归函数
print(f"5的阶乘: {factorial(5)}")
print(f"3的阶乘: {factorial(3)}")''',
            'description': '递归函数的使用'
        },
        {
            'title': 'lambda函数',
            'code': '''# lambda函数示例
# 基本lambda函数
square = lambda x: x ** 2
print(f"5的平方: {square(5)}")

# 在列表中使用lambda
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x ** 2, numbers))
print(f"平方数列表: {squared}")

# 过滤使用lambda
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(f"偶数列表: {evens}")''',
            'description': 'lambda函数的使用'
        }
    ]
    
    return jsonify(examples)
