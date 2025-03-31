import json
from openai import OpenAI
from tqdm import tqdm
from utils import get_json_data,switch2commit,extract_bug_context,extract_python_code,get_imports_info
from generate_prompt import generate_test_prompt_2,generate_test_prompt_3
from path import TEMP_EXAM_TEST_PATH,RESULT_PATH

client = OpenAI(api_key="sk-55cab67284374205bbe3f622b51e79e1", base_url="https://api.deepseek.com")

# 调用deepseek接口
def query_deepseek(prompt):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a software test engineer"},
            {"role": "user", "content": prompt},
        ],
        stream=False
    )
    return response.choices[0].message.content

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
        # 构建prompt
        prompt = generate_test_prompt_3(issue_title,issue_description,imports_info,example_tests)

    result = []
    for i in range(5):
        temp_answer = query_deepseek(prompt)
        code_a = extract_python_code(temp_answer)
        result.append(code_a)
    return imports_info,result
    
if __name__ == "__main__":
    repo = "pallets/flask"
    temp_exam_test_path = TEMP_EXAM_TEST_PATH + "/" + repo.split('/')[-1] + "/example_test.json"
    exam_test_data = get_json_data(temp_exam_test_path)
    result_path = RESULT_PATH + "/" + repo.split('/')[-1] + "/generated_tests.json"

    data_num = len(exam_test_data)
    # for d in tqdm(exam_test_data):
    for i in tqdm(range(data_num)):
        d = exam_test_data[i]
        temp = d
        # 先读取结果，再一个一个保存，防止出错后数据丢失
        with open(result_path,'r') as f1:
            result = json.load(f1)

        imports_info,generated_tests = generate_test(d)
        temp['imports_info'] = imports_info
        temp['generated_tests'] = generated_tests
        result.append(temp)
        with open(result_path, 'w') as json_file:
            json.dump(result, json_file, indent=4)

    # print(query_deepseek('hello'))

    # xxx = 0
    # for repo in repo_names:
    #     result_path = ABLATION_PATH + "/no_bug_context/" + repo.split('/')[-1] + "/generated_tests.json"
    #     data = get_json_data(result_path)
    #     xxx += len(data)
    # print(xxx)

