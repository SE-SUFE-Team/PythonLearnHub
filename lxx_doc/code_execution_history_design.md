# 代码执行历史记录 API 设计文档

## 1. 功能概述

代码执行历史记录功能是Python学习平台的核心辅助功能之一，用于记录、管理和查询用户的代码执行历史。该功能帮助用户：

- 📝 自动保存每次代码执行记录
- 🔍 快速查询历史执行记录
- 📊 区分不同类型的代码执行（通用练习 vs OJ提交）
- 🗑️ 清空历史记录以保持整洁
- 📈 追踪学习进度和代码演进

---

## 2. 功能特性

### 2.1 核心功能
- ✅ 自动记录代码执行
- ✅ 按类型分类存储（通用历史/OJ提交）
- ✅ 最多保留10条记录（自动清理旧记录）
- ✅ 支持按类型查询
- ✅ 支持单条记录详情查看
- ✅ 支持一键清空历史

### 2.2 业务规则
- 每个用户最多保存 **10条** 通用执行历史
- 超过10条时自动删除最旧的记录
- 记录类型：`0` = 通用历史，`1` = OJ提交（预留）
- 按执行时间倒序排列（最新的在前）

---

## 3. 数据库设计

### 3.1 数据表结构

#### `CodeExecution` 表

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|---------|------|------|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | 记录ID（主键） |
| `user_id` | INTEGER | NOT NULL, FOREIGN KEY → User.id | 用户ID（外键） |
| `code` | TEXT | NOT NULL | 执行的代码内容 |
| `record_type` | INTEGER | DEFAULT 0 | 记录类型：0=通用，1=OJ |
| `executed_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | 执行时间 |

#### 外键关系
```
CodeExecution.user_id → User.id
  ON DELETE: CASCADE（用户删除时级联删除历史记录）
```

### 3.2 索引设计
```sql
-- 用户ID + 执行时间复合索引（优化查询和清理）
CREATE INDEX idx_user_executed ON CodeExecution(user_id, executed_at);

-- 记录类型索引（优化按类型查询）
CREATE INDEX idx_record_type ON CodeExecution(record_type);
```

### 3.3 数据模型（ORM）

```python
class CodeExecution(db.Model):
    __tablename__ = 'code_execution'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    code = db.Column(db.Text, nullable=False)
    record_type = db.Column(db.Integer, default=0)
    executed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联关系
    user = db.relationship('User', backref='code_executions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'record_type': self.record_type,
            'executed_at': self.executed_at.strftime('%Y-%m-%d %H:%M:%S')
        }
```

---

## 4. API 接口设计

### 4.1 代码执行接口（自动记录）

**接口地址**: `POST /api/execute`

**功能**: 执行Python代码并自动保存到历史记录

#### 请求参数
```json
{
  "code": "print('Hello, World!')",
  "inputs": "可选输入数据"
}
```

#### 响应示例（成功）
```json
{
  "success": true,
  "output": "Hello, World!\n",
  "error": null,
  "execution_time": "0.005s",
  "timestamp": "2024-01-15 10:30:45",
  "record_id": 123
}
```

#### 业务逻辑
```
1. 验证用户登录状态（从session获取user_id）
2. 执行代码（调用 executor.execute_code）
3. 创建执行记录
4. 检查用户记录数是否超过10条
5. 如果超过，删除最旧的记录
6. 提交数据库事务
7. 返回执行结果 + 记录ID
```

#### 错误处理
- 代码为空 → 400 错误
- 执行失败 → 返回错误信息但仍记录
- 数据库保存失败 → 回滚事务，打印警告日志

---

### 4.2 查询历史记录接口

**接口地址**: `GET /api/executions/history`

**功能**: 查询用户的代码执行历史（最近10条）

#### 请求参数（Query String）
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `type` | integer | 否 | 记录类型：0=通用，1=OJ（默认0） |

#### 请求示例
```
GET /api/executions/history?type=0
```

#### 响应示例（成功）
```json
{
  "success": true,
  "count": 10,
  "records": [
    {
      "id": 123,
      "code": "print('Hello')",
      "record_type": 0,
      "executed_at": "2024-01-15 10:30:45"
    },
    {
      "id": 122,
      "code": "x = 10\nprint(x)",
      "record_type": 0,
      "executed_at": "2024-01-15 10:25:30"
    }
  ]
}
```

#### 响应示例（失败）
```json
{
  "success": false,
  "error": "查询失败: 数据库连接错误"
}
```

#### 业务逻辑
```
1. 从session获取当前用户ID
2. 从查询参数获取 record_type（默认0）
3. 构建查询：
   - 过滤 user_id
   - 可选过滤 record_type
   - 按 executed_at 降序
   - 限制10条
4. 执行查询
5. 将结果转换为字典列表返回
```

---

### 4.3 查询单条记录详情接口

**接口地址**: `GET /api/executions/<record_id>`

**功能**: 获取特定执行记录的完整信息

#### 请求示例
```
GET /api/executions/123
```

#### 响应示例（成功）
```json
{
  "success": true,
  "record": {
    "id": 123,
    "code": "for i in range(5):\n    print(i)",
    "record_type": 0,
    "executed_at": "2024-01-15 10:30:45"
  }
}
```

#### 响应示例（记录不存在）
```json
{
  "success": false,
  "error": "记录不存在"
}
```

#### 业务逻辑
```
1. 根据 record_id 查询数据库
2. 如果记录不存在 → 返回 404
3. 如果记录存在 → 返回完整信息
```

---

### 4.4 清空历史记录接口

**接口地址**: `POST /api/executions/clear`

**功能**: 清空当前用户的所有代码执行历史

#### 请求示例
```
POST /api/executions/clear
```

#### 响应示例（成功）
```json
{
  "success": true,
  "message": "历史记录已清空"
}
```

#### 响应示例（失败）
```json
{
  "success": false,
  "error": "清空失败: 数据库错误"
}
```

#### 业务逻辑
```
1. 从session获取当前用户ID
2. 删除该用户的所有 CodeExecution 记录
3. 提交数据库事务
4. 返回成功消息
5. 如果失败，回滚事务并返回错误
```

---

## 5. 业务流程图

### 5.1 代码执行并记录流程

```
用户提交代码
    ↓
验证用户登录
    ↓
执行代码 (SafeExecutor)
    ↓
创建执行记录
    ↓
检查记录数 > 10?
    ├─ 是 → 删除最旧记录
    └─ 否 → 跳过
    ↓
提交数据库事务
    ↓
返回结果 + 记录ID
```

### 5.2 查询历史记录流程

```
用户请求历史记录
    ↓
获取用户ID (session)
    ↓
获取筛选参数 (type)
    ↓
构建查询条件
    ↓
执行查询 (最近10条)
    ↓
转换为JSON格式
    ↓
返回记录列表
```

### 5.3 清空历史记录流程

```
用户点击清空
    ↓
确认操作
    ↓
发送DELETE请求
    ↓
删除该用户所有记录
    ↓
提交数据库事务
    ↓
返回成功提示
    ↓
前端刷新列表
```

---

## 6. 安全性设计

### 6.1 权限控制
- ✅ 所有接口需要用户登录（通过session验证）
- ✅ 用户只能查看/删除自己的记录
- ✅ 使用 `user_id` 过滤确保数据隔离

### 6.2 数据验证
```python
# 代码长度限制（防止恶意存储）
if len(code) > 10000:
    return jsonify({'error': '代码过长'}), 400

# 记录类型验证
if record_type not in [0, 1]:
    record_type = 0  # 默认值
```

### 6.3 SQL注入防护
- 使用 SQLAlchemy ORM（参数化查询）
- 避免直接拼接SQL字符串

### 6.4 XSS防护
- 前端展示代码时使用 `<pre>` 标签转义
- 使用 Jinja2 自动转义

---

## 7. 性能优化

### 7.1 数据库优化
- ✅ 创建复合索引 `(user_id, executed_at)`
- ✅ 限制查询结果数量（LIMIT 10）
- ✅ 自动清理旧记录（避免表膨胀）

### 7.2 查询优化
```python
# 优化前（全表扫描）
records = CodeExecution.query.filter_by(user_id=uid).all()

# 优化后（使用索引 + 限制数量）
records = (CodeExecution.query
           .filter_by(user_id=uid)
           .order_by(desc(CodeExecution.executed_at))
           .limit(10)
           .all())
```

### 7.3 缓存策略（可选）
```python
# 使用 Flask-Caching 缓存热门查询
@cache.memoize(timeout=60)
def get_recent_executions(user_id):
    return CodeExecution.query.filter_by(
        user_id=user_id
    ).order_by(desc(CodeExecution.executed_at)).limit(10).all()
```

---

## 8. 错误处理

### 8.1 异常类型

| 错误类型 | HTTP状态码 | 处理方式 |
|---------|-----------|---------|
| 用户未登录 | 401 | 返回错误消息，前端跳转登录 |
| 记录不存在 | 404 | 返回友好提示 |
| 数据库错误 | 500 | 回滚事务 + 打印日志 |
| 参数错误 | 400 | 返回具体错误信息 |

### 8.2 错误响应格式

```json
{
  "success": false,
  "error": "具体错误描述",
  "error_code": "ERR_DB_QUERY_FAILED"  // 可选
}
```

---

## 9. 前端集成示例

### 9.1 查询历史记录

```javascript
async function loadHistory() {
    const response = await fetch('/api/executions/history?type=0');
    const data = await response.json();
    
    if (data.success) {
        data.records.forEach(record => {
            console.log(record.code);
        });
    } else {
        alert(data.error);
    }
}
```

### 9.2 清空历史记录

```javascript
async function clearHistory() {
    if (!confirm('确定要清空所有历史记录吗？')) return;
    
    const response = await fetch('/api/executions/clear', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    });
    
    const data = await response.json();
    if (data.success) {
        alert('清空成功');
        loadHistory();  // 刷新列表
    } else {
        alert('清空失败: ' + data.error);
    }
}
```

---

## 10. 测试用例

### 10.1 功能测试

| 测试场景 | 预期结果 |
|---------|---------|
| 执行代码并保存 | 返回 record_id |
| 查询空历史 | 返回空数组 |
| 查询10条记录 | 返回10条 |
| 执行第11次代码 | 自动删除最旧记录 |
| 清空历史 | 所有记录被删除 |
| 未登录查询 | 返回401错误 |

### 10.2 性能测试

```python
# 测试1000次连续执行
import time

start = time.time()
for i in range(1000):
    response = requests.post('/api/execute', json={'code': 'print(1)'})
    assert response.json()['success']
end = time.time()

print(f'平均响应时间: {(end - start) / 1000:.3f}秒')
# 预期: < 0.1秒/次
```

---

## 11. 未来扩展

### 11.1 计划功能
- [ ] 支持代码标签分类
- [ ] 支持代码收藏功能
- [ ] 支持历史记录导出（JSON/CSV）
- [ ] 支持代码对比（Diff）
- [ ] 支持执行结果可视化
- [ ] 支持分享代码片段

### 11.2 数据库迁移
```python
# 添加新字段示例
class CodeExecution(db.Model):
    # ...existing fields...
    tags = db.Column(db.String(200))  # 标签
    is_favorite = db.Column(db.Boolean, default=False)  # 收藏
    share_token = db.Column(db.String(32), unique=True)  # 分享令牌
```

---

## 12. 运维监控

### 12.1 关键指标

- 📊 每日执行总次数
- 📊 平均响应时间
- 📊 数据库表大小
- 📊 错误率

### 12.2 日志记录

```python
import logging

logger = logging.getLogger(__name__)

@app.route('/api/execute', methods=['POST'])
def execute_code():
    logger.info(f'User {session.get("user_id")} executing code')
    # ...existing code...
    logger.debug(f'Saved record ID: {execution_record.id}')
```

---

## 13. 总结

代码执行历史记录功能是学习平台的重要辅助工具，通过自动记录、智能清理、便捷查询等特性，帮助用户更好地追踪学习进度。该功能具有以下优势：

- ✅ **自动化**: 无需用户手动保存
- ✅ **高效**: 索引优化 + 限制数量
- ✅ **安全**: 权限隔离 + 数据验证
- ✅ **易用**: RESTful API + 清晰响应

---

**文档版本**: v1.0  
**最后更新**: 2024-01-15  
**维护者**: Python学习平台开发团队

