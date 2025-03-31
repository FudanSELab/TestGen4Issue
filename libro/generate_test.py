import json
import re
from tqdm import tqdm
from search_code import get_repo_all_files,search_code
from query_gpt import query_llm_5
from definitions import ROOT_DIR

REPO_DATA_PATH = ROOT_DIR + "/data/SWE-bench_Lite"
STORE_PATH = ROOT_DIR + "/data/libro_result"
TEST_FILE_DATA_PATH = ROOT_DIR + "/data/temp_data/test_file"

example_issue_title = "Stack trace and unfriendly error when an env file doesn't exist"
example_issue_description = f'''
Traceback (most recent call last):
  File "<string>", line 3, in <module>
  File "/Users/aanand/work/docker/fig/build/docker-compose/out00-PYZ.pyz/compose.cli.main", line 31, in main
  File "/Users/aanand/work/docker/fig/build/docker-compose/out00-PYZ.pyz/compose.cli.docopt_command", line 21, in sys_dispatch
  File "/Users/aanand/work/docker/fig/build/docker-compose/out00-PYZ.pyz/compose.cli.command", line 28, in dispatch
  File "/Users/aanand/work/docker/fig/build/docker-compose/out00-PYZ.pyz/compose.cli.docopt_command", line 24, in dispatch
  File "/Users/aanand/work/docker/fig/build/docker-compose/out00-PYZ.pyz/compose.cli.command", line 60, in perform_command
  File "/Users/aanand/work/docker/fig/build/docker-compose/out00-PYZ.pyz/compose.cli.main", line 445, in up
  File "/Users/aanand/work/docker/fig/build/docker-compose/out00-PYZ.pyz/compose.project", line 183, in up
  File "/Users/aanand/work/docker/fig/build/docker-compose/out00-PYZ.pyz/compose.service", line 262, in recreate_containers
  File "/Users/aanand/work/docker/fig/build/docker-compose/out00-PYZ.pyz/compose.service", line 293, in recreate_container
  File "/Users/aanand/work/docker/fig/build/docker-compose/out00-PYZ.pyz/compose.service", line 222, in create_container
  File "/Users/aanand/work/docker/fig/build/docker-compose/out00-PYZ.pyz/compose.service", line 448, in _get_container_create_options
  File "/Users/aanand/work/docker/fig/build/docker-compose/out00-PYZ.pyz/compose.service", line 628, in merge_environment
  File "/Users/aanand/work/docker/fig/build/docker-compose/out00-PYZ.pyz/compose.service", line 660, in env_vars_from_file
IOError: [Errno 2] No such file or directory: 'web.env'
'''

example_test = f'''
def test_env_nonexistent_file(self):
    self.assertRaises(ConfigError, lambda: Service('foo', env_file='tests/fixtures/env/nonexistent.env'))
'''

# 获得SWE-bench_Lite数据集中各个repo的data file
def get_repo_data(file_path):
    # 读取数据
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    return data
  
# 在Issue Report中抽取stack trace，并获得报错代码位置（function）
def extract_bug_context(d):
    repo = d['repo']
    commit_id = d['base_commit']
    issue = d['problem_statement']
    # print(issue)
    
    # 定义正则表达式模式，匹配报错堆栈信息中最后一行的完整信息
    pattern = r"File \"([^\"]+)\", line (\d+), in (\w+)"
    # 使用正则表达式查找所有匹配项
    matches = re.findall(pattern, issue)
    # 从后往前遍历匹配项，如果该匹配项所在文件在repo项目中存在，则返回
    # 最后一个匹配项的长度符合预期（即有3个元素）
    if matches:
        matches.reverse()
        for m in matches:
            if len(m) == 3:
                # 获取各个匹配项
                file_name, line_number, function_name = m
                all_python_files = get_repo_all_files(repo,commit_id)
                code_context = search_code(all_python_files,file_name,function_name)
                if code_context:
                    # print(repo)
                    # print('-'*80)
                    # print(issue)
                    # print('-'*80)
                    # print(f"File '{file_name}', line {line_number}, in {function_name}") 
                    # print('-'*80)
                    # print(code_context)
                    # print('='*120)
                    return code_context
            else:
                continue
    return None


# 抽取answer中的Python代码
def extract_python_code(answer):
    # 使用正则表达式提取Python代码部分,匹配 ```python ... ``` 的内容
    pattern = r"```python(.*?)```"  
    matches = re.search(pattern, answer, re.DOTALL)  # 使用 DOTALL 标志以匹配换行符
    if matches:
        extracted_code = matches.group(1).strip()  # 获取匹配的内容并去除首尾空格
        return extracted_code
    else:
        return ""

# 为一个Issue data构建prompt
def generate_prompt_with_context(issue_title,issue_description,context,example_issue_title,example_issue_description,example_test):
    # 创建包含 f-string 的多行字符串
    prompt = f'''
# {issue_title}
## Issue Description
{issue_description}
## Context 
{context}

## Example Issue Title
{example_issue_title}
## Example Issue Description 
{example_issue_description}
## Example Test
{example_test}

## Generate one test.
Provide a self-contained test case that reproduces this issue.
## Tips
1. The generated test case must be a class.
2. Please use the special code format for code snippet.
'''
    return prompt
    
    
# 为一个Issue data构建prompt
def generate_prompt_without_context(issue_title,issue_description,example_issue_title,example_issue_description,example_test):
    # 创建包含 f-string 的多行字符串
    prompt = f'''
# {issue_title}
## Issue Description
{issue_description}

## Example Issue Title
{example_issue_title}
## Example Issue Description 
{example_issue_description}
## Example Test
{example_test}

## Generate one test.
Provide a self-contained test case that reproduces this issue.
## Tips
1. The generated test case must be a class.
2. Please use the special code format for code snippet.
'''
    return prompt

def generate_prompt_original(issue_title,issue_description):
    prompt=f"""
# {issue_title}
## Description 
{issue_description}

## Reproduction
>Provide a self-contained test case that reproduces this issue.
```
## Tips
1. The generated test case must be a class.
2. Please use the special code format for code snippet.
    """
    return prompt
    
# 使用大模型为每一个issue生成测试用例
def generate_test(d):
    issue_title = d['problem_statement'].split('\n',1)[0]
    issue_description = d['problem_statement'].split('\n',1)[1]
    if "Traceback (most recent call last)" in issue_description:
        # 从issue_description中抽取stack trace，并获得报错代码（function）
        bug_context = extract_bug_context(d) 
        # 构建prompt
        prompt = generate_prompt_with_context(issue_title,issue_description,bug_context,example_issue_title,example_issue_description,example_test)
    else:
        prompt = generate_prompt_without_context(issue_title,issue_description,example_issue_title,example_issue_description,example_test)
    temp_answers = query_llm_5(prompt,"gpt-4")
    result = []
    for a in temp_answers:
        code_a = extract_python_code(a)
        result.append(code_a)
    return result
    
        
# 保存context字段
def store_context():
    data_file = "../../data/test_generation/stack_trace_data/generated_data_gpt.json"
    # 读取数据
    with open(data_file, 'r') as json_file:
        data = json.load(json_file)
    result = []
    for d in data: 
        if d['repo'] in ['django/django']:
            temp = d
            context = extract_bug_context(d)
            temp['code_context'] = context
            result.append(temp)
    store_file = "../../data/test_generation/stack_trace_data/django_cases_study.json"
    with open(store_file, 'w') as json_file:
        json.dump(result, json_file, indent=4)
    
def add_test_file(repo):
    repo_name = repo.split('/')[-1]
    libro_data_path = STORE_PATH + "/" + repo_name + "/generated_tests.json"
    test_file_data_path = TEST_FILE_DATA_PATH + "/" + repo_name + "/temp_test_file.json"
    libro_data = get_repo_data(libro_data_path)
    test_file_data = get_repo_data(test_file_data_path)
    result = []
    print(len(libro_data))
    print(len(test_file_data))
    if len(libro_data) == len(test_file_data):
        for i in range(len(libro_data)):
            temp = libro_data[i]
            temp['test_file'] = test_file_data[i]['test_file']
            result.append(temp)
        with open(libro_data_path, 'w') as json_file:
            json.dump(result, json_file, indent=4)



if __name__ == "__main__":
    repo = "pylint-dev/pylint"
    # 生成测试用例
    repo_name = repo.split('/')[-1]
    data_file = REPO_DATA_PATH + "/" + repo_name + "/data.json"
    data = get_repo_data(data_file)
    # print(len(data))
    result_path = STORE_PATH_NEW + "/" + repo_name + "/generated_tests.json"
    for d in tqdm(data):
        temp = d
        # 先读取结果，再一个一个保存，防止出错后数据丢失
        with open(result_path,'r') as f1:
            result = json.load(f1)

        generated_tests = generate_test(d)
        temp['generated_tests'] = generated_tests
        result.append(temp)
        with open(result_path, 'w') as json_file:
            json.dump(result, json_file, indent=4)

    # 添加检索到的test_file
    # add_test_file(repo)