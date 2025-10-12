"""
Exceptions and Assertions views
异常和断言模块的视图
"""

from flask import Blueprint, render_template, request, jsonify
from app.utils.content_manager import EXCEPTION_ASSERTION_CONTENT
from app.utils.safe_executor import executor

# 创建异常蓝图
exceptions_bp = Blueprint('exceptions', __name__)


@exceptions_bp.route('/')
def index():
    """异常和断言主页"""
    return render_template('modules/exceptions.html', 
                         exception_examples=EXCEPTION_ASSERTION_CONTENT['exception_examples'],
                         assertion_examples=EXCEPTION_ASSERTION_CONTENT['assertion_examples'])


@exceptions_bp.route('/execute', methods=['POST'])
def execute_code():
    """执行代码"""
    if not request.json:
        return jsonify({
            'success': False,
            'error': '无效的请求数据',
            'output': ''
        })
    
    code = request.json.get('code', '')
    
    if not code.strip():
        return jsonify({
            'success': False,
            'error': '代码不能为空',
            'output': ''
        })
    
    result = executor.execute_code(code)
    
    return jsonify({
        'success': result['success'],
        'error': result.get('error', ''),
        'output': result.get('output', '')
    })


@exceptions_bp.route('/api/examples')
def get_examples():
    """获取异常和断言示例"""
    return jsonify({
        'exception_examples': EXCEPTION_ASSERTION_CONTENT['exception_examples'],
        'assertion_examples': EXCEPTION_ASSERTION_CONTENT['assertion_examples']
    })


@exceptions_bp.route('/highlight', methods=['POST'])
def highlight_code():
    """代码高亮"""
    if not request.json:
        return jsonify({'highlighted': ''})
    
    code = request.json.get('code', '')
    
    if not code.strip():
        return jsonify({'highlighted': ''})
    
    # 简单的代码高亮处理
    highlighted = f'<pre><code>{code}</code></pre>'
    
    return jsonify({'highlighted': highlighted})
