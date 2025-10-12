"""
Variables and Data Types views
变量和数据类型模块的视图
"""

from flask import Blueprint, render_template, request, jsonify
from app.utils.content_manager import VARIABLES_CONTENT
from app.utils.safe_executor import executor

# 创建变量蓝图
variables_bp = Blueprint('variables', __name__)


@variables_bp.route('/')
def index():
    """变量和数据类型主页"""
    return render_template('modules/variables.html', content=VARIABLES_CONTENT)


@variables_bp.route('/execute', methods=['POST'])
def execute_code():
    """执行代码"""
    try:
        data = request.get_json()
        code = data.get('code', '').strip()
        
        if not code:
            return jsonify({
                'success': False,
                'error': '代码不能为空'
            })
        
        result = executor.execute_code(code)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'执行错误: {str(e)}'
        })


@variables_bp.route('/examples')
def get_examples():
    """获取示例代码"""
    examples = {
        "基本数据类型": [
            {
                "title": "整数 (int)",
                "code": "# 整数类型\nage = 25\nprint(f'年龄: {age}, 类型: {type(age)}')\nprint(f'年龄的两倍: {age * 2}')",
                "description": "整数是没有小数部分的数字"
            },
            {
                "title": "浮点数 (float)",
                "code": "# 浮点数类型\nheight = 175.5\nprint(f'身高: {height}, 类型: {type(height)}')\nprint(f'身高的平方: {height ** 2}')",
                "description": "浮点数是有小数部分的数字"
            },
            {
                "title": "字符串 (str)",
                "code": "# 字符串类型\nname = 'Python学习者'\nprint(f'姓名: {name}, 类型: {type(name)}')\nprint(f'姓名长度: {len(name)}')\nprint(f'大写: {name.upper()}')",
                "description": "字符串是字符的序列"
            },
            {
                "title": "布尔值 (bool)",
                "code": "# 布尔类型\nis_student = True\nis_working = False\nprint(f'是学生: {is_student}, 类型: {type(is_student)}')\nprint(f'在工作: {is_working}, 类型: {type(is_working)}')\nprint(f'逻辑与: {is_student and is_working}')",
                "description": "布尔值只有True和False两个值"
            }
        ],
        "集合数据类型": [
            {
                "title": "列表 (list)",
                "code": "# 列表类型\nfruits = ['苹果', '香蕉', '橙子']\nprint(f'水果列表: {fruits}, 类型: {type(fruits)}')\nfruits.append('葡萄')\nprint(f'添加葡萄后: {fruits}')\nprint(f'第一个水果: {fruits[0]}')",
                "description": "列表是有序且可变的元素集合"
            },
            {
                "title": "元组 (tuple)",
                "code": "# 元组类型\ncoordinates = (10, 20)\nprint(f'坐标: {coordinates}, 类型: {type(coordinates)}')\nprint(f'X坐标: {coordinates[0]}, Y坐标: {coordinates[1]}')\n# 元组是不可变的",
                "description": "元组是有序但不可变的元素集合"
            },
            {
                "title": "字典 (dict)",
                "code": "# 字典类型\nstudent = {'姓名': '小明', '年龄': 18, '成绩': 95}\nprint(f'学生信息: {student}, 类型: {type(student)}')\nname = student['姓名']\nprint(f'姓名: {name}')\nstudent['班级'] = '高三一班'\nprint(f'添加班级后: {student}')",
                "description": "字典是键值对的集合"
            },
            {
                "title": "集合 (set)",
                "code": "# 集合类型\nnumbers = {1, 2, 3, 3, 4, 4, 5}\nprint(f'数字集合: {numbers}, 类型: {type(numbers)}')\nnumbers.add(6)\nprint(f'添加6后: {numbers}')\nprint(f'集合长度: {len(numbers)}')",
                "description": "集合是无序且元素唯一的集合"
            }
        ],
        "变量操作": [
            {
                "title": "变量赋值和类型转换",
                "code": "# 变量赋值\nx = 10\ny = '20'\nz = 3.14\n\nprint(f'x = {x}, 类型: {type(x)}')\nprint(f'y = {y}, 类型: {type(y)}')\nprint(f'z = {z}, 类型: {type(z)}')\n\n# 类型转换\ny_int = int(y)\nz_str = str(z)\nprint(f'y转整数: {y_int}, 类型: {type(y_int)}')\nprint(f'z转字符串: {z_str}, 类型: {type(z_str)}')",
                "description": "演示变量赋值和基本类型转换"
            },
            {
                "title": "变量的作用域",
                "code": "# 全局变量\nglobal_var = '我是全局变量'\n\ndef show_scope():\n    # 局部变量\n    local_var = '我是局部变量'\n    print(f'函数内部 - 全局变量: {global_var}')\n    print(f'函数内部 - 局部变量: {local_var}')\n\nshow_scope()\nprint(f'函数外部 - 全局变量: {global_var}')\n# print(local_var)  # 这会报错，因为局部变量在函数外不可访问",
                "description": "演示变量的作用域概念"
            }
        ]
    }
    
    return jsonify(examples)
