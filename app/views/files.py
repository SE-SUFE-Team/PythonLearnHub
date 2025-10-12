"""
Files views
文件操作模块的视图
"""

from flask import Blueprint, render_template, request, jsonify
from app.utils.content_manager import FILE_CONTENT
from app.utils.safe_executor import executor

# 创建文件蓝图
files_bp = Blueprint('files', __name__)


@files_bp.route('/')
def index():
    """文件操作主页"""
    return render_template('modules/files.html')


@files_bp.route('/text_operations')
def text_operations():
    """文本文件操作知识点"""
    return render_template('modules/text_operations.html')


@files_bp.route('/regex_guide')
def regex_guide():
    """正则表达式指南"""
    return render_template('modules/regex_guide.html')


@files_bp.route('/code_playground')
def code_playground():
    """代码练习场"""
    return render_template('modules/code_playground.html')


@files_bp.route('/execute_code', methods=['POST'])
def execute_code():
    """执行Python代码"""
    try:
        data = request.get_json()
        code = data.get('code', '')
        
        if not code.strip():
            return jsonify({"success": False, "error": "代码不能为空"})
        
        result = executor.execute_code(code)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"success": False, "error": f"执行错误: {str(e)}"})


@files_bp.route('/highlight_code', methods=['POST'])
def highlight_code():
    """代码高亮"""
    try:
        data = request.get_json()
        code = data.get('code', '')
        
        if not code.strip():
            return jsonify({"success": False, "error": "代码不能为空"})
        
        # 简单的代码高亮处理
        highlighted = f'<pre><code>{code}</code></pre>'
        
        return jsonify({
            "success": True, 
            "highlighted": highlighted
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": f"高亮错误: {str(e)}"})


@files_bp.route('/regex_test', methods=['POST'])
def regex_test():
    """正则表达式测试"""
    try:
        data = request.get_json()
        pattern = data.get('pattern', '')
        text = data.get('text', '')
        flags = data.get('flags', '')
        
        if not pattern:
            return jsonify({"success": False, "error": "正则表达式不能为空"})
        
        import re
        
        # 解析标志
        flag_value = 0
        if 'i' in flags.lower():
            flag_value |= re.IGNORECASE
        if 'm' in flags.lower():
            flag_value |= re.MULTILINE
        if 's' in flags.lower():
            flag_value |= re.DOTALL
        
        # 执行正则表达式匹配
        matches = []
        try:
            for match in re.finditer(pattern, text, flag_value):
                matches.append({
                    'match': match.group(),
                    'start': match.start(),
                    'end': match.end(),
                    'groups': match.groups()
                })
        except re.error as e:
            return jsonify({"success": False, "error": f"正则表达式错误: {str(e)}"})
        
        return jsonify({
            "success": True,
            "matches": matches,
            "count": len(matches)
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": f"测试错误: {str(e)}"})


@files_bp.route('/api/examples')
def get_examples():
    """获取文件操作示例"""
    examples = [
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
        },
        {
            'title': '文件路径操作',
            'code': '''# 文件路径操作示例
import os

# 模拟路径操作
current_dir = "."
filename = "test.txt"
full_path = os.path.join(current_dir, filename)

print(f"当前目录: {current_dir}")
print(f"文件名: {filename}")
print(f"完整路径: {full_path}")

# 路径信息
print(f"目录名: {os.path.dirname(full_path)}")
print(f"文件名: {os.path.basename(full_path)}")
print(f"文件扩展名: {os.path.splitext(filename)[1]}")''',
            'description': '文件路径的基本操作'
        }
    ]
    
    return jsonify(examples)
