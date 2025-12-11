"""
生成数据库ER图的PNG图片
需要安装: pip install graphviz
"""
from graphviz import Digraph

# 创建有向图
dot = Digraph(comment='Python学习平台数据库ER图', format='png')
dot.attr(rankdir='LR', size='12,8')
dot.attr('node', shape='record', style='rounded')

# 定义实体
dot.node('users', '''users|
id: INTEGER (PK)|
username: VARCHAR(80) (NOT NULL)|
email: VARCHAR(120) (UNIQUE, NOT NULL)|
password_hash: VARCHAR(120) (NOT NULL)''')

dot.node('user_profiles', '''user_profiles|
id: INTEGER (PK)|
user_id: INTEGER (FK, UNIQUE, NOT NULL)|
avatar: VARCHAR(200)|
created_at: DATETIME (NOT NULL)|
updated_at: DATETIME (NOT NULL)''')

dot.node('progress', '''progress|
progress_id: INTEGER (PK)|
user_id: INTEGER (FK, NOT NULL)|
module_id: VARCHAR(20)|
browse_coverage: FLOAT (0~1)|
study_time: FLOAT (分钟)|
quiz_completion: FLOAT (0~1)|
progress_value: FLOAT (NOT NULL, 0~1)|
last_updated: DATETIME (NOT NULL)|
UNIQUE(user_id, module_id)''')

dot.node('notes', '''notes|
note_id: INTEGER (PK)|
user_id: INTEGER (FK, NOT NULL)|
title: VARCHAR(100)|
content: TEXT (NOT NULL)|
created_at: DATETIME (NOT NULL)|
updated_at: DATETIME (NOT NULL)''')

dot.node('problems', '''problems|
id: INTEGER (PK)|
title: VARCHAR(200) (NOT NULL)|
difficulty: VARCHAR(20)|
description: TEXT|
created_at: DATETIME''')

dot.node('submissions', '''submissions|
id: INTEGER (PK)|
user_id: INTEGER (FK, NOT NULL)|
problem_id: INTEGER (FK, NOT NULL)|
code: TEXT (NOT NULL)|
status: VARCHAR(20)|
passed_cases: INTEGER (default 0)|
total_cases: INTEGER (default 0)|
error_message: TEXT|
execution_time: FLOAT (毫秒)|
submitted_at: DATETIME''')

dot.node('code_executions', '''code_executions|
id: INTEGER (PK)|
user_id: INTEGER (FK, NOT NULL)|
code: TEXT (NOT NULL)|
record_type: INTEGER (default 0)|
executed_at: DATETIME''')

# 定义关系
dot.edge('users', 'user_profiles', label='1:1', style='bold')
dot.edge('users', 'progress', label='1:N', style='bold')
dot.edge('users', 'notes', label='1:N', style='bold')
dot.edge('users', 'submissions', label='1:N', style='bold')
dot.edge('users', 'code_executions', label='1:N', style='bold')
dot.edge('problems', 'submissions', label='1:N', style='bold')

# 渲染图片
output_file = 'ER图'
dot.render(output_file, format='png', cleanup=True)
print(f"ER图已生成: {output_file}.png")

