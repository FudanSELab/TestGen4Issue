import os
import ast
import subprocess
from definitions import ROOT_DIR

# 获得某个repo克隆下来的repo_path
def get_repo_path(repo):
    repo_path = ROOT_DIR + "/data/raw_repo_lite/" + repo.split('/')[-1]
    return repo_path

# 切换某个仓库的状态到某个commit下
def switch2commit(repo_path,commit_id):
    subprocess.run(["sh","change_commit.sh",repo_path,commit_id])

# 获取一个路径下所有.py文件
def get_repo_files(repo_path):
    results = []
    items = os.listdir(repo_path)
    for item in items:
        item_path = os.path.join(repo_path,item)
        if os.path.isdir(item_path):
            results.extend(get_repo_files(item_path))
        else:
            if item_path.endswith('.py'):
                results.append(item_path)
    return results

# 获得一个仓库的所有.py文件
def get_repo_all_files(repo,commit_id):
    repo_path = get_repo_path(repo)
    switch2commit(repo_path,commit_id)
    all_python_files = get_repo_files(repo_path)
    return all_python_files

# 根据file_info在项目文件中搜索项目文件，匹配文件路径最后面的3个
def search_file(python_files,target_file_path):
    results = []
    for f in python_files:
        # 使用反斜杠 `\` 分割路径字符串
        f1 = f.split("/")
        if "\\" in target_file_path:
            f2 = target_file_path.split("\\")
        else:
            f2 = target_file_path.split("/")
        
        # 获取路径组件，排除空字符串
        last_three1 = [c for c in f1[-2:] if c]
        last_three2 = [c for c in f2[-2:] if c]
        if last_three1 == last_three2:
            results.append(f)
    if len(results) != 0:
        return results
    else:
        return None

# 获得某Python文件的内容
def get_python_file_code(file):
    with open(file,'r',encoding='utf-8') as py:
        try:
            code = py.read()
        except:
            return None
    return code

# 抽取一个Python文件里的某一function内容
def extract_function_content(file_content, function_name):
    # 将文件内容解析为抽象语法树（AST）
    tree = ast.parse(file_content)
    # 遍历 AST，寻找对应函数名的函数定义节点
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            # 找到目标函数，获取其起始和结束位置
            start_lineno = node.lineno
            end_lineno = node.end_lineno

            # 提取函数内容（从起始行到结束行）
            function_lines = file_content.splitlines()[start_lineno-1:end_lineno]
            function_content = '\n'.join(function_lines)
            return function_content
    # 如果未找到对应函数名的函数定义，则返回 None
    return None

# 根据function_name得到报错行所在的函数
def search_code(python_files,target_file_path,function_name):
    searched_file_path = search_file(python_files,target_file_path)
    if searched_file_path:
        for fp in searched_file_path:
            code = get_python_file_code(fp)
            function_body = extract_function_content(code,function_name)
            if function_body:
                return function_body
        return None
    else:
        return None

if __name__ == "__main__":
    repo = "scikit-learn/scikit-learn"
    commit_id = "fdbaa58acbead5a254f2e6d597dc1ab3b947f4c6"
    file_name = "/usr/local/lib/python3.5/dist-packages/sklearn/svm/base.py"
    line_number = "302"
    function_name = "_sparse_fit"
    all_python_files = get_repo_all_files(repo,commit_id)
    function_body = search_code(all_python_files,file_name,function_name)
    print(function_body)