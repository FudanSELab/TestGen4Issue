import json
from tqdm import tqdm
from utils import get_json_data,switch2commit,extract_bug_context,extract_python_code
from generate_prompt import generate_test_prompt_2,generate_test_prompt_3
from choose_example_tests import choose_function_by_emb
from query_gpt import query_llm_5

# 使用大模型为一个issue case生成测试用例
def generate_test(d,emb_result):
    repo = d['repo']
    commit_id = d['base_commit']
    issue_title = d['problem_statement'].split('\n',1)[0]
    issue_description = d['problem_statement'].split('\n',1)[1]
    # 从项目已有的test files中抽取imports和example tests
    imports,example_tests = choose_function_by_emb(d,emb_result)
    if "Traceback (most recent call last)" in issue_description:
        # 从issue_description中抽取stack trace，并获得报错代码（function）
        bug_context = extract_bug_context(repo,commit_id,issue_description)
        # 构建prompt
        prompt = generate_test_prompt_2(issue_title,issue_description,bug_context,imports,example_tests)
    else:
        prompt = generate_test_prompt_3(issue_title,issue_description,imports,example_tests)
    temp_answers = query_llm_5(prompt,"gpt-4")
    result = []
    for a in temp_answers:
        code_a = extract_python_code(a)
        result.append(code_a)
    return result
    
if __name__ == "__main__":
    data = get_json_data("/home/fdse/wy/RepoCodeEdit/data/SWE-bench_Lite/scikit-learn/data.json")
    emb_result = get_json_data("/home/fdse/wy/RepoCodeEdit/data/test_generation/temp_data/example_test/scikit-learn/example_test.json")
    store_file = "/home/fdse/wy/RepoCodeEdit/data/test_generation/result/scikit-learn/generated_test.json"
    for d in tqdm(data):
        with open(store_file,'r') as f1:
            result = json.load(f1)
        temp = {}
        temp['repo'] = d['repo']
        temp['instance_id'] = d['instance_id']
        temp['base_commit'] = d['base_commit']
        temp['FAIL_TO_PASS'] = d['FAIL_TO_PASS']
        temp['PASS_TO_PASS'] = d['PASS_TO_PASS']
        temp['generated_tests'] = generate_test(d,emb_result)
        result.append(temp)
        with open(store_file, 'w') as json_file:
            json.dump(result, json_file, indent=4)




    