"""
Regex views
正则表达式模块的视图
"""

from flask import Blueprint, render_template, request, jsonify
from app.utils.content_manager import REGEX_CONTENT
from app.utils.safe_executor import executor

# 创建正则表达式蓝图
regex_bp = Blueprint('regex', __name__)


@regex_bp.route('/')
def index():
    """正则表达式主页"""
    return render_template('modules/regex.html', content=REGEX_CONTENT)


@regex_bp.route('/test_regex', methods=['POST'])
def test_regex():
    """正则表达式测试"""
    try:
        data = request.get_json()
        pattern = data.get('pattern', '')
        test_string = data.get('test_string', '')
        function_name = data.get('function', 're.findall')
        flags = data.get('flags', '')
        replacement = data.get('replacement', 'X')
        
        # 安全性检查
        if not pattern or not test_string:
            return jsonify({'error': '模式和测试字符串不能为空'})
        
        # 限制模式长度
        if len(pattern) > 1000:
            return jsonify({'error': '正则表达式模式过长'})
        
        import re
        
        # 解析flags
        flag_value = 0
        if flags:
            for flag in flags.split('|'):
                flag = flag.strip()
                if hasattr(re, flag):
                    flag_value |= getattr(re, flag)
        
        # 执行正则表达式
        result = {}
        try:
            compiled_pattern = re.compile(pattern, flag_value)
        except re.error as e:
            return jsonify({'error': f'正则表达式语法错误: {str(e)}'})
        
        if function_name == 're.match':
            match = compiled_pattern.match(test_string)
            result['result'] = match.group() if match else None
            result['groups'] = match.groups() if match else []
            result['span'] = match.span() if match else None
        elif function_name == 're.search':
            match = compiled_pattern.search(test_string)
            result['result'] = match.group() if match else None
            result['groups'] = match.groups() if match else []
            result['span'] = match.span() if match else None
        elif function_name == 're.findall':
            result['result'] = compiled_pattern.findall(test_string)
        elif function_name == 're.finditer':
            matches = list(compiled_pattern.finditer(test_string))
            result['result'] = [{'match': m.group(), 'span': m.span(), 'groups': m.groups()} for m in matches]
        elif function_name == 're.split':
            result['result'] = compiled_pattern.split(test_string)
        elif function_name == 're.sub':
            result['result'] = compiled_pattern.sub(replacement, test_string)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'执行错误: {str(e)}'})


@regex_bp.route('/execute_code', methods=['POST'])
def execute_code():
    """执行代码"""
    try:
        data = request.get_json()
        code = data.get('code', '')
        
        if not code:
            return jsonify({'error': '代码不能为空'})
        
        # 安全性检查
        dangerous_keywords = ['import os', 'import sys', 'exec', 'eval', 'open', '__import__', 'file', 'input']
        for keyword in dangerous_keywords:
            if keyword in code.lower():
                return jsonify({'error': f'出于安全考虑，不允许使用 "{keyword}"'})
        
        # 限制代码长度
        if len(code) > 5000:
            return jsonify({'error': '代码长度过长'})
        
        result = executor.execute_code(code)
        return jsonify(result)
            
    except Exception as e:
        return jsonify({'error': f'处理请求时发生错误: {str(e)}'})


@regex_bp.route('/api/examples')
def get_examples():
    """获取正则表达式示例"""
    examples = [
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
        },
        {
            'title': '常用正则模式',
            'code': '''import re

# 常用正则模式示例
text = """
姓名: 张三, 年龄: 25, 邮箱: zhangsan@example.com
电话: 138-0000-1234, 身份证: 110101199001011234
"""

# 匹配邮箱
emails = re.findall(r'\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b', text)
print(f"邮箱: {emails}")

# 匹配电话号码
phones = re.findall(r'\\d{3}-\\d{4}-\\d{4}', text)
print(f"电话: {phones}")

# 匹配身份证号
ids = re.findall(r'\\d{18}', text)
print(f"身份证: {ids}")

# 匹配姓名
names = re.findall(r'姓名: ([^,]+)', text)
print(f"姓名: {names}")''',
            'description': '常用的正则表达式模式'
        }
    ]
    
    return jsonify(examples)
