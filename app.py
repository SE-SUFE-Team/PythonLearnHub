"""
Python学习平台 - 主应用
整合所有Python学习模块的Web应用
"""
import os
import random

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, send_from_directory
from werkzeug.utils import secure_filename
from functools import wraps
from utils.safe_executor import executor
from utils.module_content import ALL_MODULES, MODULE_NAVIGATION
import re
import json
import traceback
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from models import db
from models.user import User
from models.user_profile import UserProfile
from models.code_execution import CodeExecution
from sqlalchemy import desc, func, distinct
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

# 头像上传配置
app.config['UPLOAD_FOLDER'] = 'static/avatars'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB 最大文件大小
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# ======================== 数据库 ========================

db.init_app(app)

# 创建所有表
with app.app_context():
    db.create_all()
# ======================== Jinja2 过滤器 ========================

@app.template_filter('format_account_id')
def format_account_id(user_id):
    return str(user_id).zfill(8)

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

    # 生成随机的8位数字账号（10000000-99999999）
    max_attempts = 100
    user_id = None
    for _ in range(max_attempts):
        user_id = str(random.randint(10000000, 99999999))
        if not User.query.filter_by(id=user_id).first():
            break
    else:
        return jsonify({'error': '账号生成失败，请稍后重试'}), 500

    hashed_pw = generate_password_hash(password)
    new_user = User(username=username, email=email, password_hash=hashed_pw,id=user_id)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': '注册成功', 'user_id':user_id}), 201

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

# ======================== 个人主页 ========================

@app.route('/profile')
@login_required
def profile():
    """个人主页"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login_page'))
    
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('login_page'))
    
    # 查询学习统计数据
    stats = {}
    
    # 1. 总学习时长（从 Progress 表汇总 study_time，单位：分钟）
    total_study_minutes = db.session.query(db.func.sum(Progress.study_time)).filter_by(user_id=user_id).scalar() or 0.0
    # 小于500分钟显示分钟，超过500分钟显示为小时
    if total_study_minutes < 500:
        stats['total_study_time'] = f"{round(total_study_minutes, 1)} 分钟"
    else:
        total_study_hours = total_study_minutes / 60
        stats['total_study_time'] = f"{round(total_study_hours, 1)} 小时"
    
    # 2. 完成模块数（progress_value >= 0.99 视为完成）
    completed_modules = Progress.query.filter_by(user_id=user_id).filter(Progress.progress_value >= 0.99).count()
    stats['completed_modules'] = completed_modules
    total_modules = len(MODULE_NAVIGATION)  # 总模块数
    
    # 3. 笔记数
    notes_count = Note.query.filter_by(user_id=user_id).count()
    stats['notes_count'] = notes_count
    
    # 4. 已解决题目数（status='AC' 的题目，去重 problem_id）
    # 使用 distinct() 确保同一题目多次AC提交只计算一次
    solved_problems = db.session.query(Submission.problem_id).filter_by(
        user_id=user_id, 
        status='AC'
    ).distinct().count()
    stats['solved_problems'] = solved_problems
    
    # 5. 最近活跃时间（从 Progress、Note、Submission 中取最新的）
    latest_progress = db.session.query(func.max(Progress.last_updated)).filter_by(user_id=user_id).scalar()
    latest_note = db.session.query(func.max(Note.updated_at)).filter_by(user_id=user_id).scalar()
    latest_submission = db.session.query(func.max(Submission.submitted_at)).filter_by(user_id=user_id).scalar()
    
    latest_dates = [d for d in [latest_progress, latest_note, latest_submission] if d is not None]
    if latest_dates:
        latest_active = max(latest_dates)
        # 格式化最近活跃时间
        now = datetime.now()
        diff = now - latest_active
        if diff.days == 0:
            stats['last_active'] = '今天'
        elif diff.days == 1:
            stats['last_active'] = '昨天'
        elif diff.days < 7:
            stats['last_active'] = f'{diff.days} 天前'
        else:
            stats['last_active'] = latest_active.strftime('%Y-%m-%d')
    else:
        stats['last_active'] = '暂无'
    
    # 6. 连续学习天数（基于 Progress.last_updated、Note.updated_at 和 Submission.submitted_at）
    # 获取所有有活动的日期（在 Python 中处理日期，避免 SQLite 日期函数兼容性问题）
    all_dates = set()
    
    # 从 Progress 获取日期
    progresses = Progress.query.filter_by(user_id=user_id).all()
    for p in progresses:
        if p.last_updated:
            all_dates.add(p.last_updated.date())
    
    # 从 Note 获取日期
    notes = Note.query.filter_by(user_id=user_id).all()
    for n in notes:
        if n.updated_at:
            all_dates.add(n.updated_at.date())
    
    # 从 Submission 获取日期
    submissions = Submission.query.filter_by(user_id=user_id).all()
    for s in submissions:
        if s.submitted_at:
            all_dates.add(s.submitted_at.date())
    
    if all_dates:
        # 按日期排序
        sorted_dates = sorted(all_dates, reverse=True)
        today = datetime.now().date()
        
        # 计算连续天数
        consecutive_days = 0
        expected_date = today
        
        for date in sorted_dates:
            if date == expected_date:
                consecutive_days += 1
                # 计算前一天
                expected_date = expected_date - timedelta(days=1)
            elif date < expected_date:
                # 如果日期不连续，停止计算
                break
        
        stats['consecutive_days'] = consecutive_days
    else:
        stats['consecutive_days'] = 0
    
    # 获取用户头像URL（如果存在）
    avatar_url = None
    user_profile = UserProfile.query.filter_by(user_id=user_id).first()
    if user_profile and user_profile.avatar:
        avatar_url = url_for('get_avatar', filename=user_profile.avatar)
    
    # 生成活跃度图表数据（基于多个数据源）
    # 按日期汇总：学习时长、笔记数、完成模块数、解决题目数
    activity_data = {}
    
    # 1. 从 Progress 表收集学习时长
    all_progresses = Progress.query.filter_by(user_id=user_id).all()
    for progress in all_progresses:
        if progress.last_updated:
            date_key = progress.last_updated.date()
            if date_key not in activity_data:
                activity_data[date_key] = {
                    'study_time': 0.0,
                    'notes_count': 0,
                    'completed_modules': 0,
                    'solved_problems': 0
                }
            activity_data[date_key]['study_time'] += (progress.study_time or 0.0)
            # 如果模块完成（progress_value >= 0.99），计入完成模块数
            if progress.progress_value and progress.progress_value >= 0.99:
                activity_data[date_key]['completed_modules'] += 1
    
    # 2. 从 Note 表收集笔记数（按创建或更新日期）
    all_notes = Note.query.filter_by(user_id=user_id).all()
    for note in all_notes:
        # 使用 updated_at，如果没有则使用 created_at
        note_date = (note.updated_at or note.created_at)
        if note_date:
            date_key = note_date.date()
            if date_key not in activity_data:
                activity_data[date_key] = {
                    'study_time': 0.0,
                    'notes_count': 0,
                    'completed_modules': 0,
                    'solved_problems': 0
                }
            activity_data[date_key]['notes_count'] += 1
    
    # 3. 从 Submission 表收集解决题目数（AC 状态，按提交日期，去重 problem_id）
    # 使用字典记录每天已解决的题目，避免重复计算
    solved_problems_by_date = {}
    all_submissions = Submission.query.filter_by(user_id=user_id, status='AC').all()
    for submission in all_submissions:
        if submission.submitted_at:
            date_key = submission.submitted_at.date()
            if date_key not in solved_problems_by_date:
                solved_problems_by_date[date_key] = set()
            # 使用 set 去重，同一天同一题目只计一次
            solved_problems_by_date[date_key].add(submission.problem_id)
    
    # 将去重后的解决题目数添加到 activity_data
    for date_key, problem_ids in solved_problems_by_date.items():
        if date_key not in activity_data:
            activity_data[date_key] = {
                'study_time': 0.0,
                'notes_count': 0,
                'completed_modules': 0,
                'solved_problems': 0
            }
        activity_data[date_key]['solved_problems'] = len(problem_ids)
    
    # 生成过去一年的完整日期数据（365天）
    today = datetime.now().date()
    one_year_ago = today - timedelta(days=365)
    
    # 计算活跃度级别（仅基于有活动数据的日期）
    if activity_data:
        # 找到最早的活动日期
        dates = sorted(activity_data.keys())
        earliest_date = dates[0]
        
        # 只计算最早日期之后的数据用于计算最大值
        valid_data = {k: v for k, v in activity_data.items() if k >= earliest_date}
        if valid_data:
            max_study_time = max(data['study_time'] for data in valid_data.values())
            max_notes = max(data['notes_count'] for data in valid_data.values())
            max_modules = max(data['completed_modules'] for data in valid_data.values())
            max_problems = max(data['solved_problems'] for data in valid_data.values())
        else:
            max_study_time = 0
            max_notes = 0
            max_modules = 0
            max_problems = 0
    else:
        earliest_date = None
        max_study_time = 0
        max_notes = 0
        max_modules = 0
        max_problems = 0
    
    # 生成完整的过去365天数据
    activity_list = []
    for i in range(365):
        date = today - timedelta(days=364 - i)
        date_str = date.isoformat()
        
        # 如果日期在最早活动日期之前，或者没有活动数据，设置为无活动
        if not activity_data or date < earliest_date or date not in activity_data:
            activity_list.append({
                'date': date_str,
                'level': 0,
                'count': 0,  # 保持兼容性
                'study_time': 0.0,
                'notes_count': 0,
                'completed_modules': 0,
                'solved_problems': 0
            })
        else:
            # 计算活跃度级别
            data = activity_data[date]
            study_time = data['study_time']
            notes_count = data['notes_count']
            completed_modules = data['completed_modules']
            solved_problems = data['solved_problems']
            
            # 计算各维度分数（归一化到 0-1）
            # 学习时长：权重 0.35   
            if max_study_time > 0:
                time_score = (study_time / max_study_time) * 0.35               
            else:
                time_score = 0
            
            # 笔记数：权重 0.1
            if max_notes > 0:
                notes_score = (notes_count / max_notes) * 0.1
            else:
                notes_score = 0
            
            # 完成模块数：权重 0.2
            if max_modules > 0:
                modules_score = (completed_modules / max_modules) * 0.2
            else:
                modules_score = 0
            
            # 解决题目数：权重 0.35
            if max_problems > 0:
                problems_score = (solved_problems / max_problems) * 0.35
            else:
                problems_score = 0
            
            # 计算总分（0-1）
            total_score = time_score + notes_score + modules_score + problems_score
            
            # 转换为 0-4 级别（score 越高，level 越高，颜色越深）
            if total_score >= 0.8:
                level = 4
            elif total_score >= 0.6:
                level = 3
            elif total_score >= 0.4:
                level = 2
            elif total_score >= 0.1:
                level = 1
            else:
                level = 0
            
            # 计算总活动数（用于兼容前端显示）
            total_count = notes_count + completed_modules + solved_problems
            
            activity_list.append({
                'date': date_str,
                'level': level,
                'count': total_count,  # 保持兼容性
                'study_time': round(study_time, 2),
                'notes_count': notes_count,
                'completed_modules': completed_modules,
                'solved_problems': solved_problems
            })
    
    return render_template('profile.html', 
                         stats=stats,
                         total_modules=total_modules,
                         avatar_url=avatar_url,
                         activity_data=activity_list)

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


# ======================== 头像上传功能 ========================

@app.route('/api/upload-avatar', methods=['POST'])
@login_required
def api_upload_avatar():
    """上传用户头像"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': '未登录'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'error': '用户不存在'}), 400
    
    # 检查文件
    if 'avatar' not in request.files:
        return jsonify({'success': False, 'error': '没有上传文件'}), 400
    
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'success': False, 'error': '文件名为空'}), 400
    
    # 检查文件类型
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
        return jsonify({'success': False, 'error': '不支持的文件类型'}), 400
    
    # 创建目录
    upload_dir = app.config['UPLOAD_FOLDER']
    os.makedirs(upload_dir, exist_ok=True)
    
    # 生成文件名：用户ID_时间戳.扩展名
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{user_id}_{int(datetime.now().timestamp())}.{ext}"
    filepath = os.path.join(upload_dir, filename)
    
    # 获取或创建用户配置
    user_profile = UserProfile.query.filter_by(user_id=user_id).first()
    if not user_profile:
        user_profile = UserProfile(user_id=user_id)
        db.session.add(user_profile)
    
    # 删除旧头像（如果存在）
    if user_profile.avatar:
        old_filepath = os.path.join(upload_dir, user_profile.avatar)
        if os.path.exists(old_filepath):
            try:
                os.remove(old_filepath)
            except:
                pass
    
    # 保存新头像
    file.save(filepath)
    
    # 更新数据库
    user_profile.avatar = filename
    user_profile.updated_at = datetime.now()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'avatar_url': url_for('get_avatar', filename=filename)
    })

@app.route('/avatars/<filename>')
def get_avatar(filename):
    """提供头像文件"""
    upload_dir = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(upload_dir, secure_filename(filename))




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
    nav_avatar_url = None

    try:
        if 'user_id' in session:
            user_id = session.get('user_id')
            username = session.get('username', 'Guest')
            current_user = User.query.get(user_id)
            if current_user:
                username = current_user.username
                # 获取用户头像URL（用于导航栏显示）
                user_profile = UserProfile.query.filter_by(user_id=user_id).first()
                if user_profile and user_profile.avatar:
                    nav_avatar_url = url_for('get_avatar', filename=user_profile.avatar)
    except Exception:
        pass

    return dict(
        navigation_modules=MODULE_NAVIGATION,
        current_year=datetime.now().year,
        username=username,
        current_user=current_user,
        user_id=user_id,
        is_logged_in=('user_id' in session),
        nav_avatar_url=nav_avatar_url
    )

# ======================== 启动应用 ========================

# 启动信息（只执行一次）
print("🐍 Python学习平台启动中...")
print("📚 访问 http://localhost:5000 开始学习")
print("🔒 安全代码执行环境已启用")
print("📖 包含以下学习模块:")
for module in MODULE_NAVIGATION:
    print(f"   {module['icon']} {module['title']} - {module['difficulty']}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)