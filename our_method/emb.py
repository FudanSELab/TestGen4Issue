# --coding: utf-8 --**
import openai
from openai import OpenAI
# from openai.embeddings_utils import cosine_similarity
import sys
sys.path.append('../..')
import pandas as pd
import json,time
# from transformers import CodeLlamaTokenizer
import datetime
import os
# from ..definitions import REPO_COMMIT_PATH
import numpy as np
from tqdm import tqdm
import requests
import subprocess
import ast
import contextlib
from utils import get_repo_path
from path import LOG_PATH,TEMP_TEST_FILE_PATH,TEMP_EXAM_TEST_PATH


openai.api_base = "https://openkey.cloud/v1"
openai_api_key = "sk-C11ltIBbPbJEVXuZD24f9f41C0B64cF9AaA61fC4E9516c30"
client = OpenAI(api_key=openai_api_key)
CONTEXT_SIZE = 13000
# tokenizer = CodeLlamaTokenizer.from_pretrained('/home/fdse/wy/RepoCodeEdit/data/7f22f0a5f7991355a2c3867923359ec4ed0b58bf')
# os.environ['http_proxy'] = "http://127.0.0.1:7890"
# os.environ['https_proxy'] = "https://127.0.0.1:7890"

log_dense_path = LOG_PATH + f"log_d_{datetime.date.today()}.txt"


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def get_embedding(content, model="text-embedding-3-small"):
    # os.environ["http_proxy"] = "http://127.0.0.1:7890"
    # os.environ["https_proxy"] = "http://127.0.0.1:7890"
    
    url = "https://openkey.cloud/v1/embeddings"
    proxies = {
        'http': 'http://127.0.0.1:7890',    # HTTP代理IP
        'https': 'https://127.0.0.1:7890'   # HTTPS代理IP
    }
    
    headers = {
        'Content-Type': 'application/json',
        # 填写OpenKEY生成的令牌/KEY，注意前面的 Bearer 要保留，并且和 KEY 中间有一个空格。
        'Authorization': 'Bearer sk-75SrDglyrTzvr8N6Df1f7b0eDc5e412aA6028bF1594272Ab'
    }
    data = {
        "model": model,
        "input": content
    }
    # try:
    response = requests.post(url, headers=headers, json=data)
    
    # 检查响应状态码是否为200（OK）
    if response.status_code == 200:
        # 尝试将响应解析为JSON
        try:
            response_json = response.json()
            return response.json()['data'][0]['embedding']
            # print(response_json)
        except requests.exceptions.JSONDecodeError:
            print("错误：无法将响应解析为JSON")
            print("原始响应内容:", response.text)
    else:
        print(f"错误：收到状态码 {response.status_code}")
        print("响应内容:", response.json())
    
    # except requests.exceptions.RequestException as e:
    #     print(f"请求失败：{e}")
    # except:
    #     return []
    #   print(response.json())
    # try:
    
    # except:
    #     return []

# 为issue计算相似度并排序后，输出排序前10的文件
def get_retrieved_files_fromdf(issue,df,k=10,weight=False):
    issue_embedding = get_embedding(issue)
    df['similarity'] = df.embedding.apply(lambda x:cosine_similarity(x,issue_embedding))
    res = df.sort_values('similarity',ascending=False).head(k)
    if not weight:
        result = [{"file_path":res.iloc[i]['file_path'],"code":res.iloc[i]['code']} for i in range(len(res))]
    else:
        result = [{"file_path":res.iloc[i]['file_path'],"code":res.iloc[i]['code'],"score":res.iloc[i]['similarity']} for i in range(len(res))]
    return result

def get_retrieved_content(query,code_list,k=10):
    query_embedding = get_embedding(query)
    # print(query_embedding)
    # for d in code_list:
    #     time.sleep(0.01)
    #     code_emb = get_embedding(d)
    #     print(code_emb)
    df = get_embedding_from_list(code_list)
    # print(df)
    df['similarity'] = df.embedding.apply(lambda x:cosine_similarity(x,query_embedding))
    
    # print("BEFORE SORTING:\n",df)
    temp_res = df.sort_values('similarity',ascending=False).head(k)
    # print("AFTER SORTING\n",temp_res)
    res = [temp_res.iloc[i]['content'] for i in range(len(temp_res))]
    return res


# 为整个仓库建立embedding向量库(从json文件)
def get_embedding_base(json_path):
    df = []
    with open(json_path,'r') as f:
        jsons = json.load(f)
        for js in jsons:
            pruned_code = js['simplified_code']   #SIMPLIFIED
            file_path = js['file_path']
            temp = {"code":pruned_code,"file_path":file_path,"similarity":"","embedding":get_embedding(pruned_code)}
            df.append(temp)
    return pd.DataFrame(df)

# 为某个list的元素创建embeddings
def get_embedding_from_list(_list):
    df = []
    for ele in _list:
        time.sleep(0.01)
        embedding = get_embedding(ele)
        if len(embedding) != 0:
            temp = {'content':ele,'embedding':embedding,'similarity':""}
            df.append(temp)
    return pd.DataFrame(df)

def get_function_and_class_names(repo_path,commit_id,file_path):
    """Given a file path, get all the function names and class names of the file."""
    if commit_id is not None and repo_path is not None:
        # subprocess.run(["sh","change_commit.sh",repo_path,commit_id])
        subprocess.run(['git','checkout',commit_id],cwd=repo_path)
    with open(file_path, 'r', encoding='utf-8') as file:
        source_code = file.read()
        # print('-'*80)
        # print(source_code)
        # print('-'*80)
        tree = ast.parse(source_code, filename=file_path)
    functions = []
    classes = []
    current_class=None
    for node in ast.walk(tree):  
        if isinstance(node, ast.ClassDef):
            current_class = node.name
            classes.append(node.name)
        elif isinstance(node, ast.FunctionDef):
            func_name = node.name
            params = [arg.arg for arg in node.args.args]
            function_body = ast.get_source_segment(source_code, node)
            if current_class and ('self' in params or 'cls' in params):
                # function_sig = f"{current_class}::{func_name}({','.join(params)})\n{function_body})"
                function_sig = function_body
            else:
                # function_sig = f"{func_name}({','.join(params)})\n{function_body})"
                function_sig = function_body
                # function_sig = function_body
            functions.append(function_sig)
        elif isinstance(node, ast.Module):
            current_class = None
    return (classes,functions)       

# 使用embedding接口，计算各个function与issue title的相似度，获得example tests
def retrieve_func_from_repo(repo_path,temp_test_file_path,temp_exam_test_path):
    with open(temp_test_file_path,'r') as f:
        print("LOADING JSON FILE...")
        jsons = json.load(f)
        for js in tqdm(jsons):
            # 一开始设置为空的列表[]，完成一个存储一个
            with open(temp_exam_test_path,'r') as f1:
                result = json.load(f1)
            # try:
            # repo = js['repo']
            commit_id = js['base_commit']
            issue_title = js['issue_title']
            test_file = js['test_file']
            if test_file:
                functions = get_function_and_class_names(repo_path,commit_id,test_file)[1]
                if functions:
                    retrieved_result = get_retrieved_content(issue_title,functions,k=10)
                    # print(retrieved_result)
                    js['searched_functions'] = retrieved_result
            else:
                js['searched_functions'] = []
            result.append(js)
            with open(temp_exam_test_path,'w') as f2:
                json.dump(result,f2,indent=4)
            # # except Exception as e:
            #     # print(e)
            #     # continue


if __name__ == "__main__":
    repo = "pydata/xarray"
    repo_path = get_repo_path(repo)
    temp_test_file_path = TEMP_TEST_FILE_PATH + "/" + repo.split('/')[-1] + "/temp_test_file.json"
    temp_exam_test_path = TEMP_EXAM_TEST_PATH + "/" + repo.split('/')[-1] + "/example_test.json"
    retrieve_func_from_repo(repo_path,temp_test_file_path,temp_exam_test_path)
    # query = 'Dog eats bones'
    # _list = ['Cat eats fish','Rabbit eats carrots']
    # print(get_retrieved_files(query,_list))
    