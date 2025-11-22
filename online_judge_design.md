# Online Judge 系统设计文档

## 1. 概述

### 1.1 系统简介
本 Online Judge (OJ) 系统是 Python 学习平台的核心功能模块，为用户提供编程题目练习、代码提交、自动判题等功能。系统支持多测试用例验证，实时反馈代码执行结果。

### 1.2 主要功能
- 📋 题目管理：浏览、查看题目详情
- 💻 代码提交：在线编写和提交代码
- ⚖️ 自动判题：多测试用例验证
- 📊 提交历史：查看历史提交记录
- 🗑️ 记录管理：清空指定题目的提交历史

---

## 2. 系统架构

### 2.1 技术栈
- **后端框架**: Flask
- **数据库**: SQLite (SQLAlchemy ORM)
- **判题引擎**: 自定义 Judge Engine (utils.judge)
- **代码执行**: 安全沙箱环境 (utils.safe_executor)

### 2.2 模块划分
```
┌─────────────────────────────────────┐
│         前端用户界面                │
│   (oj_home.html, oj_problem.html)   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│         Flask 路由层                │
│    (API Endpoints + Page Routes)    │
└──────────────┬──────────────────────┘
               │
      ┌────────┴────────┐
      ▼                 ▼
┌──────────┐      ┌──────────┐
│ 判题引擎 │      │ 数据模型 │
│  Judge   │      │ Problem  │
│  Engine  │      │Submission│
└──────────┘      └──────────┘
      │                 │
      └────────┬────────┘
               ▼
        ┌──────────────┐
        │  数据存储层  │
        │ (SQLite DB)  │
        │ (JSON Files) │
        └──────────────┘
```

---

## 3. 数据库设计

### 3.1 Problem 表 (题目信息)
虽然题目数据主要存储在 JSON 文件中，但可扩展为数据库存储。

**字段设计**:
```python
class Problem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20))  # Easy/Medium/Hard
    test_cases = db.Column(db.Text)  # JSON格式存储
    created_at = db.Column(db.DateTime, default=datetime.now)
```

### 3.2 Submission 表 (提交记录)
存储用户的所有代码提交记录。

**字段设计**:
```python
class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    problem_id = db.Column(db.String(50), nullable=False)
    code = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20))  # Accepted/Wrong Answer/Runtime Error/...
    passed_cases = db.Column(db.Integer, default=0)
    total_cases = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text)  # JSON格式存储失败用例详情
    execution_time = db.Column(db.Float)  # 执行时间(秒)
    submitted_at = db.Column(db.DateTime, default=datetime.now)
```

**索引优化**:
```sql
CREATE INDEX idx_user_problem ON submission(user_id, problem_id);
CREATE INDEX idx_submitted_at ON submission(submitted_at DESC);
```

### 3.3 数据关系图
```
┌──────────┐         ┌──────────────┐
│   User   │ 1     * │  Submission  │
│          ├─────────┤              │
│ id (PK)  │         │ id (PK)      │
│ username │         │ user_id (FK) │
│ email    │         │ problem_id   │
└──────────┘         │ code         │
                     │ status       │
                     └──────────────┘
```

---

## 4. API 接口设计

### 4.1 获取题目列表

**接口**: `GET /api/oj/problems`

**功能**: 获取所有可用题目的列表

**请求参数**: 无

**响应示例**:
```json
{
  "success": true,
  "problems": [
    {
      "id": "1",
      "title": "两数之和",
      "description": "给定一个整数数组和目标值，找出数组中和为目标值的两个数..."
    },
    {
      "id": "2",
      "title": "回文判断",
      "description": "判断一个字符串是否为回文..."
    }
  ]
}
```

**错误响应**:
```json
{
  "success": false,
  "error": "读取题目失败"
}
```

---

### 4.2 获取题目详情

**接口**: `GET /api/oj/problem/<problem_id>`

**功能**: 获取指定题目的详细信息

**路径参数**:
- `problem_id`: 题目ID (字符串)

**响应示例**:
```json
{
  "success": true,
  "problem": {
    "id": "1",
    "title": "两数之和",
    "description": "给定一个整数数组 nums 和一个目标值 target...",
    "input_format": "第一行包含数组元素，第二行包含目标值",
    "output_format": "输出两个索引，用空格分隔",
    "examples": [
      {
        "input": "2 7 11 15\n9",
        "output": "0 1",
        "explanation": "nums[0] + nums[1] = 2 + 7 = 9"
      }
    ],
    "test_cases": [
      {
        "input": "2 7 11 15\n9",
        "expected_output": "0 1"
      }
    ]
  }
}
```

**错误响应**:
```json
{
  "success": false,
  "error": "题目不存在"
}
```

---

### 4.3 提交代码

**接口**: `POST /api/oj/submit`

**功能**: 提交代码进行判题

**请求头**:
- `Content-Type: application/json`
- 需要登录认证

**请求体**:
```json
{
  "problem_id": "1",
  "code": "def solution(nums, target):\n    # 用户代码\n    pass"
}
```

**响应示例 - 通过所有测试**:
```json
{
  "success": true,
  "submission_id": 12345,
  "result": {
    "success": true,
    "status": "Accepted",
    "passed": 10,
    "total": 10,
    "execution_time": 0.023,
    "message": "恭喜！通过所有测试用例"
  }
}
```

**响应示例 - 部分通过**:
```json
{
  "success": true,
  "submission_id": 12346,
  "result": {
    "success": false,
    "status": "Wrong Answer",
    "passed": 7,
    "total": 10,
    "execution_time": 0.018,
    "failed_case": {
      "case_id": 8,
      "input": "1 2 3 4\n10",
      "expected": "无解",
      "actual": "IndexError: list index out of range"
    }
  }
}
```

**错误响应**:
```json
{
  "success": false,
  "error": "题目ID和代码不能为空"
}
```

---

### 4.4 获取提交历史

**接口**: `GET /api/oj/submissions`

**功能**: 获取当前用户的提交记录

**请求参数**:
- `problem_id` (可选): 筛选指定题目的提交记录

**响应示例**:
```json
{
  "success": true,
  "submissions": [
    {
      "id": 12346,
      "problem_id": "1",
      "status": "Wrong Answer",
      "passed_cases": 7,
      "total_cases": 10,
      "execution_time": 0.018,
      "submitted_at": "2024-01-15 14:30:25",
      "code": "def solution(nums, target):\n    ..."
    },
    {
      "id": 12345,
      "problem_id": "1",
      "status": "Accepted",
      "passed_cases": 10,
      "total_cases": 10,
      "execution_time": 0.023,
      "submitted_at": "2024-01-15 14:25:10",
      "code": "def solution(nums, target):\n    ..."
    }
  ]
}
```

---

### 4.5 清空提交历史

**接口**: `POST /api/oj/submissions/clear`

**功能**: 清空指定题目的所有提交记录

**请求体**:
```json
{
  "problem_id": "1"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "已清空 15 条提交记录",
  "deleted_count": 15
}
```

**错误响应**:
```json
{
  "success": false,
  "error": "缺少题目ID"
}
```

---

## 5. 判题引擎设计

### 5.1 判题流程

```
开始
 │
 ├─→ 加载题目数据 (JSON)
 │
 ├─→ 验证代码安全性
 │
 ├─→ 遍历测试用例
 │    │
 │    ├─→ 准备输入数据
 │    │
 │    ├─→ 执行用户代码 (沙箱环境)
 │    │
 │    ├─→ 比对输出结果
 │    │
 │    └─→ 记录用例结果 (通过/失败)
 │
 ├─→ 统计结果
 │    - 通过用例数
 │    - 总用例数
 │    - 执行时间
 │
 └─→ 返回判题结果
```

### 5.2 判题状态

| 状态码 | 英文名称 | 中文说明 |
|-------|---------|---------|
| AC | Accepted | 通过所有测试用例 |
| WA | Wrong Answer | 答案错误 |
| RE | Runtime Error | 运行时错误 |
| TLE | Time Limit Exceeded | 超时 |
| MLE | Memory Limit Exceeded | 内存超限 |
| CE | Compilation Error | 编译错误 (Python不适用) |

### 5.3 安全机制

**代码执行限制**:
```python
# 时间限制: 5秒
# 内存限制: 128MB
# 禁止操作: 文件IO, 网络访问, 系统调用
```

**沙箱策略**:
- 使用 `subprocess` 隔离进程
- 限制标准库导入 (白名单机制)
- 禁止危险函数: `eval()`, `exec()`, `open()`, `__import__()`

---

## 6. 前端页面设计

### 6.1 OJ 主页 (`/oj`)

**功能**:
- 展示所有题目列表
- 题目搜索和筛选
- 显示题目难度标签

**页面元素**:
```
┌─────────────────────────────────┐
│  🏆 Online Judge 题库            │
├─────────────────────────────────┤
│  [搜索框]  [难度筛选] [状态筛选] │
├─────────────────────────────────┤
│  📋 题目列表                     │
│  ┌───────────────────────────┐  │
│  │ 1. 两数之和        [简单]  │  │
│  │ 已通过 ✓                  │  │
│  ├───────────────────────────┤  │
│  │ 2. 回文判断        [中等]  │  │
│  │ 未尝试                    │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

### 6.2 题目详情页 (`/oj/problem/<problem_id>`)

**功能**:
- 显示题目描述、输入输出格式
- 提供代码编辑器
- 显示测试用例示例
- 提交代码按钮
- 查看提交历史

**页面布局**:
```
┌─────────────────┬──────────────────┐
│  题目描述        │  代码编辑器       │
│  - 题目标题      │  [Monaco Editor] │
│  - 难度标签      │                  │
│  - 问题描述      │  [提交代码]      │
│  - 输入格式      │  [运行测试]      │
│  - 输出格式      │                  │
│  - 示例用例      │  ──────────────  │
│                 │  提交历史         │
│                 │  - 状态          │
│                 │  - 通过率        │
│                 │  - 提交时间      │
└─────────────────┴──────────────────┘
```

---

## 7. 运行逻辑详解

### 7.1 用户提交代码流程

```python
# 步骤 1: 前端发送提交请求
POST /api/oj/submit
{
  "problem_id": "1",
  "code": "用户代码"
}

# 步骤 2: 后端验证登录状态
@login_required
def api_submit_code():
    user_id = session.get('user_id')
    # 验证用户身份

# 步骤 3: 调用判题引擎
judge_result = judge_engine.judge(problem_id, code)

# 步骤 4: 判题引擎执行
class JudgeEngine:
    def judge(self, problem_id, code):
        # 4.1 加载题目
        problem = self.load_problem(problem_id)
        
        # 4.2 遍历测试用例
        for test_case in problem['test_cases']:
            # 4.3 执行代码
            result = executor.execute_code(
                code, 
                inputs=test_case['input']
            )
            
            # 4.4 比对结果
            if result['output'] != test_case['expected_output']:
                return {
                    'status': 'Wrong Answer',
                    'failed_case': test_case
                }
        
        # 4.5 所有用例通过
        return {'status': 'Accepted'}

# 步骤 5: 保存提交记录
submission = Submission(
    user_id=user_id,
    problem_id=problem_id,
    code=code,
    status=judge_result['status'],
    ...
)
db.session.add(submission)
db.session.commit()

# 步骤 6: 返回结果给前端
return jsonify({
    'success': True,
    'result': judge_result
})
```

### 7.2 题目数据加载

**JSON 文件格式** (`Data/problem_1.json`):
```json
{
  "id": "1",
  "title": "两数之和",
  "description": "给定一个整数数组 nums 和一个目标值 target，请你在该数组中找出和为目标值的那两个整数，并返回它们的数组下标。",
  "difficulty": "Easy",
  "test_cases": [
    {
      "input": "2 7 11 15\n9",
      "expected_output": "0 1"
    },
    {
      "input": "3 2 4\n6",
      "expected_output": "1 2"
    }
  ]
}
```

---

## 8. 扩展功能设计

### 8.1 题目难度分级
- **简单 (Easy)**: 基础语法练习
- **中等 (Medium)**: 算法应用
- **困难 (Hard)**: 复杂算法和优化

### 8.2 用户排行榜
```sql
-- 统计用户通过题目数
SELECT user_id, COUNT(DISTINCT problem_id) as solved_count
FROM submission
WHERE status = 'Accepted'
GROUP BY user_id
ORDER BY solved_count DESC;
```

### 8.3 代码质量评分
- 时间复杂度分析
- 空间复杂度分析
- 代码风格检查 (PEP8)

### 8.4 讨论区功能
- 题目讨论
- 题解分享
- 代码评审

---

## 9. 性能优化

### 9.1 数据库优化
```python
# 使用索引加速查询
submission.query.filter_by(user_id=user_id, problem_id=problem_id).first()

# 限制返回数量
submission.query.limit(20).all()

# 使用 join 减少查询次数
db.session.query(Submission).join(User).filter(...)
```

### 9.2 缓存策略
```python
# 题目数据缓存 (使用 Flask-Caching)
@cache.cached(timeout=3600, key_prefix='problem')
def load_problem(problem_id):
    # 读取 JSON 文件
    pass
```

### 9.3 异步判题
```python
# 使用 Celery 实现异步任务队列
@celery.task
def async_judge(submission_id):
    submission = Submission.query.get(submission_id)
    result = judge_engine.judge(submission.problem_id, submission.code)
    submission.status = result['status']
    db.session.commit()
```

---

## 10. 安全性考虑

### 10.1 代码注入防护
```python
# 禁止危险操作
FORBIDDEN_KEYWORDS = ['__import__', 'eval', 'exec', 'open', 'os.system']

def validate_code(code):
    for keyword in FORBIDDEN_KEYWORDS:
        if keyword in code:
            raise SecurityError(f"禁止使用 {keyword}")
```

### 10.2 资源限制
```python
# 限制执行时间和内存
import resource
resource.setrlimit(resource.RLIMIT_CPU, (5, 5))  # 5秒CPU时间
resource.setrlimit(resource.RLIMIT_AS, (128*1024*1024, 128*1024*1024))  # 128MB内存
```

### 10.3 用户权限控制
```python
@login_required
def api_submit_code():
    # 验证用户是否有权限提交
    pass
```

---

## 11. 错误处理

### 11.1 常见错误类型

| 错误类型 | HTTP状态码 | 处理方式 |
|---------|-----------|---------|
| 未登录 | 401 | 重定向到登录页 |
| 题目不存在 | 404 | 返回错误提示 |
| 代码为空 | 400 | 返回错误提示 |
| 数据库错误 | 500 | 回滚事务，记录日志 |
| 判题超时 | 200 | 返回TLE状态 |

### 11.2 异常捕获示例
```python
try:
    judge_result = judge_engine.judge(problem_id, code)
except TimeoutError:
    return jsonify({'status': 'TLE'})
except MemoryError:
    return jsonify({'status': 'MLE'})
except Exception as e:
    return jsonify({'error': str(e)}), 500
```

---

## 12. 测试方案

### 12.1 单元测试
```python
def test_submit_code():
    """测试代码提交功能"""
    response = client.post('/api/oj/submit', json={
        'problem_id': '1',
        'code': 'def solution(): return [0, 1]'
    })
    assert response.status_code == 200
    assert response.json['success'] == True
```

### 12.2 集成测试
- 测试完整提交流程
- 测试判题引擎准确性
- 测试并发提交

---

## 13. 部署说明

### 13.1 环境要求
- Python 3.8+
- Flask 2.0+
- SQLAlchemy 1.4+
- SQLite 3

### 13.2 配置文件
```python
# config.py
SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
SECRET_KEY = 'your-secret-key'
JUDGE_TIMEOUT = 5  # 判题超时时间（秒）
MAX_MEMORY = 128   # 最大内存限制（MB）
```

### 13.3 启动命令
```bash
# 初始化数据库
flask db init
flask db migrate
flask db upgrade

# 启动应用
python app.py
```

---

## 14. 未来改进方向

1. **多语言支持**: 扩展支持 C++, Java, JavaScript 等语言
2. **实时排行榜**: 使用 WebSocket 实现实时更新
3. **AI 代码提示**: 集成 AI 助手提供解题思路
4. **竞赛模式**: 支持定时比赛和积分系统
5. **社区功能**: 添加关注、点赞、评论等社交功能

---

## 15. 参考资源

- [Flask 官方文档](https://flask.palletsprojects.com/)
- [SQLAlchemy 文档](https://www.sqlalchemy.org/)
- [LeetCode API 设计](https://leetcode.com/)
- [Judge0 开源判题系统](https://github.com/judge0/judge0)

---

**文档版本**: v1.0  
**最后更新**: 2024-01-15  
**维护者**: Python学习平台开发团队

