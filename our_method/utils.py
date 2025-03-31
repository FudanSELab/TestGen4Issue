import os
import re
import ast 
import json
import subprocess
from collections import Counter
from search_code import search_code
from path import REPO_PATH

# 切换某个仓库的状态到某个commit下
def switch2commit(repo_path,commit_id):
    subprocess.run(['git','checkout',commit_id],cwd=repo_path)
    # subprocess.run(["sh","change_commit.sh",repo_path,commit_id])

# 获得某个repo克隆下来的repo_path
def get_repo_path(repo):
    repo_path = REPO_PATH + "/" + repo.split('/')[-1]
    return repo_path

# 获得json文件的数据
def get_json_data(file_path):
    # 读取数据
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    return data

# 存储json文件的数据
def store_json_data(file_path,data):
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
 
# 获取路径下的所有.py文件的路径
def get_py_files(dir_path):
    results = []
    items = os.listdir(dir_path)
    for item in items:
        item_path = os.path.join(dir_path,item)
        if os.path.isdir(item_path):
            results.extend(get_py_files(item_path))
        else:
            if item_path.endswith('.py'):
                results.append(item_path)
    return results 
 
# 获得一个仓库的所有.py文件
def get_repo_all_files(repo,commit_id):
    repo_path = get_repo_path(repo)
    switch2commit(repo_path,commit_id)
    all_python_files = get_py_files(repo_path)
    return all_python_files
 
# 根据repo_name获得该repo的测试文件夹路径列表
def get_repo_test_paths(repo,repo_path):
    test_paths = []
    if repo in ["scikit-learn/scikit-learn","astropy/astropy","matplotlib/matplotlib","sympy/sympy","pydata/xarray"]:
        for dirpath, dirnames, filenames in os.walk(repo_path):
            # Check if 'tests' is one of the directories
            if 'tests' in dirnames:
                # Add the full path to the list
                test_paths.append(os.path.join(dirpath, 'tests'))
        return test_paths
    elif repo == "pytest-dev/pytest":
        test_path = repo_path + "/testing"
        test_paths.append(test_path)
        return test_paths
    elif repo in ['pallets/flask','django/django',"pylint-dev/pylint","mwaskom/seaborn","sphinx-doc/sphinx"]:
        test_path = repo_path + "/tests"
        test_paths.append(test_path)
        return test_paths
    elif repo in ["psf/requests"]:
        test_paths.append(repo_path)
        return test_paths

# 获得该repo在该commit_id下的所有测试文件，返回列表
def get_repo_test_files(repo,commit_id):
    repo_path = get_repo_path(repo)
    switch2commit(repo_path,commit_id)
    # 获得所有测试文件夹的路径
    test_paths = get_repo_test_paths(repo,repo_path)
    test_files = []
    for test_path in test_paths:
        test_files += get_py_files(test_path)
    return test_files

# 提取类名
def extract_class_names(node):
    class_names = []
    for item in node.body:
        if isinstance(item, ast.ClassDef):
            class_names.append(item.name)
    return class_names

# 从测试文件中抽取class name，并将其与路径拼接起来
def extract_classes_from_test_files(test_files):
    result = []
    for tf in test_files:
        with open(tf, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 解析代码成 AST
                    try:
                        tree = ast.parse(content)
                        classes = extract_class_names(tree)
                        for cls in classes:
                            temp_result = f"{tf[:-3]}:{cls}"
                            temp_result = temp_result.split('/')
                            temp_result = '/'.join(temp_result[-2:])
                            result.append(temp_result)
                    except:
                        continue
    return result

# 从llm的回答中抽取path
def extract_path(answer):
    # 定义正则表达式模式以匹配由斜杠和冒号组成，并且以单引号包围的路径
    pattern = r"'([^']+/[^']+:[^']+)'"
    # 搜索匹配模式的路径
    match = re.search(pattern, answer)
    if match:
        return match.group(1)  # 返回匹配的路径，不包括单引号
    else:
        return None

def extract_file_path(answer):
    # 抽取路径
    pattern = r"'([^']+)'"
    # 搜索匹配模式的路径
    # match = re.search(pattern, answer)
    matches = re.findall(pattern, answer)
    return matches
    # if match:
    #     return match.group(1)  # 返回匹配的路径，不包括单引号
    # else:
    #     return None
    
# 获得列表中出现次数最多的元素
def get_most_frequent_element(lst):
    if not lst:
        return None  # 如果列表为空，返回 None
    count = Counter(lst)
    most_common_element, _ = count.most_common(1)[0]  # 取出现次数最多的元素
    return most_common_element

# 获得列表中出现次数最多和第二多的元素
def find_top_two_elements(data_list):
    # 统计每个元素的出现次数
    counter = Counter(data_list)
    
    # 获取出现次数最多的两个元素
    most_common_elements = counter.most_common(2)
    
    # 提取元素和它们的出现次数
    if len(most_common_elements) < 2:
        # 如果列表中元素少于两个，则返回仅有的元素和None
        return most_common_elements[0][0], None
    else:
        return most_common_elements[0][0], most_common_elements[1][0]

# 抽取一个py文件里面的所有function，以字典存储，key是function name，value是function body
def extract_functions(file_path):
    # 读取文件内容
    with open(file_path, 'r') as file:
        file_content = file.read()
    tree = ast.parse(file_content)
    functions = {}
    # 遍历AST节点，找到所有的函数定义
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # 获取函数名
            func_name = node.name
            # 获取函数体的源码
            func_body = ast.get_source_segment(file_content, node)
            # 存储在字典中
            functions[func_name] = func_body
    return functions

# 抽取python文件中的imports信息和function信息
def extract_imports_and_functions(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        file_content = file.read()
    tree = ast.parse(file_content)
    imports = []
    function_signatures = []
    function_bodies = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            import_statement = "import " + ", ".join(alias.name if alias.asname is None else f"{alias.name} as {alias.asname}" for alias in node.names)
            imports.append(import_statement)
        elif isinstance(node, ast.ImportFrom):
            module = node.module if node.module else ""
            import_statement = f"from {module} import " + ", ".join(alias.name if alias.asname is None else f"{alias.name} as {alias.asname}" for alias in node.names)
            imports.append(import_statement)
        elif isinstance(node, ast.FunctionDef):
            func_name = node.name
            func_args = ", ".join(arg.arg for arg in node.args.args)
            func_signature = f"{func_name}({func_args})"
            func_body = ast.get_source_segment(file_content, node)
            function_signatures.append(func_signature)
            function_bodies[func_signature] = func_body
    return imports, function_signatures, function_bodies

# 抽取一段代码里调用的class、method、function，返回一个列表
def extract_called_names_from_code(code):
    # 解析代码生成AST
    tree = ast.parse(code)
    class_names = []
    method_names = []
    function_names = []
    # 访问节点的内部函数
    def visit_node(node):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                # 顶层函数调用
                function_names.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    # 类实例的方法调用
                    method_names.append(node.func.attr)
                elif isinstance(node.func.value, ast.Attribute):
                    # 类的方法调用
                    class_names.append(node.func.attr)
        for child in ast.iter_child_nodes(node):
            visit_node(child)
    # 开始访问根节点
    visit_node(tree)
    result = class_names + method_names + function_names
    return list(set(result))

# 根据<repo,commit_id>确定repo，再从Issue Report中抽取stack trace，并获得报错代码位置（function）
def extract_bug_context(repo,commit_id,issue):
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

# 抽取LLM answer中的Python代码
def extract_python_code(answer):
    # 使用正则表达式提取Python代码部分,匹配 ```python ... ``` 的内容
    pattern = r"```python(.*?)```"  
    matches = re.search(pattern, answer, re.DOTALL)  # 使用 DOTALL 标志以匹配换行符
    if matches:
        extracted_code = matches.group(1).strip()  # 获取匹配的内容并去除首尾空格
        return extracted_code
    else:
        return ""
    
# 获得test_file里面的imports_info
def get_imports_info(d):
    repo = d['repo']
    commit_id = d['base_commit']
    repo_path = get_repo_path(repo)
    test_file = d['test_file']
    # 若前面的步骤已经切换了commit_id，可跳过
    switch2commit(repo_path,commit_id)
    if test_file:
        imports, function_signatures, function_bodies = extract_imports_and_functions(test_file)
        return imports
    else:
        return []