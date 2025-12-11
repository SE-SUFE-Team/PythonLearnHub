# Python学习平台 - 数据库设计文档

## 1. 文档概述

### 1.1 文档目的
本文档详细描述了Python学习平台的数据库设计，包括所有数据表的结构、字段定义、约束条件、索引设计、关系说明以及业务逻辑。

### 1.2 数据库概述
- **数据库类型**: SQLite 3
- **ORM框架**: SQLAlchemy (Flask-SQLAlchemy)
- **数据库文件位置**: `instance/database.db`
- **字符编码**: UTF-8

### 1.3 设计原则
1. **用户中心设计**: 所有业务数据都围绕`users`表展开
2. **数据完整性**: 通过外键约束、唯一约束和非空约束保证数据一致性
3. **性能优化**: 合理设计索引，优化查询性能
4. **可扩展性**: 表结构设计支持未来功能扩展

---

## 2. 数据表详细设计

### 2.1 users（用户表）

**表说明**: 存储系统用户的基本信息，包括用户名、邮箱和加密后的密码。用户ID为8位随机数字（10000000-99999999）。

**表结构**:

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|---------|------|--------|------|
| id | INTEGER | PRIMARY KEY | - | 用户ID，8位随机数字（10000000-99999999），非自增 |
| username | VARCHAR(80) | NOT NULL | - | 用户名，允许重复 |
| email | VARCHAR(120) | UNIQUE, NOT NULL | - | 邮箱地址，全局唯一 |
| password_hash | VARCHAR(120) | NOT NULL | - | 密码哈希值（使用Werkzeug的generate_password_hash生成） |

**索引**:
- PRIMARY KEY: `id`
- UNIQUE INDEX: `email`

**业务规则**:
- 用户名允许重复，但邮箱必须唯一
- 密码使用Werkzeug的`generate_password_hash`进行哈希存储
- 用户ID在注册时随机生成，确保唯一性

**关联关系**:
- 一对一到 `user_profiles`
- 一对多到 `progress`
- 一对多到 `notes`
- 一对多到 `submissions`
- 一对多到 `code_executions`

---

### 2.2 user_profiles（用户配置表）

**表说明**: 存储用户的个性化配置信息，如头像等。与users表为一对一关系。

**表结构**:

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|---------|------|--------|------|
| id | INTEGER | PRIMARY KEY | AUTO_INCREMENT | 主键，自增 |
| user_id | INTEGER | FOREIGN KEY, UNIQUE, NOT NULL | - | 外键，关联users.id，唯一约束确保一对一关系 |
| avatar | VARCHAR(200) | NULL | NULL | 头像文件名，格式：`{user_id}_{timestamp}.{ext}` |
| created_at | DATETIME | NOT NULL | datetime.now | 创建时间 |
| updated_at | DATETIME | NOT NULL | datetime.now | 更新时间，自动更新 |

**索引**:
- PRIMARY KEY: `id`
- UNIQUE INDEX: `user_id`
- FOREIGN KEY: `user_id` → `users.id`

**业务规则**:
- 每个用户只能有一条配置记录（通过user_id的唯一约束保证）
- 头像文件存储在`static/avatars/`目录
- 更新头像时自动删除旧头像文件
- `updated_at`字段在记录更新时自动更新

**关联关系**:
- 多对一到 `users` (user_id)

---

### 2.3 progress（学习进度表）

**表说明**: 记录用户在每个学习模块的学习进度，包括浏览覆盖率、学习时长、习题完成度等。每个用户每个模块只有一条进度记录。

**表结构**:

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|---------|------|--------|------|
| progress_id | INTEGER | PRIMARY KEY | AUTO_INCREMENT | 主键，自增 |
| user_id | INTEGER | FOREIGN KEY, NOT NULL | - | 外键，关联users.id |
| module_id | VARCHAR(20) | NULL | NULL | 模块编号，如'variables', 'strings'等 |
| browse_coverage | FLOAT | NULL | NULL | 浏览覆盖率，范围0~1 |
| study_time | FLOAT | NULL | NULL | 学习时长，单位：分钟 |
| quiz_completion | FLOAT | NULL | NULL | 习题完成度，范围0~1 |
| progress_value | FLOAT | NOT NULL | - | 综合进度值，范围0~1，计算公式：`browse_coverage * 0.6 + study_norm * 0.4` |
| last_updated | DATETIME | NOT NULL | datetime.utcnow | 最后更新时间，自动更新 |

**索引**:
- PRIMARY KEY: `progress_id`
- UNIQUE INDEX: `(user_id, module_id)` - 确保每个用户每个模块只有一条记录
- FOREIGN KEY: `user_id` → `users.id`
- INDEX: `user_id` (用于快速查询用户的所有进度)

**业务规则**:
- 每个用户每个模块只能有一条进度记录（通过唯一约束保证）
- 进度更新采用合并策略：
  - `browse_coverage`: 取最大值（更高覆盖率）
  - `study_time`: 累加（累计学习时长）
  - `quiz_completion`: 取最大值（更高完成度）
- `progress_value`计算公式：
  - `study_norm = min(study_time / 10.0, 1.0)` (新建记录时使用120分钟作为基准)
  - `progress_value = browse_coverage * 0.6 + quiz_completion * 0.0 + study_norm * 0.4`
- `last_updated`字段在记录更新时自动更新

**关联关系**:
- 多对一到 `users` (user_id)

---

### 2.4 notes（笔记表）

**表说明**: 存储用户的学习笔记，支持标题和内容。用户可以创建、编辑、删除自己的笔记。

**表结构**:

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|---------|------|--------|------|
| note_id | INTEGER | PRIMARY KEY | AUTO_INCREMENT | 主键，自增 |
| user_id | INTEGER | FOREIGN KEY, NOT NULL | - | 外键，关联users.id |
| title | VARCHAR(100) | NULL | NULL | 笔记标题，可选 |
| content | TEXT | NOT NULL | - | 笔记内容，必填 |
| created_at | DATETIME | NOT NULL | datetime.now | 创建时间 |
| updated_at | DATETIME | NOT NULL | datetime.now | 更新时间，自动更新 |

**索引**:
- PRIMARY KEY: `note_id`
- FOREIGN KEY: `user_id` → `users.id`
- INDEX: `user_id` (用于快速查询用户的所有笔记)
- INDEX: `updated_at` (用于按时间排序)

**业务规则**:
- 笔记内容不能为空
- 标题可以为空，如果为空则使用内容的前100个字符作为标题
- 支持按标题或内容进行模糊搜索（使用ILIKE查询）
- `updated_at`字段在记录更新时自动更新
- 用户只能查看、编辑、删除自己的笔记

**关联关系**:
- 多对一到 `users` (user_id)

---

### 2.5 problems（题目表）

**表说明**: 存储OJ系统的题目信息。虽然题目数据主要存储在JSON文件中，但数据库表已定义，支持未来扩展为数据库存储。

**表结构**:

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|---------|------|--------|------|
| id | INTEGER | PRIMARY KEY | AUTO_INCREMENT | 主键，自增 |
| title | VARCHAR(200) | NOT NULL | - | 题目标题 |
| difficulty | VARCHAR(20) | NULL | NULL | 难度等级，如'Easy', 'Medium', 'Hard' |
| description | TEXT | NULL | NULL | 题目描述 |
| created_at | DATETIME | NULL | datetime.now | 创建时间 |

**索引**:
- PRIMARY KEY: `id`
- INDEX: `difficulty` (用于按难度筛选题目)

**业务规则**:
- 题目标题不能为空
- 题目详细信息和测试用例存储在JSON文件中（`Data/problem_*.json`和`Data/test_case_*.json`）
- 支持通过题目ID加载题目信息

**关联关系**:
- 一对多到 `submissions` (problem_id)

**JSON文件格式**:
- 题目信息: `Data/problem_{id}.json`
- 测试用例: `Data/test_case_{id}.json`

---

### 2.6 submissions（提交记录表）

**表说明**: 记录用户对题目的代码提交，包括代码、状态、通过用例数、执行时间等。是OJ系统的核心数据表。

**表结构**:

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|---------|------|--------|------|
| id | INTEGER | PRIMARY KEY | AUTO_INCREMENT | 主键，自增 |
| user_id | INTEGER | FOREIGN KEY, NOT NULL | - | 外键，关联users.id |
| problem_id | INTEGER | FOREIGN KEY, NOT NULL | - | 外键，关联problems.id |
| code | TEXT | NOT NULL | - | 用户提交的完整代码 |
| status | VARCHAR(20) | NULL | NULL | 判题状态：AC(通过), WA(答案错误), TLE(超时), RE(运行时错误), CE(编译错误) |
| passed_cases | INTEGER | NULL | 0 | 通过的测试用例数 |
| total_cases | INTEGER | NULL | 0 | 总测试用例数 |
| error_message | TEXT | NULL | NULL | 错误信息，JSON格式存储失败用例详情 |
| execution_time | FLOAT | NULL | NULL | 执行时间，单位：毫秒 |
| submitted_at | DATETIME | NULL | datetime.now | 提交时间 |

**索引**:
- PRIMARY KEY: `id`
- FOREIGN KEY: `user_id` → `users.id`
- FOREIGN KEY: `problem_id` → `problems.id`
- INDEX: `user_id` (用于快速查询用户的所有提交)
- INDEX: `problem_id` (用于快速查询题目的所有提交)
- INDEX: `submitted_at` (用于按时间排序)
- INDEX: `status` (用于按状态筛选)

**业务规则**:
- 提交代码不能为空
- 状态码说明：
  - `AC`: Accepted（通过所有测试用例）
  - `WA`: Wrong Answer（答案错误）
  - `TLE`: Time Limit Exceeded（超时）
  - `RE`: Runtime Error（运行时错误）
  - `CE`: Compilation Error（编译错误，Python中较少见）
- `error_message`字段存储失败用例的详细信息（JSON格式），包含输入、期望输出、实际输出、错误信息等
- `execution_time`记录代码执行时间，用于性能分析
- 支持按用户、题目、状态、时间进行查询和筛选
- 用户可以清空指定题目的所有提交记录

**关联关系**:
- 多对一到 `users` (user_id)
- 多对一到 `problems` (problem_id)

---

### 2.7 code_executions（代码执行历史表）

**表说明**: 记录用户在代码练习场执行的代码历史。系统自动管理记录数量，每个用户最多保留10条记录。

**表结构**:

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|---------|------|--------|------|
| id | INTEGER | PRIMARY KEY | AUTO_INCREMENT | 主键，自增 |
| user_id | INTEGER | FOREIGN KEY, NOT NULL | - | 外键，关联users.id |
| code | TEXT | NOT NULL | - | 执行的代码内容 |
| record_type | INTEGER | NULL | 0 | 记录类型，0=通用历史记录，预留扩展 |
| executed_at | DATETIME | NULL | datetime.now | 执行时间 |

**索引**:
- PRIMARY KEY: `id`
- FOREIGN KEY: `user_id` → `users.id`
- INDEX: `user_id` (用于快速查询用户的所有执行记录)
- INDEX: `executed_at` (用于按时间排序)

**业务规则**:
- 执行代码不能为空
- 每个用户最多保留10条执行记录，超过时自动删除最旧的记录
- `record_type`字段预留扩展，当前只使用0（通用历史记录）
- 支持按用户、类型、时间进行查询
- 用户可以清空自己的所有执行历史记录

**关联关系**:
- 多对一到 `users` (user_id)

---

## 3. 数据字典

### 3.1 状态码定义

#### Submission.status（提交状态）
- `AC`: Accepted - 通过所有测试用例
- `WA`: Wrong Answer - 答案错误
- `TLE`: Time Limit Exceeded - 超时
- `RE`: Runtime Error - 运行时错误
- `CE`: Compilation Error - 编译错误

#### CodeExecution.record_type（记录类型）
- `0`: 通用历史记录

### 3.2 模块ID定义

Progress.module_id支持的模块编号：
- `variables`: 变量和数据类型
- `strings`: 字符串操作
- `tuples`: 元组
- `lists`: 列表和列表生成式
- `flow_control`: 流程控制
- `functions`: 函数
- `exceptions`: 异常和断言
- `files`: 文件操作
- `regex`: 正则表达式

### 3.3 数据类型说明

- **INTEGER**: 整数类型
- **VARCHAR(n)**: 可变长度字符串，最大长度n
- **TEXT**: 长文本类型，无长度限制
- **FLOAT**: 浮点数类型
- **DATETIME**: 日期时间类型

---

## 4. 关系说明

### 4.1 实体关系图（ER图）

详见 `docs/ER图.md` 文件。

### 4.2 关系详细说明

#### 一对一关系（1:1）

**users ↔ user_profiles**
- 关系类型: 一对一
- 外键: `user_profiles.user_id` → `users.id`
- 约束: `user_profiles.user_id` 设置唯一约束
- 说明: 每个用户有且仅有一个配置记录

#### 一对多关系（1:N）

**users → progress**
- 关系类型: 一对多
- 外键: `progress.user_id` → `users.id`
- 说明: 一个用户可以有多个模块的学习进度记录
- 唯一约束: `(user_id, module_id)` 确保每个用户每个模块只有一条记录

**users → notes**
- 关系类型: 一对多
- 外键: `notes.user_id` → `users.id`
- 说明: 一个用户可以有多条笔记

**users → submissions**
- 关系类型: 一对多
- 外键: `submissions.user_id` → `users.id`
- 说明: 一个用户可以有多次代码提交

**users → code_executions**
- 关系类型: 一对多
- 外键: `code_executions.user_id` → `users.id`
- 说明: 一个用户可以有多次代码执行记录

**problems → submissions**
- 关系类型: 一对多
- 外键: `submissions.problem_id` → `problems.id`
- 说明: 一道题目可以有多条提交记录

### 4.3 数据流关系

```
用户(User)
├── 用户配置(UserProfile) [1:1]
│   └── 头像文件存储在 static/avatars/
├── 学习进度(Progress) [1:N]
│   └── 每个模块一条记录，记录学习进度
├── 学习笔记(Note) [1:N]
│   └── 支持标题和内容，可搜索
├── 代码提交(Submission) [1:N]
│   └── 关联题目(Problem) [N:1]
│       └── 题目信息存储在 JSON 文件
└── 代码执行历史(CodeExecution) [1:N]
    └── 最多保留10条记录
```

---

## 5. 索引设计

### 5.1 主键索引

所有表都使用自增主键作为聚集索引：
- `users.id`
- `user_profiles.id`
- `progress.progress_id`
- `notes.note_id`
- `problems.id`
- `submissions.id`
- `code_executions.id`

### 5.2 唯一索引

- `users.email`: 确保邮箱唯一性
- `user_profiles.user_id`: 确保用户配置一对一关系
- `progress(user_id, module_id)`: 确保每个用户每个模块只有一条进度记录

### 5.3 外键索引

所有外键字段自动创建索引，优化关联查询性能：
- `user_profiles.user_id`
- `progress.user_id`
- `notes.user_id`
- `submissions.user_id`
- `submissions.problem_id`
- `code_executions.user_id`

### 5.4 业务索引

**建议添加的索引**（可通过SQLAlchemy迁移实现）：

```sql
-- 提交记录表索引优化
CREATE INDEX idx_submissions_user_problem ON submissions(user_id, problem_id);
CREATE INDEX idx_submissions_submitted_at ON submissions(submitted_at DESC);
CREATE INDEX idx_submissions_status ON submissions(status);

-- 笔记表索引优化
CREATE INDEX idx_notes_user_updated ON notes(user_id, updated_at DESC);

-- 进度表索引优化
CREATE INDEX idx_progress_user_module ON progress(user_id, module_id);

-- 代码执行历史表索引优化
CREATE INDEX idx_code_executions_user_executed ON code_executions(user_id, executed_at DESC);
```

---

## 6. 数据完整性约束

### 6.1 外键约束

所有外键都设置了`nullable=False`，确保数据完整性：
- `user_profiles.user_id` → `users.id`
- `progress.user_id` → `users.id`
- `notes.user_id` → `users.id`
- `submissions.user_id` → `users.id`
- `submissions.problem_id` → `problems.id`
- `code_executions.user_id` → `users.id`

### 6.2 唯一约束

- `users.email`: 确保邮箱唯一性
- `user_profiles.user_id`: 确保用户配置一对一关系
- `progress(user_id, module_id)`: 确保每个用户每个模块只有一条进度记录

### 6.3 非空约束

关键字段设置了非空约束：
- `users.username`, `users.email`, `users.password_hash`
- `user_profiles.user_id`, `user_profiles.created_at`, `user_profiles.updated_at`
- `progress.user_id`, `progress.progress_value`, `progress.last_updated`
- `notes.user_id`, `notes.content`, `notes.created_at`, `notes.updated_at`
- `problems.title`
- `submissions.user_id`, `submissions.problem_id`, `submissions.code`
- `code_executions.user_id`, `code_executions.code`

### 6.4 默认值

时间字段、计数字段等都设置了合理的默认值：
- 时间字段: `datetime.now` 或 `datetime.utcnow`
- 计数字段: `0`
- 状态字段: `NULL`（允许为空）

### 6.5 数据范围约束

- `progress.browse_coverage`: 0~1
- `progress.quiz_completion`: 0~1
- `progress.progress_value`: 0~1
- `users.id`: 10000000~99999999（8位数字）

---

## 7. 业务逻辑说明

### 7.1 用户注册流程

1. 验证用户名、密码、邮箱不能为空
2. 检查邮箱是否已存在（唯一性检查）
3. 生成8位随机数字作为用户ID（10000000-99999999）
4. 检查用户ID是否已存在，如果存在则重新生成（最多尝试100次）
5. 使用`generate_password_hash`对密码进行哈希
6. 创建用户记录并保存到数据库

### 7.2 用户登录流程

1. 验证账号ID和密码不能为空
2. 根据用户ID查询用户
3. 使用`check_password_hash`验证密码
4. 登录成功后，将用户ID和用户名存入session

### 7.3 学习进度更新流程

1. 验证用户已登录
2. 验证模块ID存在
3. 查找该用户该模块的进度记录
4. 如果记录存在：
   - 合并策略更新：`browse_coverage`取最大值，`study_time`累加，`quiz_completion`取最大值
   - 重新计算`progress_value`
   - 更新`last_updated`
5. 如果记录不存在：
   - 创建新记录
   - 计算初始`progress_value`
6. 保存到数据库

### 7.4 代码提交流程

1. 验证用户已登录
2. 验证题目ID和代码不能为空
3. 调用判题引擎执行代码
4. 获取判题结果（状态、通过用例数、执行时间等）
5. 创建提交记录并保存到数据库
6. 返回判题结果给前端

### 7.5 代码执行历史管理

1. 用户执行代码后，创建执行记录
2. 查询该用户的执行记录总数
3. 如果超过10条，删除最旧的记录（按`executed_at`排序）
4. 保存新记录到数据库

### 7.6 头像上传流程

1. 验证用户已登录
2. 验证文件存在且不为空
3. 验证文件类型（png, jpg, jpeg, gif）
4. 生成文件名：`{user_id}_{timestamp}.{ext}`
5. 获取或创建用户配置记录
6. 如果存在旧头像，删除旧文件
7. 保存新头像文件
8. 更新数据库记录

---

## 8. 性能优化建议

### 8.1 查询优化

1. **分页查询**: 对于大量数据的查询（如提交记录、笔记），建议使用分页
2. **索引优化**: 根据实际查询场景添加合适的索引
3. **避免N+1查询**: 使用SQLAlchemy的`joinedload`或`selectinload`优化关联查询

### 8.2 数据清理

1. **代码执行历史**: 自动清理超过10条的记录
2. **提交记录**: 考虑定期归档或清理旧的提交记录
3. **用户数据**: 考虑实现用户数据导出和删除功能

### 8.3 缓存策略

1. **模块内容**: 模块内容可以缓存，减少文件读取
2. **用户信息**: 用户基本信息可以缓存到session
3. **题目信息**: 题目信息可以缓存，减少JSON文件读取

---

## 9. 数据迁移和版本管理

### 9.1 数据库初始化

数据库表通过SQLAlchemy的`db.create_all()`自动创建，在应用启动时执行。

### 9.2 未来扩展建议

1. **使用Flask-Migrate**: 建议使用Flask-Migrate进行数据库版本管理和迁移
2. **数据备份**: 定期备份数据库文件
3. **数据迁移脚本**: 编写数据迁移脚本，支持数据库结构变更

---

## 10. 安全考虑

### 10.1 密码安全

- 使用Werkzeug的`generate_password_hash`进行密码哈希
- 密码以哈希值形式存储，不存储明文密码

### 10.2 数据访问控制

- 用户只能访问自己的数据（进度、笔记、提交记录等）
- 通过session验证用户身份
- API接口使用`@login_required`装饰器保护

### 10.3 SQL注入防护

- 使用SQLAlchemy ORM，自动防护SQL注入
- 避免直接拼接SQL语句

### 10.4 文件上传安全

- 限制文件类型（只允许图片格式）
- 限制文件大小（最大2MB）
- 使用`secure_filename`处理文件名
- 验证文件内容，防止恶意文件上传

---

## 11. 附录

### 11.1 相关文档

- [ER图文档](ER图.md)
- [在线判题系统设计](online_judge_design.md)
- [代码执行历史设计](code_execution_history_design.md)
- [用户个人主页设计](profile.md)

### 11.2 模型文件位置

- `models/user.py`: User模型
- `models/user_profile.py`: UserProfile模型
- `models/progress.py`: Progress模型
- `models/notes.py`: Note模型
- `models/problem.py`: Problem和Submission模型
- `models/code_execution.py`: CodeExecution模型
- `models/__init__.py`: 数据库初始化

