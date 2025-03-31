import json
from tqdm import tqdm
from utils import get_json_data,switch2commit,extract_bug_context,extract_python_code,get_imports_info
from generate_prompt import generate_test_prompt_2,generate_test_prompt_3
from query_gpt import query_llm_5
from definitions import ROOT_DIR
from path import TEMP_EXAM_TEST_PATH,RESULT_PATH,ABLATION_PATH

# 读取ramdom_data_id_list
def get_random_data_ids():
    file_name =ROOT_DIR + "/data/random_id_list.txt"
    with open(file_name, 'r') as file:
        lines = file.readlines()
    
    data_ids = [line.strip() for line in lines]
    return data_ids

def get_repos():
    file_name =ROOT_DIR + "/data/repo_names.txt"
    with open(file_name, 'r') as file:
        lines = file.readlines()
    
    repo_names = [line.strip() for line in lines]
    return repo_names

# 使用大模型为一个issue case生成测试用例
def generate_test(d):
    repo = d['repo']
    commit_id = d['base_commit']
    issue_title = d['problem_statement'].split('\n',1)[0]
    issue_description = d['problem_statement'].split('\n',1)[1]
    example_tests = d['searched_functions'][:3]
    # 从test_file中抽取imports_info
    imports_info = get_imports_info(d)
    # print(imports_info)
    if "Traceback (most recent call last)" in issue_description:
        # 从issue_description中抽取stack trace，并获得报错代码（function）
        bug_context = extract_bug_context(repo,commit_id,issue_description)
        # 构建prompt
        prompt = generate_test_prompt_2(issue_title,issue_description,bug_context,imports_info,example_tests)
    else:
        prompt = generate_test_prompt_3(issue_title,issue_description,imports_info,example_tests)
    temp_answers = query_llm_5(prompt,"gpt-4")
    result = []
    for a in temp_answers:
        code_a = extract_python_code(a)
        result.append(code_a)
    return imports_info,result
    
# 消融实验
# 使用大模型为一个issue case生成测试用例
def generate_test_ablation(d):
    repo = d['repo']
    commit_id = d['base_commit']
    issue_title = d['problem_statement'].split('\n',1)[0]
    issue_description = d['problem_statement'].split('\n',1)[1]
    example_tests = d['searched_functions'][:3]
    # 从test_file中抽取imports_info
    imports_info = get_imports_info(d)

    # if "Traceback (most recent call last)" in issue_description:
    #     # 从issue_description中抽取stack trace，并获得报错代码（function）
    #     bug_context = extract_bug_context(repo,commit_id,issue_description)
    #     # 构建prompt
    #     prompt = generate_test_prompt_2(issue_title,issue_description,bug_context,imports_info,example_tests)
    # else:
    prompt = generate_test_prompt_3(issue_title,issue_description,imports_info,example_tests)
    temp_answers = query_llm_5(prompt,"gpt-4")
    result = []
    for a in temp_answers:
        code_a = extract_python_code(a)
        result.append(code_a)
    return imports_info,result

if __name__ == "__main__":
    repo_names = get_repos()
    repo = "pydata/xarray"
    temp_exam_test_path = TEMP_EXAM_TEST_PATH + "/" + repo.split('/')[-1] + "/example_test.json"
    exam_test_data = get_json_data(temp_exam_test_path)
    result_path = ABLATION_PATH + "/no_bug_context/" + repo.split('/')[-1] + "/generated_tests.json"
    random_ids = get_random_data_ids()
    for d in tqdm(exam_test_data):
        if d['instance_id'] in random_ids:
            temp = d
            # 先读取结果，再一个一个保存，防止出错后数据丢失
            with open(result_path,'r') as f1:
                result = json.load(f1)

            imports_info,generated_tests = generate_test_ablation(d)
            temp['imports_info'] = imports_info
            temp['generated_tests'] = generated_tests
            result.append(temp)
            with open(result_path, 'w') as json_file:
                json.dump(result, json_file, indent=4)

    # xxx = 0
    # for repo in repo_names:
    #     result_path = ABLATION_PATH + "/no_bug_context/" + repo.split('/')[-1] + "/generated_tests.json"
    #     data = get_json_data(result_path)
    #     xxx += len(data)
    # print(xxx)

