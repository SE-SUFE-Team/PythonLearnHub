"""
Python学习平台 - 主应用
整合所有Python学习模块的Web应用
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from utils.safe_executor import executor
from utils.module_content import ALL_MODULES, MODULE_NAVIGATION
import re
import json
import traceback
from datetime import datetime
from models import db
from models.user import User
from models.code_execution import CodeExecution
from sqlalchemy import desc

app = Flask(__name__)
app.config['SECRET_KEY'] = 'python_learning_platform_2024'

# SQLite 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ======================== 数据库 ========================

db.init_app(app)

with app.app_context():
    db.create_all()
    # 插入测试用户
    if not User.query.filter_by(username='testuser').first():
        test_user = User(
            id=1,
            username='testuser',
            email='test@example.com',
            password_hash='123456'
        )
        db.session.add(test_user)
        db.session.commit()
        print("✅ 数据库表测试，testuser已插入")

    # 查询用户验证
    users = User.query.all()
    for u in users:
        print(u)

# ======================== 主页和导航 ========================

@app.route('/')
def index():
    """主页"""
    return render_template('index.html', modules=MODULE_NAVIGATION)

@app.route('/about')
def about():
    """关于页面"""
    return render_template('about.html')

# ======================== 模块页面路由 ========================

@app.route('/module/<module_id>')
def module_detail(module_id):
    """模块详情页面"""
    if module_id in ALL_MODULES:
        module_data = ALL_MODULES[module_id]
        module_info = next((m for m in MODULE_NAVIGATION if m['id'] == module_id), None)
        return render_template('module_detail.html', 
                             module=module_data, 
                             module_info=module_info,
                             module_id=module_id)
    else:
        return "模块不存在", 404

@app.route('/module/<module_id>/topic/<topic_id>')
def topic_detail(module_id, topic_id):
    """主题详情页面"""
    if module_id in ALL_MODULES:
        module_data = ALL_MODULES[module_id]
        if 'topics' in module_data and topic_id in module_data['topics']:
            topic_data = module_data['topics'][topic_id]
            module_info = next((m for m in MODULE_NAVIGATION if m['id'] == module_id), None)
            return render_template('topic_detail.html',
                                 topic=topic_data,
                                 topic_id=topic_id,
                                 module=module_data,
                                 module_info=module_info,
                                 module_id=module_id)
    return "主题不存在", 404

# ======================== 代码执行API ========================

@app.route('/api/execute', methods=['POST'])
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
        user_id = data.get('user_id')
        
        if not code:
            return jsonify({
                'success': False,
                'error': '代码不能为空'
            })
        
        # 执行代码
        result = executor.execute_code(code, inputs)
        
        # 添加执行时间戳
        result['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            execution_record = CodeExecution(
                user_id=user_id,
                code=code,
                record_type=0  # 通用历史记录
            )
            db.session.add(execution_record)

            # 保持该用户最多10条记录
            user_count = CodeExecution.query.filter_by(user_id=user_id).count()
            if user_count > 10:
                # 删除该用户最旧的记录
                oldest_records = CodeExecution.query.filter_by(
                    user_id=user_id
                ).order_by(
                    CodeExecution.executed_at
                ).limit(user_count - 10).all()
                for record in oldest_records:
                    db.session.delete(record)

            db.session.commit()
            result['record_id'] = execution_record.id
        except Exception as db_error:
            db.session.rollback()
            print(f"⚠️ 保存执行历史失败: {str(db_error)}")

        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}',
            'traceback': traceback.format_exc()
        })


@app.route('/api/executions/history', methods=['GET'])
def get_execution_history():
    """查询代码执行历史记录"""
    try:
        user_id = request.args.get('user_id', 1, type=int)  # 从查询参数获取用户ID
        record_type = request.args.get('type', 0, type=int)  # 可选的记录类型过滤

        # 构建查询
        query = CodeExecution.query.filter_by(user_id=user_id)
        if record_type is not None:
            query = query.filter_by(record_type=record_type)

        # 获取最近的10条记录,按时间倒序
        executions = query.order_by(
            desc(CodeExecution.executed_at)
        ).limit(10).all()

        return jsonify({
            'success': True,
            'count': len(executions),
            'records': [execution.to_dict() for execution in executions]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'查询失败: {str(e)}'
        })


@app.route('/api/executions/<int:record_id>', methods=['GET'])
def get_execution_detail(record_id):
    """获取特定执行记录的详情"""
    try:
        execution = CodeExecution.query.get(record_id)
        if not execution:
            return jsonify({
                'success': False,
                'error': '记录不存在'
            }), 404

        return jsonify({
            'success': True,
            'record': execution.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'查询失败: {str(e)}'
        })


@app.route('/api/executions/clear', methods=['POST'])
def clear_execution_history():
    """清空执行历史记录"""
    try:
        user_id = request.args.get('user_id', 1, type=int)
        CodeExecution.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '历史记录已清空'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'清空失败: {str(e)}'
        })

# ======================== 模块特定API ========================

@app.route('/api/regex/test', methods=['POST'])
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

@app.route('/api/examples/<module_id>')
def get_module_examples(module_id):
    """获取模块示例代码API"""
    if module_id in ALL_MODULES:
        module_data = ALL_MODULES[module_id]
        return jsonify({
            'success': True,
            'examples': module_data.get('examples', [])
        })
    else:
        return jsonify({
            'success': False,
            'error': '模块不存在'
        })

@app.route('/api/module/<module_id>/examples')
def get_examples(module_id):
    """获取特定模块的示例"""
    if module_id not in ALL_MODULES:
        return jsonify({'error': '模块不存在'})
    
    module_data = ALL_MODULES[module_id]
    
    # 根据不同模块类型返回示例
    if module_id == 'variables':
        examples = {}
        for topic_id, topic_data in module_data['topics'].items():
            examples[topic_id] = topic_data['examples']
        return jsonify(examples)
    
    elif module_id == 'strings':
        return jsonify(module_data.get('examples', []))
    
    elif module_id == 'tuples':
        return jsonify(module_data.get('examples', {}))
    
    elif module_id == 'lists':
        examples = {}
        for topic_id, topic_data in module_data['topics'].items():
            examples[topic_id] = topic_data['examples']
        return jsonify(examples)
    
    elif module_id == 'flow_control':
        examples = {}
        for topic_id, topic_data in module_data.items():
            if isinstance(topic_data, dict) and 'examples' in topic_data:
                examples[topic_id] = topic_data['examples']
        return jsonify(examples)
    
    elif module_id == 'functions':
        return jsonify(module_data.get('examples', []))
    
    elif module_id == 'exceptions':
        return jsonify({
            'exception_examples': module_data.get('exception_examples', {}),
            'assertion_examples': module_data.get('assertion_examples', {})
        })
    
    elif module_id == 'files':
        return jsonify(module_data.get('examples', []))
    
    elif module_id == 'regex':
        return jsonify(module_data.get('examples', []))
    
    else:
        return jsonify({'error': '未知模块类型'})

# ======================== 工具页面 ========================

@app.route('/tools')
def tools():
    """工具页面"""
    return render_template('tools.html')

@app.route('/tools/regex')
def regex_tool():
    """正则表达式工具"""
    return render_template('regex_tool.html')

@app.route('/tools/code_playground')
def code_playground():
    """代码练习场"""
    return render_template('code_playground.html')

# ======================== 搜索功能 ========================

@app.route('/search')
def search():
    """搜索页面"""
    query = request.args.get('q', '')
    results = []
    
    if query:
        query_lower = query.lower()
        
        # 搜索模块
        for module_info in MODULE_NAVIGATION:
            if (query_lower in module_info['title'].lower() or 
                query_lower in module_info['description'].lower()):
                results.append({
                    'type': 'module',
                    'title': module_info['title'],
                    'description': module_info['description'],
                    'url': url_for('module_detail', module_id=module_info['id']),
                    'icon': module_info['icon']
                })
        
        # 搜索示例代码
        for module_id, module_data in ALL_MODULES.items():
            module_info = next((m for m in MODULE_NAVIGATION if m['id'] == module_id), None)
            
            # 搜索examples列表
            if 'examples' in module_data:
                examples = module_data['examples']
                if isinstance(examples, list):
                    for example in examples:
                        if (query_lower in example.get('title', '').lower() or
                            query_lower in example.get('description', '').lower() or
                            query_lower in example.get('code', '').lower()):
                            results.append({
                                'type': 'example',
                                'title': f"{example.get('title', '示例')} - {module_info['title'] if module_info else module_id}",
                                'description': example.get('description', ''),
                                'url': url_for('module_detail', module_id=module_id),
                                'icon': '💡'
                            })
                elif isinstance(examples, dict):
                    for example_key, example_data in examples.items():
                        if (query_lower in example_data.get('title', '').lower() or
                            query_lower in example_data.get('code', '').lower()):
                            results.append({
                                'type': 'example',
                                'title': f"{example_data.get('title', example_key)} - {module_info['title'] if module_info else module_id}",
                                'description': example_data.get('description', ''),
                                'url': url_for('module_detail', module_id=module_id),
                                'icon': '💡'
                            })
    
    return render_template('search_results.html', query=query, results=results)

# ======================== 错误处理 ========================

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return render_template('error.html', 
                         error_code=404,
                         error_message="页面不存在"), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return render_template('error.html',
                         error_code=500,
                         error_message="服务器内部错误"), 500

# ======================== 上下文处理器 ========================

@app.context_processor
def inject_navigation():
    """注入导航数据到所有模板"""
    return dict(
        navigation_modules=MODULE_NAVIGATION,
        current_year=datetime.now().year
    )

# ======================== 启动应用 ========================

# 启动信息（只执行一次）
print("🐍 Python学习平台启动中...")
print("📚 访问 http://localhost:5555 开始学习")
print("🔒 安全代码执行环境已启用")
print("📖 包含以下学习模块:")
for module in MODULE_NAVIGATION:
    print(f"   {module['icon']} {module['title']} - {module['difficulty']}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5555)