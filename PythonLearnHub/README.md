# Python学习平台

一个功能全面、交互式的 Python 编程学习 Web 应用，提供实时代码执行和结构化学习路径。

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动应用

```bash
python app.py
```

应用将在 `http://localhost:5000` 启动。

## 功能特性

### 学习模块
- **变量和数据类型** - Python基本数据类型和变量操作
- **字符串操作** - 字符串的各种操作方法
- **列表和列表生成式** - 列表操作和列表生成式
- **元组** - 元组的特性和使用场景
- **流程控制** - 条件语句和循环语句
- **函数** - 函数的定义和使用
- **异常和断言** - 异常处理和断言使用
- **文件操作** - 文件读写和处理
- **正则表达式** - 正则表达式的使用

### 工具功能
- **代码练习场** - 在线Python代码执行环境
- **正则表达式工具** - 正则表达式测试和调试
- **安全代码执行** - 内置安全执行器，支持大部分Python语法
- **代码高亮** - 语法高亮显示
- **示例代码** - 丰富的示例代码和练习



## 项目结构

```
python_learning_platform/
├── app/                          # 主应用目录
│   ├── __init__.py              # Flask应用工厂
│   ├── models/                  # 数据模型
│   ├── views/                   # 视图蓝图
│   │   ├── main.py             # 主页和导航
│   │   ├── variables.py        # 变量和数据类型
│   │   ├── strings.py          # 字符串操作
│   │   ├── tuples.py           # 元组
│   │   ├── lists.py            # 列表和列表生成式
│   │   ├── flow_control.py     # 流程控制
│   │   ├── functions.py        # 函数
│   │   ├── exceptions.py       # 异常和断言
│   │   ├── files.py            # 文件操作
│   │   ├── regex.py            # 正则表达式
│   │   └── tools.py            # 工具页面
│   ├── utils/                   # 工具模块
│   │   ├── safe_executor.py    # 安全代码执行器
│   │   └── content_manager.py  # 内容管理
│   ├── static/                  # 静态资源
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── templates/               # 模板文件
│       ├── base.html
│       ├── index.html
│       ├── modules/
│       └── tools/
├── config.py                    # 配置文件
├── requirements.txt             # 依赖管理
├── app.py                      # 主启动文件
├── run.py                      # 备用启动脚本
└── README.md                   # 项目说明
```

## 技术栈

- **后端**: Flask 2.3.3
- **前端**: Bootstrap 5.3.0, JavaScript
- **代码高亮**: Prism.js
- **图标**: Font Awesome 6.4.0

## 开发说明

### 添加新模块

1. 在 `app/views/` 中创建新的蓝图文件
2. 在 `app/utils/content_manager.py` 中添加模块内容
3. 在 `app/__init__.py` 中注册蓝图
4. 创建对应的模板文件

### 自定义配置

修改 `config.py` 文件来调整应用配置：

```python
class DevelopmentConfig(Config):
    DEBUG = True
    PORT = 5000
```

## 许可证

本项目仅供教学和学习使用。
