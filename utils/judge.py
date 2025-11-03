import json
import os
import time
import traceback
from io import StringIO
import sys
import signal


class JudgeEngine:
    def __init__(self, data_dir='./Data'):
        self.data_dir = data_dir

    def load_problem(self, problem_id):
        """加载题目信息"""
        try:
            problem_file = os.path.join(self.data_dir, f'problem_{problem_id}.json')
            with open(problem_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
        except json.JSONDecodeError:
            return None

    def load_testcases(self, problem_id):
        """加载测试用例"""
        try:
            testcase_file = os.path.join(self.data_dir, f'test_case_{problem_id}.json')
            with open(testcase_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('testcases', [])
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []

    def run_code(self, code, input_data, time_limit=1.0):
        """执行用户代码"""
        result = {
            'success': False,
            'output': '',
            'error': '',
            'execution_time': 0
        }

        # 重定向输入输出
        old_stdin = sys.stdin
        old_stdout = sys.stdout

        sys.stdin = StringIO(input_data)
        sys.stdout = StringIO()

        start_time = time.time()

        try:
            # 创建受限的执行环境
            exec_globals = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'range': range,
                    'list': list,
                    'dict': dict,
                    'set': set,
                    'tuple': tuple,
                    'str': str,
                    'int': int,
                    'float': float,
                    'bool': bool,
                    'map': map,
                    'filter': filter,
                    'sorted': sorted,
                    'sum': sum,
                    'max': max,
                    'min': min,
                    'abs': abs,
                    'enumerate': enumerate,
                    'zip': zip,
                }
            }

            exec(code, exec_globals)

            execution_time = time.time() - start_time

            # 检查超时
            if execution_time > time_limit:
                result['error'] = f'Time Limit Exceeded (>{time_limit}s)'
                return result

            output = sys.stdout.getvalue().strip()
            result['success'] = True
            result['output'] = output
            result['execution_time'] = execution_time

        except Exception as e:
            result['error'] = f'{type(e).__name__}: {str(e)}'
            result['traceback'] = traceback.format_exc()
        finally:
            sys.stdin = old_stdin
            sys.stdout = old_stdout

        return result

    def compare_output(self, user_output, expected_output):
        """比较输出结果"""
        # 去除首尾空白字符并统一换行符
        user_lines = [line.strip() for line in user_output.strip().split('\n')]
        expected_lines = [line.strip() for line in expected_output.strip().split('\n')]

        return user_lines == expected_lines

    def judge(self, problem_id, code):
        """判题主函数"""
        problem = self.load_problem(problem_id)
        if not problem:
            return {
                'success': False,
                'error': '题目不存在'
            }

        testcases = self.load_testcases(problem_id)
        if not testcases:
            return {
                'success': False,
                'error': '测试用例不存在'
            }

        result = {
            'success': True,
            'status': 'AC',  # Accepted
            'passed': 0,
            'total': len(testcases),
            'failed_case': None,
            'execution_time': 0,
            'details': []
        }

        time_limit = problem.get('time_limit', 1.0)

        for idx, testcase in enumerate(testcases):
            input_data = testcase['input']
            expected_output = testcase['expected_output']

            run_result = self.run_code(code, input_data, time_limit)

            case_result = {
                'case_id': idx + 1,
                'passed': False,
                'execution_time': run_result.get('execution_time', 0)
            }

            if not run_result['success']:
                # 运行时错误或超时
                result['status'] = 'TLE' if 'Time Limit' in run_result['error'] else 'RE'
                result['failed_case'] = {
                    'case_id': idx + 1,
                    'input': input_data,
                    'expected': expected_output,
                    'error': run_result['error']
                }
                case_result['error'] = run_result['error']
                result['details'].append(case_result)
                break

            # 比较输出
            if self.compare_output(run_result['output'], expected_output):
                result['passed'] += 1
                case_result['passed'] = True
            else:
                # 答案错误
                result['status'] = 'WA'  # Wrong Answer
                result['failed_case'] = {
                    'case_id': idx + 1,
                    'input': input_data,
                    'expected': expected_output,
                    'actual': run_result['output']
                }
                case_result['actual'] = run_result['output']
                case_result['expected'] = expected_output
                result['details'].append(case_result)
                break

            result['execution_time'] = max(result['execution_time'], run_result['execution_time'])
            result['details'].append(case_result)

        return result


judge_engine = JudgeEngine()
