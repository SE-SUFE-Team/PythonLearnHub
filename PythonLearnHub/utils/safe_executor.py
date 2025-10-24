"""
统一的安全代码执行器
整合所有Python学习模块的安全代码执行功能
"""

import ast
import io
import sys
import traceback
import operator
import re
import math
import time
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, Any, Tuple


class SafeCodeExecutor:
    """统一的安全代码执行器"""
    
    def __init__(self):
        # 安全的内置函数白名单
        self.safe_builtins = {
            'abs': abs,
            'all': all,
            'any': any,
            'bool': bool,
            'dict': dict,
            'enumerate': enumerate,
            'float': float,
            'int': int,
            'len': len,
            'list': list,
            'max': max,
            'min': min,
            'print': print,
            'range': range,
            'reversed': reversed,
            'round': round,
            'set': set,
            'sorted': sorted,
            'str': str,
            'sum': sum,
            'tuple': tuple,
            'type': type,
            'zip': zip,
            'map': map,
            'filter': filter,
            'chr': chr,
            'ord': ord,
            'hex': hex,
            'oct': oct,
            'bin': bin,
            'pow': pow,
            'divmod': divmod,
            'isinstance': isinstance,
            'hasattr': hasattr,
            'getattr': getattr,
            'repr': repr,
            'format': format,
        }
        
        # 允许的模块
        self.allowed_modules = {
            're': re,
            'math': math,
        }
        
        # 允许的异常类型
        self.allowed_exceptions = {
            'Exception': Exception,
            'ValueError': ValueError,
            'TypeError': TypeError,
            'IndexError': IndexError,
            'KeyError': KeyError,
            'AssertionError': AssertionError,
            'ZeroDivisionError': ZeroDivisionError,
            'AttributeError': AttributeError,
            'NameError': NameError,
            'SyntaxError': SyntaxError,
            'RuntimeError': RuntimeError,
        }
        
        # 危险关键字
        self.dangerous_keywords = [
            'import os', 'import sys', 'import subprocess', 'import shutil',
            'from os', 'from sys', 'from subprocess', 'from shutil',
            'eval(', 'exec(', 'compile(', 'open(', 'file(',
            'input(', 'raw_input(', '__import__(', 'globals()',
            'locals()', 'vars()', 'dir()', 'help(', 'exit(',
            'quit(', 'copyright', 'credits', 'license',
        ]
        
        # 允许的AST节点类型
        self.allowed_nodes = (
            ast.Expression, ast.Constant, ast.Name, ast.Load, ast.Store,
            ast.BinOp, ast.UnaryOp, ast.Compare, ast.BoolOp, ast.And, ast.Or,
            ast.List, ast.Tuple, ast.Dict, ast.Set, ast.Subscript,
            ast.Slice, ast.Call, ast.keyword, ast.Assign, ast.AugAssign,
            ast.If, ast.For, ast.While, ast.Break, ast.Continue, ast.Pass,
            ast.Return, ast.FunctionDef, ast.arguments, ast.arg, ast.Module,
            ast.Expr, ast.JoinedStr, ast.FormattedValue, ast.Attribute,
            ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp,
            ast.comprehension, ast.Try, ast.ExceptHandler, ast.Raise,
            # 操作符
            ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
            ast.LShift, ast.RShift, ast.BitOr, ast.BitXor, ast.BitAnd, ast.MatMult,
            ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Is, ast.IsNot,
            ast.In, ast.NotIn, ast.UAdd, ast.USub, ast.Not, ast.Invert,
        )
        
        # 允许的方法调用
        self.allowed_methods = {
            # 列表方法
            'append', 'extend', 'insert', 'remove', 'pop', 'clear', 
            'index', 'count', 'sort', 'reverse', 'copy',
            # 字符串方法
            'upper', 'lower', 'strip', 'lstrip', 'rstrip', 'split', 
            'join', 'replace', 'find', 'rfind', 'startswith', 'endswith',
            'format', 'capitalize', 'title', 'swapcase', 'center',
            'ljust', 'rjust', 'zfill', 'encode', 'decode',
            # 字典方法
            'keys', 'values', 'items', 'get', 'update', 'setdefault',
            'popitem', 'clear', 'copy',
            # 集合方法
            'add', 'discard', 'remove', 'pop', 'clear', 'union',
            'intersection', 'difference', 'symmetric_difference',
            'update', 'intersection_update', 'difference_update',
            'symmetric_difference_update', 'issubset', 'issuperset',
            'isdisjoint', 'copy',
            # 正则表达式方法
            'match', 'search', 'findall', 'finditer', 'split', 'sub', 'subn',
            'compile', 'escape', 'purge',
        }
    
    def safe_import(self, name, globals=None, locals=None, fromlist=(), level=0):
        """安全的import函数"""
        if name in self.allowed_modules:
            return self.allowed_modules[name]
        else:
            raise ImportError(f"模块 '{name}' 不被允许导入")
    
    def is_safe_code(self, code: str) -> Tuple[bool, str]:
        """检查代码是否安全"""
        # 检查危险关键字
        code_lower = code.lower()
        for keyword in self.dangerous_keywords:
            if keyword in code_lower:
                return False, f"代码包含潜在危险操作: {keyword}"
        
        # 解析AST并检查节点
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"语法错误: {str(e)}"
        
        for node in ast.walk(tree):
            if not isinstance(node, self.allowed_nodes):
                return False, f"不允许的操作: {type(node).__name__}"
            
            # 检查导入语句
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name not in self.allowed_modules:
                        return False, f"不允许导入模块: {alias.name}"
            
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module not in self.allowed_modules:
                    return False, f"不允许从模块导入: {node.module}"
            
            # 检查函数调用
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    # 检查函数名是否在安全列表中
                    func_name = node.func.id
                    if (func_name not in self.safe_builtins and 
                        func_name not in self.allowed_exceptions):
                        # 允许用户自定义函数
                        pass
                elif isinstance(node.func, ast.Attribute):
                    # 检查方法调用
                    if hasattr(node.func, 'attr') and node.func.attr not in self.allowed_methods:
                        return False, f"不允许调用方法: {node.func.attr}"
            
            # 检查属性访问
            elif isinstance(node, ast.Attribute):
                dangerous_attrs = [
                    '__class__', '__bases__', '__subclasses__', '__import__',
                    '__builtins__', '__globals__', '__locals__', '__dict__',
                    '__code__', '__func__', '__self__'
                ]
                if node.attr in dangerous_attrs:
                    return False, f"不允许访问属性: {node.attr}"
        
        return True, "代码安全"
    
    def convert_for_json(self, obj):
        """转换对象为JSON可序列化的格式"""
        if isinstance(obj, set):
            return list(obj)
        elif callable(obj):
            return f"<function {getattr(obj, '__name__', 'unknown')}>"
        elif isinstance(obj, (list, tuple)):
            return [self.convert_for_json(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: self.convert_for_json(value) for key, value in obj.items()}
        elif hasattr(obj, '__dict__'):
            # 处理自定义对象
            return f"<{type(obj).__name__} object>"
        else:
            return obj
    
    def execute_code(self, code: str, inputs: list = None) -> Dict[str, Any]:
        """安全执行Python代码"""
        # 安全检查
        is_safe, message = self.is_safe_code(code)
        if not is_safe:
            return {
                'success': False,
                'error': message,
                'output': '',
                'variables': {},
                'execution_time': 0
            }
        
        # 创建安全的执行环境
        safe_globals = {
            '__builtins__': self.safe_builtins.copy(),
            '__name__': '__main__',
            '__import__': self.safe_import,
        }
        
        # 添加允许的模块
        safe_globals.update(self.allowed_modules)
        
        # 添加允许的异常类型
        safe_globals.update(self.allowed_exceptions)
        
        # 处理输入（如果有的话）
        if inputs:
            # 简单的输入处理，模拟input函数
            input_iter = iter(inputs)
            def mock_input(prompt=''):
                try:
                    value = next(input_iter)
                    print(f"{prompt}{value}")
                    return value
                except StopIteration:
                    return ''
            safe_globals['input'] = mock_input
        
        # 捕获输出
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        start_time = time.time()
        
        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code, safe_globals, safe_globals)
            
            execution_time = time.time() - start_time
            output = stdout_capture.getvalue()
            error_output = stderr_capture.getvalue()
            
            # 过滤用户定义的变量
            user_variables = {
                k: self.convert_for_json(v) 
                for k, v in safe_globals.items() 
                if not k.startswith('__') and k not in self.safe_builtins and k not in self.allowed_modules
            }
            
            return {
                'success': True,
                'output': output,
                'error': error_output if error_output else None,
                'variables': user_variables,
                'execution_time': round(execution_time, 3)
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_output = stderr_capture.getvalue()
            
            return {
                'success': False,
                'error': str(e),
                'output': stdout_capture.getvalue(),
                'traceback': traceback.format_exc(),
                'execution_time': round(execution_time, 3)
            }


# 创建全局执行器实例
executor = SafeCodeExecutor()


def create_executor():
    """创建代码执行器实例"""
    return SafeCodeExecutor()