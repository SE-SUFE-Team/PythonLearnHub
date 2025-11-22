"""
Python学习平台 - 主应用
整合所有Python学习模块的Web应用
"""
import os

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from functools import wraps
from utils.safe_executor import executor
from utils.module_content import ALL_MODULES, MODULE_NAVIGATION
import re
import json
import traceback
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models import db
from models.user import User
from models.code_execution import CodeExecution
from sqlalchemy import desc
from models.progress import Progress
from models.notes import Note
from sqlalchemy.exc import IntegrityError
from utils.judge import judge_engine
from models.problem import Problem, Submission
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'python_learning_platform_2024')

# SQLite 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ======================== 数据库 ========================

db.init_app(app)

# ======================== Jinja2 过滤器 ========================

@app.template_filter('format_account_id')
def format_account_id(user_id):
    """将用户ID格式化为8位数字字符串（例如：2 -> 00000002）"""
    return str(user_id).zfill(8)

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

# ======================== 登陆注册 ========================

# 注册页面
@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

# 注册接口
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    if not username or not password or not email:
        return jsonify({'error': '用户名、密码和邮箱不能为空'}), 400

    # 只检查邮箱唯一性，用户名允许重复
    if User.query.filter_by(email=email).first():
        return jsonify({'error': '邮箱已存在'}), 400

    hashed_pw = generate_password_hash(password)
    new_user = User(username=username, email=email, password_hash=hashed_pw)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': '注册成功', 'user_id': new_user.id}), 201

# 登录页面
@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

# 登录接口
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    id = data.get('id')
    password = data.get('password')

    user = User.query.filter_by(id=id).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': '账号或密码错误'}), 401

    session['user_id'] = user.id
    session['username'] = user.username

    return jsonify({'message': '登录成功', 'user_id': user.id, 'username': user.username})

@app.route('/logout', methods=['POST'])
def logout():
    """登出用户"""
    session.clear()
    return jsonify({'message': '已成功登出'}), 200

@app.route('/me', methods=['GET'])
def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': '未登录'}), 401

    user = User.query.get(user_id)
    return jsonify({'user_id': user.id, 'username': user.username})

# ======================== 登录验证装饰器 ========================

def login_required(f):
    """登录检查装饰器：未登录用户会被重定向到登录页面"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # 如果是API请求（POST/PUT/DELETE），返回JSON错误
            if request.method in ['POST', 'PUT', 'DELETE'] or request.path.startswith('/api/'):
                return jsonify({'error': '请先登录'}), 401
            # 如果是页面请求（GET），显示提示并重定向到登录页
            flash('请先登录', 'warning')
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

# ======================== 主页和导航 ========================

@app.route('/')
@login_required
def index():
    """主页"""
    # 查询当前用户的进度数据并传入模板（使用session中的用户ID）
    progress_map = {}
    try:
        user_id = session.get('user_id')
        if user_id:
            progresses = Progress.query.filter_by(user_id=user_id).all()
        else:
            progresses = []
        for p in progresses:
            # 存储为 0~1 的浮点数
            progress_map[p.module_id] = float(p.progress_value) if p.progress_value is not None else 0.0
    except Exception:
        # 如果查询失败（例如数据库尚未创建），保持空字典
        progress_map = {}

    return render_template('index.html', modules=MODULE_NAVIGATION, progress_map=progress_map)

@app.route('/about')
@login_required
def about():
    """关于页面"""
    return render_template('about.html')

# ======================== 模块页面路由 ========================

@app.route('/module/<module_id>')
@login_required
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
@login_required
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
        user_id = session.get('user_id')

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
# ======================== 代码执行历史记录API ========================

@app.route('/api/executions/history', methods=['GET'])
def get_execution_history():
    """查询代码执行历史记录"""
    try:
        user_id = session.get('user_id')
        record_type = request.args.get('type', 0, type=int)

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
        user_id = session.get('user_id')
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


# ======================== Online Judge 功能 ========================

@app.route('/oj')
@login_required
def oj_home():
    """OJ 主页"""
    return render_template('oj_home.html')


@app.route('/api/oj/problems', methods=['GET'])
def api_get_problems():
    """获取所有题目列表"""
    try:
        problems = []
        data_dir = './Data'

        for filename in os.listdir(data_dir):
            if filename.startswith('problem_') and filename.endswith('.json'):
                problem_id = filename.replace('problem_', '').replace('.json', '')
                problem_data = judge_engine.load_problem(problem_id)
                if problem_data:
                    problems.append({
                        'id': problem_data.get('id', problem_id),
                        'title': problem_data.get('title', ''),
                        'description': problem_data.get('description', '')[:100] + '...'
                    })

        return jsonify({
            'success': True,
            'problems': sorted(problems, key=lambda x: int(x['id']))
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/oj/problem/<problem_id>', methods=['GET'])
def api_get_problem_detail(problem_id):
    """获取题目详情"""
    try:
        problem = judge_engine.load_problem(problem_id)
        if not problem:
            return jsonify({
                'success': False,
                'error': '题目不存在'
            }), 404

        return jsonify({
            'success': True,
            'problem': problem
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/oj/submit', methods=['POST'])
@login_required
def api_submit_code():
    """提交代码进行判题"""
    try:
        data = request.get_json()
        problem_id = data.get('problem_id')
        code = data.get('code', '').strip()

        if not problem_id or not code:
            return jsonify({
                'success': False,
                'error': '题目ID和代码不能为空'
            }), 400

        judge_result = judge_engine.judge(problem_id, code)

        if not judge_result.get('success'):
            return jsonify(judge_result), 400

        # 保存提交记录
        user_id = session.get('user_id')
        submission = Submission(
            user_id=user_id,
            problem_id=problem_id,
            code=code,
            status=judge_result['status'],
            passed_cases=judge_result['passed'],
            total_cases=judge_result['total'],
            error_message=json.dumps(judge_result.get('failed_case')),
            execution_time=judge_result['execution_time']
        )
        db.session.add(submission)
        db.session.commit()

        return jsonify({
            'success': True,
            'submission_id': submission.id,
            'result': judge_result
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/oj/submissions', methods=['GET'])
@login_required
def api_get_submissions():
    """获取用户提交记录"""
    try:
        user_id = session.get('user_id')
        problem_id = request.args.get('problem_id', type=int)

        query = Submission.query.filter_by(user_id=user_id)
        if problem_id:
            query = query.filter_by(problem_id=problem_id)

        submissions = query.order_by(Submission.submitted_at.desc()).limit(20).all()

        return jsonify({
            'success': True,
            'submissions': [s.to_dict() for s in submissions]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/oj/submissions/clear', methods=['POST'])
@login_required
def api_clear_submissions():
    """清空指定题目的提交历史记录"""
    try:
        data = request.get_json()
        problem_id = data.get('problem_id')

        if not problem_id:
            return jsonify({
                'success': False,
                'error': '缺少题目ID'
            }), 400

        user_id = session.get('user_id')

        # 删除该用户指定题目的所有提交记录
        deleted_count = Submission.query.filter_by(
            user_id=user_id,
            problem_id=problem_id
        ).delete()

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'已清空 {deleted_count} 条提交记录',
            'deleted_count': deleted_count
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'清空失败: {str(e)}'
        }), 500


@app.route('/oj/problem/<problem_id>')
@login_required
def oj_problem_detail(problem_id):
    """题目详情页面"""
    problem = judge_engine.load_problem(problem_id)
    if not problem:
        return "题目不存在", 404
    return render_template('oj_problem.html', problem=problem)
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

# ======================== 进度条功能 ========================
@app.route('/api/progress', methods=['POST'])
def api_progress():
    """接收前端上报的进度数据并插入或更新 Progress 表。
    请求 JSON 示例:
    {
      'module_id': 'variables',
      'browse_coverage': 0.75,   # 0~1
      'study_time': 1.5,         # 分钟
      'quiz_completion': 0.2     # 可选，0~1
    }
    """
    try:
        data = request.get_json() or {}
        module_id = data.get('module_id')
        if not module_id:
            return jsonify({'success': False, 'error': '缺少 module_id'}), 400

        if module_id not in ALL_MODULES:
            return jsonify({'success': False, 'error': '模块不存在'}), 400

        try:
            browse = float(data.get('browse_coverage', 0) or 0)
        except (TypeError, ValueError):
            browse = 0.0

        try:
            study_time = float(data.get('study_time', 0) or 0)
        except (TypeError, ValueError):
            study_time = 0.0

        quiz = data.get('quiz_completion', None)
        if quiz is not None:
            try:
                quiz = float(quiz)
            except (TypeError, ValueError):
                quiz = None

        # 使用session中的用户ID
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': '用户未登录'}), 401

        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'error': '用户不存在'}), 400

        # 查找已有记录
        p = Progress.query.filter_by(user_id=user.id, module_id=module_id).first()
        if p:
            # 合并策略：browse 取最大（更高覆盖率），study_time 累加，quiz 取最大
            p.browse_coverage = max(p.browse_coverage or 0.0, min(max(browse, 0.0), 1.0))
            p.study_time = (p.study_time or 0.0) + max(study_time, 0.0)
            if quiz is not None:
                p.quiz_completion = max(p.quiz_completion or 0.0, min(max(quiz, 0.0), 1.0))

            # 重新计算 progress_value（权重与之前一致，可后续抽出为配置）
            study_norm = min((p.study_time or 0.0) / 10.0, 1.0)
            p.progress_value = round((p.browse_coverage * 0.6) + ((p.quiz_completion or 0.0) * 0.0) + (study_norm * 0.4), 4)
            p.last_updated = datetime.now()
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                return jsonify({'success': False, 'error': '数据库冲突，稍后重试'}), 500

            return jsonify({'success': True, 'action': 'updated', 'progress_value': p.progress_value})
        else:
            # 新建记录
            init_quiz = float(quiz) if quiz is not None else 0.0
            study_norm = min(max(study_time, 0.0) / 120.0, 1.0)
            progress_value = round((min(max(browse, 0.0), 1.0) * 0.6) + (init_quiz * 0.0) + (study_norm * 0.4), 4)
            new = Progress(
                user_id=user.id,
                module_id=module_id,
                browse_coverage=min(max(browse, 0.0), 1.0),
                study_time=max(study_time, 0.0),
                quiz_completion=init_quiz,
                progress_value=progress_value,
                last_updated=datetime.now()
            )
            db.session.add(new)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                existing = Progress.query.filter_by(user_id=user.id, module_id=module_id).first()
                if existing:
                    return jsonify({'success': True, 'action': 'exists', 'progress_value': existing.progress_value})
                return jsonify({'success': False, 'error': '插入失败'}), 500

            return jsonify({'success': True, 'action': 'created', 'progress_value': progress_value})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ======================== 学习笔记功能 ========================
@app.route('/api/notes', methods=['GET'])
def api_get_notes():
    """获取当前用户的笔记列表，支持 q 查询（标题或内容模糊匹配）"""
    try:
        q = request.args.get('q', '').strip()
        # 使用session中的用户ID
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': '用户未登录'}), 401

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 400

        query = Note.query.filter_by(user_id=user.id)
        if q:
            like = f"%{q}%"
            query = query.filter((Note.title.ilike(like)) | (Note.content.ilike(like)))

        notes = query.order_by(Note.updated_at.desc()).all()
        return jsonify([n.to_dict() for n in notes])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/notes', methods=['POST'])
def api_create_note():
    try:
        data = request.get_json() or {}
        content = data.get('content', '').strip()
        title = data.get('title', '').strip() or None

        if not content:
            return jsonify({'error': 'content 不能为空'}), 400

        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': '用户未登录'}), 401

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 400

        n = Note(user_id=user.id, title=title, content=content)
        db.session.add(n)
        db.session.commit()
        return jsonify({'success': True, 'note': n.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/notes/<int:note_id>', methods=['PUT'])
def api_update_note(note_id):
    try:
        data = request.get_json() or {}
        content = data.get('content', None)
        title = data.get('title', None)

        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': '用户未登录'}), 401

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 400

        note = Note.query.filter_by(note_id=note_id, user_id=user.id).first()
        if not note:
            return jsonify({'error': '笔记不存在或无权限'}), 404

        if content is not None:
            note.content = content
        if title is not None:
            note.title = title or None
        note.updated_at = datetime.now()
        db.session.commit()
        return jsonify({'success': True, 'note': note.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def api_delete_note(note_id):
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': '用户未登录'}), 401

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 400

        note = Note.query.filter_by(note_id=note_id, user_id=user.id).first()
        if not note:
            return jsonify({'error': '笔记不存在或无权限'}), 404

        db.session.delete(note)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500





# ======================== 工具页面 ========================

@app.route('/tools')
@login_required
def tools():
    """工具页面"""
    return render_template('tools.html')

@app.route('/tools/regex')
@login_required
def regex_tool():
    """正则表达式工具"""
    return render_template('regex_tool.html')

@app.route('/tools/code_playground')
@login_required
def code_playground():
    """代码练习场"""
    return render_template('code_playground.html')

# ======================== 搜索功能 ========================

@app.route('/search')
@login_required
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
    # 从session获取当前登录用户信息
    current_user = None
    user_id = None
    username = 'Guest'

    try:
        if 'user_id' in session:
            user_id = session.get('user_id')
            username = session.get('username', 'Guest')
            current_user = User.query.get(user_id)
            if current_user:
                username = current_user.username
    except Exception:
        pass

    return dict(
        navigation_modules=MODULE_NAVIGATION,
        current_year=datetime.now().year,
        username=username,
        current_user=current_user,
        user_id=user_id,
        is_logged_in=('user_id' in session)
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
    app.run(debug=True, host='0.0.0.0', port=5000)