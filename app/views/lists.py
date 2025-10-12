"""
Lists views
列表和列表生成式模块的视图
"""

from flask import Blueprint, render_template, request, jsonify
from app.utils.content_manager import LIST_CONTENT
from app.utils.safe_executor import executor

# 创建列表蓝图
lists_bp = Blueprint('lists', __name__)


@lists_bp.route('/')
def index():
    """列表主页"""
    return render_template('modules/lists.html', content=LIST_CONTENT)


@lists_bp.route('/execute', methods=['POST'])
def execute_code():
    """执行Python代码的API端点"""
    data = request.get_json()
    code = data.get('code', '')
    
    if not code.strip():
        return jsonify({"error": "请输入代码"})
    
    result = executor.execute_code(code)
    return jsonify(result)


@lists_bp.route('/examples')
def examples():
    """示例页面"""
    return render_template('modules/list_examples.html')


@lists_bp.route('/test')
def test():
    """测试页面"""
    return render_template('modules/list_test.html')


@lists_bp.route('/operator-test')
def operator_test():
    """操作符测试页面"""
    return render_template('modules/operator_test.html')


@lists_bp.route('/api/examples')
def get_examples():
    """获取列表示例"""
    examples = {
        "基本列表操作": [
            {
                "title": "列表创建和访问",
                "code": '''# 列表创建和访问
numbers = [1, 2, 3, 4, 5]
fruits = ['苹果', '香蕉', '橙子']
mixed = [1, 'hello', 3.14, True]

print(f"数字列表: {numbers}")
print(f"水果列表: {fruits}")
print(f"混合列表: {mixed}")
print(f"第一个数字: {numbers[0]}")
print(f"最后一个水果: {fruits[-1]}")''',
                "description": "列表的创建和元素访问"
            },
            {
                "title": "列表方法",
                "code": '''# 列表方法
fruits = ['苹果', '香蕉']
print(f"初始列表: {fruits}")

fruits.append('橙子')
print(f"添加橙子: {fruits}")

fruits.insert(1, '葡萄')
print(f"插入葡萄: {fruits}")

fruits.remove('香蕉')
print(f"删除香蕉: {fruits}")

last_fruit = fruits.pop()
print(f"弹出最后一个: {last_fruit}, 剩余: {fruits}")''',
                "description": "列表的常用方法"
            }
        ],
        "列表生成式": [
            {
                "title": "基础列表生成式",
                "code": '''# 基础列表生成式
# 生成平方数
squares = [x**2 for x in range(1, 6)]
print(f"平方数: {squares}")

# 生成偶数
evens = [x for x in range(1, 11) if x % 2 == 0]
print(f"偶数: {evens}")

# 字符串处理
words = ['hello', 'world', 'python']
upper_words = [word.upper() for word in words]
print(f"大写单词: {upper_words}")''',
                "description": "列表生成式的基本用法"
            },
            {
                "title": "复杂列表生成式",
                "code": '''# 复杂列表生成式
# 嵌套循环
matrix = [[i*j for j in range(1, 4)] for i in range(1, 4)]
print(f"乘法表矩阵: {matrix}")

# 条件表达式
numbers = range(-5, 6)
abs_even = [abs(x) if x % 2 == 0 else x for x in numbers]
print(f"处理后的数字: {abs_even}")

# 多条件过滤
filtered = [x for x in range(1, 21) if x % 2 == 0 if x % 3 == 0]
print(f"既是偶数又是3的倍数: {filtered}")''',
                "description": "复杂的列表生成式用法"
            }
        ]
    }
    
    return jsonify(examples)
