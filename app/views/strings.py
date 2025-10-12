"""
Strings views
字符串模块的视图
"""

from flask import Blueprint, render_template, request, jsonify
from app.utils.content_manager import STRING_CONTENT
from app.utils.safe_executor import executor

# 创建字符串蓝图
strings_bp = Blueprint('strings', __name__)


@strings_bp.route('/')
def index():
    """字符串主页"""
    return render_template('modules/strings.html', 
                         categories=STRING_CONTENT['categories'],
                         examples=STRING_CONTENT['examples'])


@strings_bp.route('/category/<category_name>')
def category_detail(category_name):
    """显示特定类别的字符串示例"""
    if category_name in STRING_CONTENT['categories']:
        category_examples = [ex for ex in STRING_CONTENT['examples'] if ex['category'] == category_name]
        return render_template('modules/string_category.html', 
                             category=STRING_CONTENT['categories'][category_name],
                             examples=category_examples)
    return "Category not found", 404


@strings_bp.route('/execute', methods=['POST'])
def execute_code():
    """执行用户提交的Python代码"""
    try:
        data = request.get_json()
        code = data.get('code', '').strip()
        
        if not code:
            return jsonify({'error': '代码不能为空'})
        
        # 使用安全执行器执行代码
        result = executor.execute_code(code)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': f'执行出错: {str(e)}',
            'output': '',
            'execution_time': 0
        })


@strings_bp.route('/api/examples')
def api_examples():
    """API接口返回所有字符串示例"""
    return jsonify({
        'categories': STRING_CONTENT['categories'],
        'examples': STRING_CONTENT['examples']
    })


@strings_bp.route('/help')
def help_page():
    """帮助页面"""
    return render_template('modules/string_help.html')
