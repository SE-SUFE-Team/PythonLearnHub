"""
Tools views
工具页面模块的视图
"""

from flask import Blueprint, render_template, request, jsonify
from app.utils.safe_executor import executor

# 创建工具蓝图
tools_bp = Blueprint('tools', __name__)


@tools_bp.route('/')
def tools():
    """工具页面"""
    return render_template('tools.html')


@tools_bp.route('/regex')
def regex_tool():
    """正则表达式工具"""
    return render_template('regex_tool.html')


@tools_bp.route('/code_playground')
def code_playground():
    """代码练习场"""
    return render_template('code_playground.html')


@tools_bp.route('/api/regex/test', methods=['POST'])
def test_regex():
    """正则表达式测试API"""
    try:
        data = request.get_json()
        pattern = data.get('pattern', '')
        test_string = data.get('test_string', '')
        function_name = data.get('function', 're.findall')
        flags = data.get('flags', '')
        replacement = data.get('replacement', 'X')
        
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


@tools_bp.route('/api/execute', methods=['POST'])
def execute_code():
    """执行Python代码API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '无效的请求数据'
            })
        
        code = data.get('code', '').strip()
        inputs = data.get('inputs', None)
        
        if not code:
            return jsonify({
                'success': False,
                'error': '代码不能为空'
            })
        
        # 执行代码
        result = executor.execute_code(code, inputs)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        })
