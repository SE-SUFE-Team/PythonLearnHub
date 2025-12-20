"""
生成测试数据脚本
为 bob 账号生成学习数据，时间跨度从2025年1月到现在
"""
import sys
import os
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# 添加项目路径（动态获取项目根目录）
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app import app
from models import db
from models.user import User
from models.progress import Progress
from models.notes import Note
from models.problem import Problem, Submission
from utils.module_content import MODULE_NAVIGATION
from utils.judge import judge_engine
from sqlalchemy import distinct

def generate_test_data():
    """生成测试数据"""
    with app.app_context():
        # 查找bob用户
        bob = User.query.filter_by(username='Bob').first()
        if not bob:
            print("未找到 bob 账号，请先创建该账号")
            return
        print(f"找到 bob 账号，ID: {bob.id}")
        
        # 确保有题目数据（从JSON文件加载，匹配现有的JSON文件）
        problems = Problem.query.all()
        if not problems:
            # 从JSON文件加载题目数据
            data_dir = './Data'
            created_count = 0
            
            for i in range(1, 6):
                # 加载JSON文件
                problem_data = judge_engine.load_problem(str(i))
                if problem_data:
                    # 从JSON文件读取数据
                    problem_id = problem_data.get('id', i)
                    title = problem_data.get('title', f'题目 {i}')
                    description = problem_data.get('description', '')
                    
                    # 如果没有difficulty字段，根据题目复杂度推断（这里可以设置默认值）
                    # 或者可以根据题目ID或其他特征推断难度
                    difficulty = problem_data.get('difficulty', None)
                    
                    problem = Problem(
                        id=problem_id,
                        title=title,
                        difficulty=difficulty,
                        description=description
                    )
                    db.session.add(problem)
                    created_count += 1
                    print(f"  从JSON加载题目 {i}: {title}")
                else:
                    print(f"  警告：无法加载 problem_{i}.json")
            
            db.session.commit()
            problems = Problem.query.all()
            print(f"从JSON文件创建了 {created_count} 道题目（ID: {[p.id for p in problems]}）")
        
        # 只使用有效的题目（ID 1-5，匹配JSON文件）
        valid_problems = [p for p in problems if p.id <= 5]
        if not valid_problems:
            print("错误：没有找到有效的题目（ID 1-5）")
            return
        print(f"使用有效题目: {[p.id for p in valid_problems]}")
        
        # 获取模块ID列表
        module_ids = [m['id'] for m in MODULE_NAVIGATION]
        
        # 清空bob的现有数据
        print("\n清空bob的现有数据...")
        Progress.query.filter_by(user_id=bob.id).delete()
        Note.query.filter_by(user_id=bob.id).delete()
        Submission.query.filter_by(user_id=bob.id).delete()
        db.session.commit()
        print("已清空bob的现有数据")
        
        print("\n开始为bob生成测试数据...")
        
        # ========== bob 账号：均衡型活跃度 ==========
        # 时间范围：2025年8月1日到现在
        today = datetime.now()
        start_date = datetime(2025, 8, 1)
        
        # 计算总天数
        total_days = (today - start_date).days + 1
        print(f"时间范围：{start_date.strftime('%Y-%m-%d')} 到 {today.strftime('%Y-%m-%d')}，共 {total_days} 天")
        
        # bob: 从2025年8月1日到现在，每天都有活动，但强度不同
        # 使用连续性逻辑，让相邻日期的活跃度有一定关联
        last_activity_level = 2  # 初始活跃度
        activity_levels = []  # 记录所有活跃度级别，用于统计
        
        for day_offset in range(total_days):
            date = start_date + timedelta(days=day_offset)
            date_only = date.date()
            day_of_week = date.weekday()  # 0=周一, 6=周日
            
            # 根据前一天活跃度和星期几决定当天活跃度
            # 添加连续性：有60%概率保持相近的活跃度，40%概率随机变化
            if random.random() < 0.6:
                # 保持连续性：在前一天活跃度基础上小幅波动（±1）
                base_level = last_activity_level
                change = random.choice([-1, 0, 0, 1])  # 更倾向于保持或小幅增加
                activity_level = max(0, min(4, base_level + change))
            else:
                # 随机变化，但考虑星期几
                # 工作日（周一到周五）倾向于更高活跃度
                if day_of_week < 5:  # 工作日
                    weights = [1, 3, 8, 25, 30]  # 工作日：更倾向于高活跃度
                else:  # 周末
                    weights = [3, 8, 15, 20, 15]  # 周末：活跃度稍低
                activity_level = random.choices([0, 1, 2, 3, 4], weights=weights)[0]
            
            # 确保level 4有足够的天数，但不要太极端
            # 如果连续多天都是低活跃度，增加高活跃度的概率
            recent_low_days = sum(1 for l in activity_levels[-7:] if l <= 1)
            if recent_low_days >= 5 and random.random() < 0.3:
                activity_level = random.choice([3, 4])
            
            last_activity_level = activity_level
            activity_levels.append(activity_level)
            
            if activity_level > 0:
                # 学习时长：更合理的分布，避免极端值
                if activity_level == 1:
                    study_time = random.uniform(15, 40)
                elif activity_level == 2:
                    study_time = random.uniform(40, 80)
                elif activity_level == 3:
                    study_time = random.uniform(80, 150)
                else:  # level 4 - 深度学习，但不要过于极端
                    study_time = random.uniform(120, 220)  # 降低上限，更自然
                
                # 随机选择1-4个模块进行学习（高活跃度选择更多模块）
                max_modules = min(2 + activity_level, len(module_ids))
                modules_today = random.sample(module_ids, min(random.randint(1, max_modules), len(module_ids)))
                
                for module_id in modules_today:
                    # 检查是否已有该模块的进度
                    progress = Progress.query.filter_by(
                        user_id=bob.id,
                        module_id=module_id
                    ).first()
                    
                    if not progress:
                        # 创建新进度
                        progress_value = min(0.3 + random.uniform(0, 0.4), 1.0)
                        progress = Progress(
                            user_id=bob.id,
                            module_id=module_id,
                            browse_coverage=random.uniform(0.5, 1.0),
                            study_time=study_time / len(modules_today),
                            quiz_completion=random.uniform(0.3, 1.0),
                            progress_value=progress_value,
                            last_updated=date
                        )
                        db.session.add(progress)
                    else:
                        # 更新现有进度
                        progress.study_time = (progress.study_time or 0) + study_time / len(modules_today)
                        progress.progress_value = min((progress.progress_value or 0) + random.uniform(0.1, 0.3), 1.0)
                        progress.last_updated = date
                
                # 笔记：更自然的分布
                if activity_level == 1:
                    notes_count = random.randint(0, 1)
                elif activity_level == 2:
                    notes_count = random.randint(0, 2)
                elif activity_level == 3:
                    notes_count = random.randint(1, 3)
                else:  # level 4
                    notes_count = random.randint(2, 4)  # 深度学习时笔记更多
                for _ in range(notes_count):
                    note = Note(
                        user_id=bob.id,
                        title=f'学习笔记 - {date_only.strftime("%Y-%m-%d")}',
                        content=f'这是 {date_only} 的学习笔记内容。记录了当天的学习心得和重要知识点。',
                        created_at=date,
                        updated_at=date
                    )
                    db.session.add(note)
                
                # 完成模块：根据活跃度增加完成概率
                if activity_level >= 2:
                    completion_prob = {2: 0.2, 3: 0.4, 4: 0.6}[activity_level]
                    if random.random() < completion_prob:
                        module_to_complete = random.choice(module_ids)
                        progress = Progress.query.filter_by(
                            user_id=bob.id,
                            module_id=module_to_complete
                        ).first()
                        if progress:
                            progress.progress_value = 1.0
                            progress.last_updated = date
                
                # 解决题目：更自然的分布，避免极端值
                if activity_level == 1:
                    problems_solved = random.randint(1, 2)
                elif activity_level == 2:
                    problems_solved = random.randint(2, 4)
                elif activity_level == 3:
                    problems_solved = random.randint(4, 8)
                else:  # level 4 - 深度学习，但不要过于极端
                    problems_solved = random.randint(6, 12)  # 降低上限，更合理
                
                # 允许重复做同一道题，不进行去重
                for _ in range(problems_solved):
                    problem = random.choice(valid_problems)
                    submission = Submission(
                        user_id=bob.id,
                        problem_id=problem.id,
                        code=f'# Solution for problem {problem.id}',
                        status='AC',
                        passed_cases=10,
                        total_cases=10,
                        execution_time=random.uniform(10, 500),
                        submitted_at=date
                    )
                    db.session.add(submission)
        
        # 提交所有更改
        db.session.commit()
        print("\n✅ bob的测试数据生成完成！")
        print(f"\n数据统计：")
        print(f"  进度记录: {Progress.query.filter_by(user_id=bob.id).count()} 条")
        print(f"  笔记: {Note.query.filter_by(user_id=bob.id).count()} 条")
        print(f"  AC提交: {Submission.query.filter_by(user_id=bob.id, status='AC').count()} 次")
        
        # 统计已解决的唯一题目数
        solved_unique = db.session.query(Submission.problem_id).filter_by(
            user_id=bob.id, 
            status='AC'
        ).filter(Submission.problem_id <= 5).distinct().count()
        print(f"  已解决题目数: {solved_unique} 道（去重后）")
        
        # 统计活跃度级别分布
        if activity_levels:
            level_counts = {}
            for level in range(5):
                level_counts[level] = activity_levels.count(level)
            print(f"\n活跃度级别分布：")
            for level in range(5):
                count = level_counts[level]
                percentage = (count / len(activity_levels)) * 100
                level_name = ['无活动', '较少', '中等', '较多', '很多'][level]
                print(f"  Level {level} ({level_name}): {count} 天 ({percentage:.1f}%)")

if __name__ == '__main__':
    generate_test_data()

