"""
Flow Control views
流程控制模块的视图
"""

from flask import Blueprint, render_template, request, jsonify
from app.utils.content_manager import FLOW_CONTROL_CONTENT
from app.utils.safe_executor import executor

# 创建流程控制蓝图
flow_control_bp = Blueprint('flow_control', __name__)


@flow_control_bp.route('/')
def index():
    """流程控制主页"""
    return render_template('modules/flow_control.html', 
                         content=FLOW_CONTROL_CONTENT)


@flow_control_bp.route('/topic/<topic_id>')
def topic_detail(topic_id):
    """知识点详情页"""
    if topic_id in FLOW_CONTROL_CONTENT:
        topic = FLOW_CONTROL_CONTENT[topic_id]
        return render_template('modules/flow_control_topic.html', 
                             topic=topic, 
                             topic_id=topic_id,
                             all_topics=FLOW_CONTROL_CONTENT)
    else:
        return "知识点不存在", 404


@flow_control_bp.route('/api/get_example_code/<topic_id>/<int:example_index>')
def get_example_code(topic_id, example_index):
    """获取示例代码API"""
    try:
        if topic_id in FLOW_CONTROL_CONTENT:
            examples = FLOW_CONTROL_CONTENT[topic_id]['examples']
            if 0 <= example_index < len(examples):
                return jsonify({
                    'success': True,
                    'code': examples[example_index]['code']
                })
        
        return jsonify({
            'success': False,
            'error': '示例代码不存在'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@flow_control_bp.route('/api/execute', methods=['POST'])
def execute_code():
    """执行Python代码API"""
    try:
        data = request.get_json()
        code = data.get('code', '')
        inputs = data.get('inputs', None)  # 获取输入参数
        
        if not code.strip():
            return jsonify({
                'success': False,
                'error': '代码不能为空'
            })
        
        # 执行代码
        result = executor.execute_code(code, inputs=inputs)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        })


@flow_control_bp.route('/api/topics')
def get_topics():
    """获取所有知识点API"""
    topics = {}
    for topic_id, content in FLOW_CONTROL_CONTENT.items():
        topics[topic_id] = {
            'title': content['title'],
            'description': content['description']
        }
    return jsonify(topics)
