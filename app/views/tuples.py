"""
Tuples views
元组模块的视图
"""

from flask import Blueprint, render_template, request, jsonify
from app.utils.content_manager import TUPLE_CONTENT
from app.utils.safe_executor import executor

# 创建元组蓝图
tuples_bp = Blueprint('tuples', __name__)


@tuples_bp.route('/')
def index():
    """元组主页"""
    return render_template('modules/tuples.html', content=TUPLE_CONTENT)


@tuples_bp.route('/execute', methods=['POST'])
def execute_code():
    """代码执行路由"""
    try:
        data = request.get_json()
        code = data.get('code', '')
        
        if not code.strip():
            return jsonify({
                'success': False,
                'error': '请输入要执行的代码',
                'output': ''
            })
        
        # 执行代码
        result = executor.execute_code(code)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}',
            'output': ''
        })


@tuples_bp.route('/examples')
def get_examples():
    """获取示例代码"""
    examples = {
        'basic_tuple': {
            'title': '基本元组操作',
            'code': '''# 创建元组
my_tuple = (1, 2, 3, 4, 5)
print("元组内容:", my_tuple)
print("元组长度:", len(my_tuple))
print("第一个元素:", my_tuple[0])
print("最后一个元素:", my_tuple[-1])''',
            'description': '元组的基本操作'
        },
        'tuple_slicing': {
            'title': '元组切片',
            'code': '''# 元组切片操作
numbers = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
print("原元组:", numbers)
print("前5个元素:", numbers[:5])
print("后5个元素:", numbers[5:])
print("步长为2:", numbers[::2])
print("反向:", numbers[::-1])''',
            'description': '元组的切片操作'
        },
        'tuple_unpacking': {
            'title': '元组解包',
            'code': '''# 元组解包
point = (3, 4)
x, y = point
print(f"坐标: x={x}, y={y}")

# 多个变量交换
a, b = 10, 20
print(f"交换前: a={a}, b={b}")
a, b = b, a
print(f"交换后: a={a}, b={b}")''',
            'description': '元组解包和变量交换'
        },
        'nested_tuples': {
            'title': '嵌套元组',
            'code': '''# 嵌套元组
matrix = ((1, 2, 3), (4, 5, 6), (7, 8, 9))
print("矩阵:", matrix)
print("第一行:", matrix[0])
print("第二行第三列:", matrix[1][2])

# 遍历嵌套元组
for i, row in enumerate(matrix):
    print(f"第{i+1}行: {row}")''',
            'description': '嵌套元组的操作'
        },
        'tuple_comprehension': {
            'title': '元组生成式（生成器表达式）',
            'code': '''# 元组生成式实际上是生成器表达式
squares = tuple(x**2 for x in range(1, 6))
print("平方数元组:", squares)

# 过滤条件
even_squares = tuple(x**2 for x in range(1, 11) if x % 2 == 0)
print("偶数的平方:", even_squares)

# 从字符串生成
words = "hello world python"
lengths = tuple(len(word) for word in words.split())
print("单词长度:", lengths)''',
            'description': '元组生成式的使用'
        },
        'tuple_methods': {
            'title': '元组方法',
            'code': '''# 元组的方法
sample = (1, 2, 3, 2, 4, 2, 5)
print("原元组:", sample)
print("元素2出现次数:", sample.count(2))
print("元素3的索引:", sample.index(3))

# 元组比较
tuple1 = (1, 2, 3)
tuple2 = (1, 2, 4)
print("tuple1 < tuple2:", tuple1 < tuple2)
print("tuple1 == (1, 2, 3):", tuple1 == (1, 2, 3))''',
            'description': '元组的常用方法'
        }
    }
    
    return jsonify(examples)
