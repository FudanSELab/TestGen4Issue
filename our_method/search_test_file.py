from utils import get_repo_test_files,extract_file_path,get_json_data,get_most_frequent_element
from query_gpt import query_llm
from generate_prompt import search_test_file_prompt, search_test_file_prompt_final
import json
from path import REPO_DATA_PATH,TEMP_TEST_FILE_PATH
    
# 按照每500个path进行切割
def chunk_path_list(class_paths,size):
    # 使用列表推导式和切片操作将列表切割为多个小列表
    return [class_paths[i:i + size] for i in range(0, len(class_paths), size)]
    
# 检索与该data相关的test file
def search_test_file(data):
    repo = data['repo']
    commit_id = data['base_commit']
    issue_title = data['problem_statement'].split('\n',1)[0]
    test_files = get_repo_test_files(repo,commit_id)
    simple_test_files = []
    for tf in test_files:
        temp_tf = tf.split('/')
        temp_tf = '/'.join(temp_tf[-3:])
        # if temp_tf == "test_apps/subdomaintestmodule/__init__.py":
        #     print('-'*80)
        #     print(tf)
        #     print('-'*80)
        simple_test_files.append(temp_tf)
    chunked_path_list = chunk_path_list(simple_test_files,300)
    temp_result = []
    for path_list in chunked_path_list:
        prompt = search_test_file_prompt(issue_title,path_list)
        temp_answer = query_llm(prompt,"gpt-3.5-turbo")
        temp_result += extract_file_path(temp_answer)
    prompt = search_test_file_prompt_final(issue_title,temp_result)
    results = []
    for i in range(5):
        answer = query_llm(prompt,"gpt-3.5-turbo")
        results += extract_file_path(answer)
    # print(results)
    final_result = get_most_frequent_element(results)
    return final_result

    
# 补全完整test_file的路径
def complete_file_path(repo,commit_id,simple_test_file):
    test_files = get_repo_test_files(repo,commit_id)
    for tf in test_files:
        temp_tf = tf.split('/')
        temp_tf = '/'.join(temp_tf[-3:])
        if temp_tf == simple_test_file:
            return tf
    return ""
    
# 生成包含LLM检索出来的test_file的临时数据，为进一步抽取example test
def generate_temp_data(repo,data):
    result = []
    for d in data:
        temp = d
        temp['issue_title'] = d['problem_statement'].split('\n',1)[0]
        print( d['instance_id'])
        simple_test_file = search_test_file(d)
        complete_test_file = complete_file_path(d['repo'],d['base_commit'],simple_test_file)
        temp['test_file'] = complete_test_file
        print(d['FAIL_TO_PASS'])
        print(simple_test_file)
        print('-'*80)
        result.append(temp)
    temp_test_file_path = TEMP_TEST_FILE_PATH + "/" + repo.split('/')[-1] + "/temp_test_file.json"
    with open(temp_test_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(result, json_file, ensure_ascii=False, indent=4)
        
if __name__ == "__main__":
    repo = "django/django"
    repo_data_path = REPO_DATA_PATH + "/" + repo.split('/')[-1] + "/data.json"
    data = get_json_data(repo_data_path)
    # print(len(data))
    generate_temp_data(repo,data)


    
    # for d in data:
    #     pass_to_pass = ast.literal_eval(d['PASS_TO_PASS'])
    #     for ptp in pass_to_pass:
    #         print(ptp)
    #     print('-'*80)
        