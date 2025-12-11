"""
Python学习平台 - 整合所有模块的内容数据
包含所有Python学习主题的知识点、示例代码和练习
"""

# ======================== 变量和数据类型 ========================
VARIABLES_CONTENT = {
    'title': 'Python变量和数据类型',
    'description': '学习Python的基本变量概念和数据类型',
    'topics': {
        'basic_types': {
            'title': '基本数据类型',
            'examples': [
                {
                    'title': '整数 (int)',
                    'code': '''# 整数类型
age = 25
print(f'年龄: {age}, 类型: {type(age)}')
print(f'年龄的两倍: {age * 2}')''',
                    'description': '整数是没有小数部分的数字'
                },
                {
                    'title': '浮点数 (float)',
                    'code': '''# 浮点数类型
height = 175.5
print(f'身高: {height}, 类型: {type(height)}')
print(f'身高的平方: {height ** 2}')''',
                    'description': '浮点数是有小数部分的数字'
                },
                {
                    'title': '字符串 (str)',
                    'code': '''# 字符串类型
name = 'Python学习者'
print(f'姓名: {name}, 类型: {type(name)}')
print(f'姓名长度: {len(name)}')
print(f'大写: {name.upper()}')''',
                    'description': '字符串是字符的序列'
                },
                {
                    'title': '布尔值 (bool)',
                    'code': '''# 布尔类型
is_student = True
is_working = False
print(f'是学生: {is_student}, 类型: {type(is_student)}')
print(f'在工作: {is_working}, 类型: {type(is_working)}')
print(f'逻辑与: {is_student and is_working}')''',
                    'description': '布尔值只有True和False两个值'
                }
            ]
        },
        'collection_types': {
            'title': '集合数据类型',
            'examples': [
                {
                    'title': '列表 (list)',
                    'code': '''# 列表类型
fruits = ['苹果', '香蕉', '橙子']
print(f'水果列表: {fruits}, 类型: {type(fruits)}')
fruits.append('葡萄')
print(f'添加葡萄后: {fruits}')
print(f'第一个水果: {fruits[0]}')''',
                    'description': '列表是有序且可变的元素集合'
                },
                {
                    'title': '元组 (tuple)',
                    'code': '''# 元组类型
coordinates = (10, 20)
print(f'坐标: {coordinates}, 类型: {type(coordinates)}')
print(f'X坐标: {coordinates[0]}, Y坐标: {coordinates[1]}')
# 元组是不可变的''',
                    'description': '元组是有序但不可变的元素集合'
                },
                {
                    'title': '字典 (dict)',
                    'code': '''# 字典类型
student = {'姓名': '小明', '年龄': 18, '成绩': 95}
print(f'学生信息: {student}, 类型: {type(student)}')
name = student['姓名']
print(f'姓名: {name}')
student['班级'] = '高三一班'
print(f'添加班级后: {student}')''',
                    'description': '字典是键值对的集合'
                },
                {
                    'title': '集合 (set)',
                    'code': '''# 集合类型
numbers = {1, 2, 3, 3, 4, 4, 5}
print(f'数字集合: {numbers}, 类型: {type(numbers)}')
numbers.add(6)
print(f'添加6后: {numbers}')
print(f'集合长度: {len(numbers)}')''',
                    'description': '集合是无序且元素唯一的集合'
                }
            ]
        }
    }
}

# ======================== 字符串 ========================
STRING_CONTENT = {
    'title': 'Python字符串操作',
    'description': '学习Python字符串的各种操作方法',
    'categories': {
        'basic_operations': '基本字符串操作',
        'formatting': '字符串格式化',
        'methods': '字符串方法',
        'slicing': '字符串切片'
    },
    'examples': [
        {
            'title': '字符串创建和基本操作',
            'category': 'basic_operations',
            'code': '''# 字符串创建
text1 = "Hello, World!"
text2 = 'Python编程'
text3 = """多行字符串
可以换行
非常方便"""

print(f"text1: {text1}")
print(f"text2: {text2}")
print(f"text3: {text3}")
print(f"字符串连接: {text1 + ' ' + text2}")''',
            'description': '演示字符串的创建和基本操作'
        },
        {
            'title': '字符串格式化',
            'category': 'formatting',
            'code': '''# 字符串格式化方法
name = "张三"
age = 25
score = 95.5

# f-string格式化 (推荐)
print(f"姓名: {name}, 年龄: {age}, 成绩: {score:.1f}")

# format方法
print("姓名: {}, 年龄: {}, 成绩: {:.1f}".format(name, age, score))

# %格式化
print("姓名: %s, 年龄: %d, 成绩: %.1f" % (name, age, score))''',
            'description': '不同的字符串格式化方法'
        },
        {
            'title': '字符串方法',
            'category': 'methods',
            'code': '''# 字符串常用方法
text = "  Hello, Python World!  "
print(f"原字符串: '{text}'")
print(f"去除空格: '{text.strip()}'")
print(f"转大写: '{text.upper()}'")
print(f"转小写: '{text.lower()}'")
print(f"替换: '{text.replace('Python', 'Java')}'")
print(f"分割: {text.strip().split(', ')}")
print(f"查找: {text.find('Python')}")''',
            'description': '字符串的常用方法'
        },
        {
            'title': '字符串切片',
            'category': 'slicing',
            'code': '''# 字符串切片
text = "Python编程学习"
print(f"原字符串: {text}")
print(f"前3个字符: {text[:3]}")
print(f"后3个字符: {text[-3:]}")
print(f"中间部分: {text[2:6]}")
print(f"步长为2: {text[::2]}")
print(f"反转字符串: {text[::-1]}")''',
            'description': '字符串的切片操作'
        }
    ]
}

# ======================== 列表和列表生成式 ========================
LIST_CONTENT = {
    'title': 'Python列表和列表生成式',
    'description': '学习Python列表的操作和列表生成式',
    'topics': {
        'basic_operations': {
            'title': '列表基本操作',
            'examples': [
                {
                    'title': '列表创建和访问',
                    'code': '''# 列表创建和访问
numbers = [1, 2, 3, 4, 5]
fruits = ['苹果', '香蕉', '橙子']
mixed = [1, 'hello', 3.14, True]

print(f"数字列表: {numbers}")
print(f"水果列表: {fruits}")
print(f"混合列表: {mixed}")
print(f"第一个数字: {numbers[0]}")
print(f"最后一个水果: {fruits[-1]}")''',
                    'description': '列表的创建和元素访问'
                },
                {
                    'title': '列表方法',
                    'code': '''# 列表方法
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
                    'description': '列表的常用方法'
                }
            ]
        },
        'list_comprehension': {
            'title': '列表生成式',
            'examples': [
                {
                    'title': '基础列表生成式',
                    'code': '''# 基础列表生成式
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
                    'description': '列表生成式的基本用法'
                },
                {
                    'title': '复杂列表生成式',
                    'code': '''# 复杂列表生成式
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
                    'description': '复杂的列表生成式用法'
                }
            ]
        }
    }
}

# ======================== 元组 ========================
TUPLE_CONTENT = {
    'title': 'Python元组',
    'description': '学习Python元组的操作和使用',
    'examples': {
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
        }
    }
}

# ======================== 流程控制 ========================
FLOW_CONTROL_CONTENT = {
    'title':'流程控制',
    'description':'学习流程控制',
    'topics':{
        'conditional': {
            'title': '条件语句',
            'description': '学习if、elif、else条件语句的使用',
            'examples': [
                {
                    'title': 'if语句基础',
                    'code': '''# if语句基础
age = 18
if age >= 18:
    print("你已经成年了")
else:
    print("你还未成年")

# elif多分支
score = 85
if score >= 90:
    print("优秀")
elif score >= 80:
    print("良好")
elif score >= 60:
    print("及格")
else:
    print("不及格")''',
                    'description': 'if条件语句的基本使用'
                }
            ]
    },
        'loops': {
            'title': '循环语句',
            'description': '学习for和while循环的使用',
            'examples': [
                {
                    'title': 'for循环',
                    'code': '''# for循环遍历
fruits = ['苹果', '香蕉', '橙子']
for fruit in fruits:
    print(f"我喜欢{fruit}")

# range函数
for i in range(1, 6):
    print(f"数字: {i}")

# enumerate获取索引
for index, fruit in enumerate(fruits):
    print(f"{index}: {fruit}")''',
                    'description': 'for循环的各种用法'
                },
                {
                    'title': 'while循环',
                    'code': '''# while循环
count = 0
while count < 5:
    print(f"计数: {count}")
    count += 1

# break和continue
for i in range(10):
    if i == 3:
        continue  # 跳过3
    if i == 7:
        break     # 在7处结束
print(f"当前数字: {i}")''',
                    'description': 'while循环和控制语句'
                }
            ]
    }
    }
}

# ======================== 函数 ========================
FUNCTION_CONTENT = {
    'title': 'Python函数',
    'description': '学习Python函数的定义和使用',
    'examples': [
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
        }
    ]
}

# ======================== 异常和断言 ========================
EXCEPTION_ASSERTION_CONTENT = {
    'title': 'Python异常处理和断言',
    'description': '学习异常处理和断言的使用',
    'topics':{
            'basic_exceptions': {
                'title': '基本异常类型',
                'examples': [
                    {
                        'title': 'ValueError',
                        'description': '当传递给函数的参数类型正确但值不正确时抛出',
                        'code': '''# ValueError 示例
try:
    num = int("abc")  # 字符串无法转换为整数
except ValueError as e:
    print(f"发生ValueError: {e}")

# 另一个例子
try:
    import math
    result = math.sqrt(-1)  # 负数不能开平方根
except ValueError as e:
    print(f"数学错误: {e}")'''
                    },
                    {
                        'title': 'TypeError',
                        'description': '当对象类型不支持某种操作时抛出',
                        'code': '''# TypeError 示例
try:
    result = "5" + 5  # 字符串和数字不能直接相加
except TypeError as e:
    print(f"发生TypeError: {e}")

# 另一个例子
try:
    len(123)  # len()不能用于整数
except TypeError as e:
    print(f"类型错误: {e}")'''
                    }
                ]
            }
        ,
            'basic_assertions': {
                'title': '基本断言用法',
                'examples': [
                    {
                        'title': '基本assert语句',
                        'description': '使用assert进行条件检查',
                        'code': '''# 基本断言示例
def calculate_square_root(x):
    assert x >= 0, "输入值必须非负"
    return x ** 0.5

# 测试断言
try:
    result1 = calculate_square_root(16)
    print(f"√16 = {result1}")

    result2 = calculate_square_root(-4)  # 触发断言错误
except AssertionError as e:
    print(f"断言错误: {e}")'''
                    }
                ]
            }
        }
}

# ======================== 文件操作 ========================
FILE_CONTENT = {
    'title': 'Python文件操作',
    'description': '学习Python文件读写和操作',
    'examples': [
        {
            'title': '文件读写基础',
            'code': '''# 文件读写示例（模拟）
# 注意：在Web环境中不能真实操作文件

# 模拟文件内容
file_content = """第一行内容
第二行内容
第三行内容"""

print("模拟文件内容:")
print(file_content)

# 模拟按行处理
lines = file_content.split('\\n')
for i, line in enumerate(lines, 1):
    print(f"第{i}行: {line}")''',
            'description': '文件读写的基本操作'
        }
    ]
}

# ======================== 正则表达式 ========================
REGEX_CONTENT = {
    'title': 'Python正则表达式',
    'description': '学习正则表达式在Python中的使用',
    'examples': [
        {
            'title': '基础正则匹配',
            'code': '''import re

# 基础匹配
text = "我的电话是138-0000-1234"
pattern = r"\\d{3}-\\d{4}-\\d{4}"
match = re.search(pattern, text)

if match:
    print(f"找到电话号码: {match.group()}")
else:
    print("未找到匹配")

# 查找所有匹配
text2 = "邮箱: test@qq.com 和 admin@163.com"
emails = re.findall(r"\\w+@\\w+\\.\\w+", text2)
print(f"找到的邮箱: {emails}")''',
            'description': '正则表达式的基本使用'
        },
        {
            'title': '正则替换',
            'code': '''import re

# 替换操作
text = "今天是2024年1月1日"
# 将日期格式从YYYY年MM月DD日改为YYYY-MM-DD
new_text = re.sub(r"(\\d{4})年(\\d{1,2})月(\\d{1,2})日", r"\\1-\\2-\\3", text)
print(f"原文: {text}")
print(f"替换后: {new_text}")

# 分割字符串
data = "苹果,香蕉;橙子:葡萄"
fruits = re.split(r"[,;:]", data)
print(f"分割结果: {fruits}")''',
            'description': '正则表达式的替换和分割'
        }
    ]
}

# ======================== 整合所有内容 ========================
ALL_MODULES = {
    'variables': VARIABLES_CONTENT,
    'strings': STRING_CONTENT,
    'lists': LIST_CONTENT,
    'tuples': TUPLE_CONTENT,
    'flow_control': FLOW_CONTROL_CONTENT,
    'functions': FUNCTION_CONTENT,
    'exceptions': EXCEPTION_ASSERTION_CONTENT,
    'files': FILE_CONTENT,
    'regex': REGEX_CONTENT
}

# 模块导航信息
MODULE_NAVIGATION = [
    {
        'id': 'variables',
        'title': 'Python变量和数据类型',
        'description': '学习Python的基本变量概念和数据类型',
        'icon': '🔢',
        'difficulty': '入门'
    },
    {
        'id': 'strings',
        'title': 'Python字符串',
        'description': '掌握字符串的各种操作方法',
        'icon': '📝',
        'difficulty': '入门'
    },
    {
        'id': 'lists',
        'title': 'Python列表和列表生成式',
        'description': '学习列表操作和列表生成式',
        'icon': '📋',
        'difficulty': '基础'
    },
    {
        'id': 'tuples',
        'title': 'Python元组',
        'description': '了解元组的特性和使用场景',
        'icon': '📦',
        'difficulty': '基础'
    },
    {
        'id': 'flow_control',
        'title': 'Python流程控制',
        'description': '掌握条件语句和循环语句',
        'icon': '🔄',
        'difficulty': '基础'
    },
    {
        'id': 'functions',
        'title': 'Python函数',
        'description': '学习函数的定义和使用',
        'icon': '⚡',
        'difficulty': '中级'
    },
    {
        'id': 'exceptions',
        'title': 'Python异常和断言',
        'description': '学习异常处理和断言使用',
        'icon': '⚠️',
        'difficulty': '中级'
    },
    {
        'id': 'files',
        'title': 'Python文件操作',
        'description': '学习文件读写和处理',
        'icon': '📁',
        'difficulty': '中级'
    },
    {
        'id': 'regex',
        'title': 'Python正则表达式',
        'description': '掌握正则表达式的使用',
        'icon': '🔍',
        'difficulty': '高级'
    }
]