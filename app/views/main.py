"""
Main views for Python Learning Platform
主页和导航相关的视图
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from datetime import datetime
from app.utils.content_manager import MODULE_NAVIGATION, ALL_MODULES
from app.utils.safe_executor import executor

# 创建主蓝图
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """主页"""
    return render_template('index.html', modules=MODULE_NAVIGATION)


@main_bp.route('/about')
def about():
    """关于页面"""
    return render_template('about.html')


@main_bp.route('/module/<module_id>')
def module_detail(module_id):
    """模块详情页面"""
    if module_id in ALL_MODULES:
        module_data = ALL_MODULES[module_id]
        module_info = next((m for m in MODULE_NAVIGATION if m['id'] == module_id), None)
        return render_template('modules/module_detail.html', 
                             module=module_data, 
                             module_info=module_info,
                             module_id=module_id)
    else:
        return "模块不存在", 404


@main_bp.route('/module/<module_id>/topic/<topic_id>')
def topic_detail(module_id, topic_id):
    """主题详情页面"""
    if module_id in ALL_MODULES:
        module_data = ALL_MODULES[module_id]
        if 'topics' in module_data and topic_id in module_data['topics']:
            topic_data = module_data['topics'][topic_id]
            module_info = next((m for m in MODULE_NAVIGATION if m['id'] == module_id), None)
            return render_template('modules/topic_detail.html',
                                 topic=topic_data,
                                 topic_id=topic_id,
                                 module=module_data,
                                 module_info=module_info,
                                 module_id=module_id)
    return "主题不存在", 404


@main_bp.route('/api/execute', methods=['POST'])
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
        
        # 添加执行时间戳
        result['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}',
            'traceback': str(e)
        })


@main_bp.route('/api/examples/<module_id>')
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


@main_bp.route('/api/module/<module_id>/examples')
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


@main_bp.route('/search')
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
                    'url': url_for('main.module_detail', module_id=module_info['id']),
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
                                'url': url_for('main.module_detail', module_id=module_id),
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
                                'url': url_for('main.module_detail', module_id=module_id),
                                'icon': '💡'
                            })
    
    return render_template('search_results.html', query=query, results=results)


def register_error_handlers(app):
    """注册错误处理器"""
    
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


@main_bp.context_processor
def inject_navigation():
    """注入导航数据到所有模板"""
    return dict(
        navigation_modules=MODULE_NAVIGATION,
        current_year=datetime.now().year
    )
