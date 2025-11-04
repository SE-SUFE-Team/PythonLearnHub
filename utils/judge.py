import json
import os
import time
import traceback

class JudgeEngine:
    def __init__(self, data_dir='./Data'):
        self.data_dir = data_dir

    def load_problem(self, problem_id):
        """加载题目信息"""
        try:
            problem_file = os.path.join(self.data_dir, f'problem_{problem_id}.json')
            with open(problem_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def load_testcases(self, problem_id):
        """加载测试用例"""
        try:
            testcase_file = os.path.join(self.data_dir, f'test_case_{problem_id}.json')
            with open(testcase_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('testcases', [])
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def run_function_mode(self, code, function_name, test_input, time_limit=1.0):
        """函数模式执行"""
        result = {
            'success': False,
            'output': None,
            'error': '',
            'execution_time': 0
        }

        start_time = time.time()

        try:
            # 创建受限的执行环境
            exec_globals = {
                '__builtins__': {
                    'len': len, 'range': range, 'list': list,
                    'dict': dict, 'set': set, 'tuple': tuple,
                    'str': str, 'int': int, 'float': float,
                    'bool': bool, 'map': map, 'filter': filter,
                    'sorted': sorted, 'sum': sum, 'max': max,
                    'min': min, 'abs': abs, 'enumerate': enumerate,
                    'zip': zip,'round':round
                }
            }

            # 执行用户代码
            exec(code, exec_globals)

            # 检查函数是否存在
            if function_name not in exec_globals:
                result['error'] = f'函数 {function_name} 未定义'
                return result

            user_function = exec_globals[function_name]

            # 解析输入参数
            args = eval(test_input, {"__builtins__": {}})
            if not isinstance(args, (list, tuple)):
                args = (args,)

            # 调用函数
            output = user_function(*args)

            execution_time = time.time() - start_time

            if execution_time > time_limit:
                result['error'] = f'Time Limit Exceeded (>{time_limit}s)'
                return result

            result['success'] = True
            result['output'] = output
            result['execution_time'] = execution_time

        except Exception as e:
            result['error'] = f'{type(e).__name__}: {str(e)}'
            result['traceback'] = traceback.format_exc()

        return result

    def compare_output(self, user_output, expected_output):
        """比较输出结果"""
        return user_output == expected_output

    def judge(self, problem_id, code):
        """判题主函数"""
        problem = self.load_problem(problem_id)
        if not problem:
            return {'success': False, 'error': '题目不存在'}

        testcases = self.load_testcases(problem_id)
        if not testcases:
            return {'success': False, 'error': '测试用例不存在'}

        # 获取函数名
        function_name = problem.get('function_name')
        if not function_name:
            return {'success': False, 'error': '题目未指定函数名'}

        result = {
            'success': True,
            'status': 'AC',
            'passed': 0,
            'total': len(testcases),
            'failed_case': None,
            'execution_time': 0,
            'details': []
        }

        time_limit = problem.get('time_limit', 1.0)

        for idx, testcase in enumerate(testcases):
            test_input = testcase['input']
            expected_output = testcase['expected_output']

            run_result = self.run_function_mode(code, function_name, test_input, time_limit)

            case_result = {
                'case_id': idx + 1,
                'passed': False,
                'execution_time': run_result.get('execution_time', 0)
            }

            if not run_result['success']:
                result['status'] = 'TLE' if 'Time Limit' in run_result['error'] else 'RE'
                result['failed_case'] = {
                    'case_id': idx + 1,
                    'input': test_input,
                    'expected': expected_output,
                    'error': run_result['error']
                }
                case_result['error'] = run_result['error']
                result['details'].append(case_result)
                break

            if self.compare_output(run_result['output'], expected_output):
                result['passed'] += 1
                case_result['passed'] = True
            else:
                result['status'] = 'WA'
                result['failed_case'] = {
                    'case_id': idx + 1,
                    'input': test_input,
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
