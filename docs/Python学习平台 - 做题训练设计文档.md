# Python学习平台 - 做题训练（OJ）设计文档

## 1. 功能概述

### 1.1 功能描述

做题训练功能为用户提供题目选择、题目详情查看、在线编写与提交代码判题、查看提交历史等能力，形成从学习到实践的闭环。

- 题目选择：下拉选择题目，自动加载题目详情
- 代码编写：基于 CodeMirror 的在线编辑器，支持快捷键与简单格式化
- 判题与结果：提交到后端 OJ 判题引擎，展示状态、通过用例数、执行时间，以及错误信息
- 提交历史：以模态框方式展示当前题目的历史提交记录（含完整代码与错误原因），支持按状态筛选（ALL/AC/WA/TLE/RE/CE）
- 错误详情：可折叠展示首个失败用例的 输入/期望/实际/错误 文本
- 结果清空：一键清空当前结果展示

### 1.2 适用范围

- 页面：`/oj`（模板：`templates/oj_home.html`）
- 入口：
  - 顶部导航“工具”下拉 → “做题训练”
  - 首页“快速开始” → “做题训练”按钮

### 1.3 功能特性

- 题目列表：从后端加载所有题目（ID、标题、简介）
- 题目详情：显示题目标题、ID、描述、示例（输入/输出）、函数名
- 在线编辑器：Python 语法高亮、行号、匹配括号、Ctrl+Enter 提交、基础格式化；按题目 sessionStorage 草稿持久化（自动保存/切换恢复）
- 判题结果：显示状态（AC/WA/TLE/RE/CE）、用例统计、执行时间；追加错误文本（如 ImportError、NameError）
- 提交历史：模态框展示最近 20 条提交，含完整代码与错误原因；支持按状态筛选

---

## 2. 技术架构

### 2.1 前端技术栈

- UI 框架：Bootstrap 5.3.0，Font Awesome 图标
- 编辑器：CodeMirror 5.65.2（在 `base.html` 中全局引入）
- JavaScript：原生 ES6+

### 2.2 后端技术栈

- Flask + SQLAlchemy
- 判题引擎：`utils/judge.py` 暴露 `load_problem`、`judge`
- 模型：`models/problem.py`（`Problem` 与 `Submission`）

### 2.3 数据模型

#### 2.3.1 Submission（提交记录）

```python
class Submission(db.Model):
    id: int
    user_id: int
    problem_id: int
    code: Text
    status: str  # AC/WA/TLE/RE/CE
    passed_cases: int
    total_cases: int
    error_message: Text
    execution_time: float
    submitted_at: datetime

    def to_dict(self):
        return {
            'id': ..., 'user_id': ..., 'problem_id': ..., 'code': ..., 'status': ...,
            'passed_cases': ..., 'total_cases': ..., 'error_message': ...,
            'execution_time': ..., 'submitted_at': 'YYYY-MM-DD HH:MM:SS'
        }
```

说明：`to_dict()` 已包含 `code` 字段，供前端展示历史代码。

#### 2.3.2 Problem（题目数据结构）

题目数据从 JSON 文件加载，包含以下字段：

```json
{
  "id": 1,
  "title": "最长回文子串",
  "description": "给你一个字符串 s，找到 s 中最长的回文子串...",
  "example": {
    "input": "\"babad\"",
    "output": "\"bab\""
  },
  "function_name": "longestPalindrome"
}
```

字段说明：
- `id`：题目唯一标识
- `title`：题目标题
- `description`：题目描述（多行文本）
- `example`（可选）：示例对象
  - `input`：示例输入值（字符串）
  - `output`：示例输出值（字符串）
- `function_name`（可选）：要求实现的函数名（字符串）

---

## 3. UI 设计

### 3.1 顶部工具条（题目选择区）

- 结构：标签（“选择题目:”）+ 下拉框（题目列表）+ “刷新”按钮 + “提交历史”按钮

示例代码：

```html
<div class="d-flex gap-2 controls-equal-height">
  <label for="problem-select" class="form-label mb-0 d-flex align-items-center text-nowrap">选择题目:</label>
  <select id="problem-select" class="form-select" style="min-width: 260px;"></select>
  <button id="refresh-problems" class="btn btn-outline-secondary d-flex align-items-center">
    <i class="fas fa-rotate me-1"></i> 刷新
  </button>
  <button id="open-submissions" class="btn btn-outline-info d-flex align-items-center">
    <i class="fas fa-history me-1"></i> 提交历史
  </button>
</div>
```

### 3.2 主体布局

- 左列：题目详情卡片
  - 标题（题目名）
  - `ID` 徽章
  - 描述（多行文本，`white-space: pre-wrap`）
  - 空行分隔（`<div class="mt-3"></div>`）
  - 示例（如果存在）：
    - 六级标题：**示例:**
    - 代码块：包含输入和输出，格式为 `输入：<input值>\n输出：<output值>`，其中"输入："和"输出："文字加粗
  - 函数名（如果存在）：
    - 六级标题：**函数名:**
    - 代码块：显示函数名
  - 最小高度：`min-height: 320px`（CSS：`#problem-detail`），内容超出后自适应增长
- 右列：代码提交与结果合并卡片
  - 标题：`代码提交`
  - 上半部分：编辑器容器（最小高度 260px）+ “格式化/提交判题”按钮
- 下半部分：结果区（深底浅字 `pre`，可滚动）+ “查看错误详情（折叠）/清空结果”按钮（切换题目时重置）

### 3.3 提交历史模态框

- 采用 Bootstrap `modal-lg`
- 顶部内嵌状态筛选 Select：ALL/AC/WA/TLE/RE/CE
- 内容区分四种状态模块：loading / empty / error / list
- 列表项卡片：
  - 顶部：状态徽章、提交时间、提交 ID
  - 统计：通过用例、总用例、执行时间
  - 错误：若存在，以“错误”徽章 + 文本展示
  - 代码：完整提交代码（限制最大高度，超出滚动）

---

## 4. 交互流程

### 4.1 页面初始化

1) 初始化编辑器（CodeMirror）
2) 绑定事件（选择题目、刷新、格式化、提交、打开历史、状态筛选、清空结果、草稿自动保存）
3) 加载题目列表；默认选第一题并加载详情与历史；如存在草稿则恢复到编辑器

### 4.2 选择题目

1) 下拉变更 → 记录当前 `problem_id`
2) 切换前保存上一题草稿；切换后恢复目标题草稿至编辑器
3) GET `/api/oj/problem/<id>` 加载详情
4) 清空运行/判题结果与错误详情
5) 更新历史（按题过滤）

### 4.3 提交判题

1) 校验：题目已选、代码非空
2) POST `/api/oj/submit`（`{ problem_id, code }`）
3) loading：按钮禁用 + 文案“提交中…”
4) 成功：渲染状态、通过用例数、总用例数、执行时间，若返回 `result.error` 或 `result.failed_case.error|message` 也输出“错误: ...”；渲染失败用例详情折叠面板
5) 完成：恢复按钮、刷新该题的提交历史

### 4.4 查看提交历史

1) 点击“提交历史” → 打开模态框
2) 显示 loading → GET `/api/oj/submissions?problem_id=<id>`
3) 若空 → 显示空状态；否则渲染卡片列表
4) 切换筛选值 → 基于最近一次结果的前端缓存即时过滤
5) 错误 → 显示错误提示块

### 4.5 清空结果

- 清空结果：结果标题行右侧“清空结果” → 重置结果区文本并折叠错误详情

---

## 5. API 接口设计

### 5.1 获取题目列表

- `GET /api/oj/problems`
- 响应：`{ success: true, problems: [{ id, title, description }, ...] }`

### 5.2 获取题目详情

- `GET /api/oj/problem/<id>`
- 响应：`{ success: true, problem: { id, title, description, example?, function_name? } }`
- 说明：
  - `example`（可选）：对象，包含 `input` 和 `output` 字段，示例输入和输出值
  - `function_name`（可选）：字符串，题目要求的函数名
  - 示例响应：
```json
{
  "success": true,
  "problem": {
    "id": 1,
    "title": "最长回文子串",
    "description": "给你一个字符串 s，找到 s 中最长的回文子串...",
    "example": {
      "input": "\"babad\"",
      "output": "\"bab\""
    },
    "function_name": "longestPalindrome"
  }
}
```

### 5.3 提交判题

- `POST /api/oj/submit`
- 入参：`{ problem_id: string|number, code: string }`
- 响应（示例）：

```json
{
  "success": true,
  "submission_id": 12,
  "result": {
    "status": "WA",
    "passed": 2,
    "total": 5,
    "execution_time": 12.3,
    "error": "ImportError: __import__ not found",
    "failed_case": {
      "input": "abc",
      "expected": "...",
      "actual": "...",
      "error": "NameError: ..."
    }
  }
}
```

### 5.4 获取提交历史

- `GET /api/oj/submissions?problem_id=<id>`（按题过滤）
- 响应：

```json
{
  "success": true,
  "submissions": [
    {
      "id": 1,
      "user_id": 1,
      "problem_id": 2,
      "code": "print('hello')",
      "status": "AC",
      "passed_cases": 5,
      "total_cases": 5,
      "error_message": null,
      "execution_time": 10.5,
      "submitted_at": "2024-01-01 12:00:00"
    }
  ]
}
```

---

## 6. 核心函数实现

### 6.1 初始化与事件绑定

```javascript
function initEditor() {
  // CodeMirror 初始化；on('change') 以 400ms 防抖保存当前题目的草稿到 sessionStorage
}
function bindEvents() {
  // 选择题目、刷新、格式化、提交、打开历史、状态筛选、清空结果、切换前保存草稿并恢复目标题草稿
}
```

### 6.2 加载题目与详情

```javascript
function loadProblems() {
  // GET /api/oj/problems → 渲染 select → 选中第一题 → 若有草稿则恢复到编辑器
}
function loadProblemDetail(id) {
  // GET /api/oj/problem/<id> → 渲染标题/ID/描述
  // 如果存在 example，渲染示例
  // 如果存在 function_name，渲染函数名
}
```

### 6.3 提交判题与结果渲染

```javascript
function submitCurrentCode() {
  // POST /api/oj/submit，渲染状态、用例、时间；输出错误摘要；渲染失败用例详情
}
```

### 6.4 提交历史加载/筛选

```javascript
function loadSubmissions(problemId) {
  // modal 内：loading → 请求 → empty 或 list → error
}
function renderSubmissionsFromCache() {
  // 基于 lastSubmissionsCache + currentStatusFilter 的前端过滤
}
```

### 6.5 失败用例详情折叠

```javascript
function renderFailedCase(failed) {
  // 将 input/expected/actual/error 渲染到 #oj-failed-detail 内，切换按钮控制折叠/展开
}
```

---

## 7. 样式设计

### 7.1 顶部控件等高与不换行

```css
.controls-equal-height>* { height: 38px; }
.controls-equal-height .form-label,
.controls-equal-height .btn { white-space: nowrap; }
.controls-equal-height .form-select { height: 38px; }
```

### 7.2 结果与代码块

```css
.code-output-area { min-height: 200px; max-height: 360px; overflow-y: auto; }
pre { white-space: pre-wrap; }
```

### 7.3 题目详情代码块样式

题目详情中的示例和函数名代码块样式：

```css
#problem-detail .oj-code-block {
  border-left: 3px solid #d8dce0;  /* 左侧灰色竖线 */
  padding: 0.5rem;
  padding-left: 0.75rem;
  background-color: transparent;   /* 默认背景，无特殊颜色 */
}
```

### 7.4 历史项卡片

- 左侧色条：根据状态（AC/WA/TLE/RE/CE）变化
- 代码容器：最大高度约 14 行，可滚动展示完整提交代码

### 7.5 失败用例详情

```css
#oj-failed-detail pre { min-height: 2.25rem; } /* 空值时也显示底色 */
```

### 7.6 题目详情最小高度

```css
#problem-detail { min-height: 320px; }
```

---

## 8. 数据流

### 8.1 题目加载

用户打开页面 → GET 题目列表 → 渲染下拉 → 自动加载第一题详情（包含标题、ID、描述、示例、函数名） → 如有草稿恢复编辑器

### 8.2 提交与结果

用户编写代码 → 点击提交 → POST 判题 → 返回结果/错误 → 在结果区展示 → 刷新历史 → 可展开失败用例详情

### 8.3 历史查看

点击“提交历史” → 打开 modal → GET 历史（按题过滤） → 渲染卡片 → 状态筛选前端过滤

---

## 9. 安全与健壮性

- XSS 防护：所有动态文本经 `escapeHtml` 输出
- 用户隔离：后端按 `session.user_id` 过滤提交与历史
- 错误兜底：网络/接口错误以 `.alert-danger` 呈现；结果区追加错误文本（包含 ImportError 等）
- 仅支持状态：ALL/AC/WA/TLE/RE/CE（前端筛选值与后端 `Submission.status` 保持一致）

---

## 10. 实现文件清单

- `templates/oj_home.html`：页面、DOM 结构与 JS 交互
- `templates/base.html`：全局依赖（Bootstrap、CodeMirror）与导航入口
- `models/problem.py`：`Submission.to_dict()` 含 `code` 字段，供历史展示
- `app.py`：`/api/oj/problems`、`/api/oj/problem/<id>`、`/api/oj/submit`、`/api/oj/submissions`
- `Data/problem_*.json`：题目数据文件，包含 `example` 和 `function_name` 字段

---

## 11. 测试用例（前端）

- 题目列表加载：成功/失败/为空
- 切换题目：详情正确刷新；历史按题过滤
- 题目详情展示：标题、ID、描述正确显示；显示示例输入输出和函数名
- 提交判题：AC/WA/TLE/RE/CE；错误信息（ImportError/NameError）正确显示
- 失败用例：折叠面板展示 input/expected/actual/error；空值也显示底色
- 结果清空：清空结果文本并折叠详情
- 历史模态：loading/empty/error/list 状态正确；筛选（ALL/AC/WA/TLE/RE/CE）正确

---

## 12. 未来优化

- 历史列表分页/虚拟滚动
- 代码高亮（Prism）与错误高亮
- 历史条目对比/Diff
- 模板代码与一键插入
- WebSocket 实时队列与判题进度
