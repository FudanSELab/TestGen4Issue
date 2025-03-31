import json

# Prompt1
# 根据Issue生成生成一个temp test，用于检索repo中相似的example test
# input: issue_title,issue_description,context
# output: test case
def generate_test_prompt_1(issue_title,issue_description,context):
    # 创建包含 f-string 的多行字符串
    prompt = f'''
# {issue_title}
## Issue Description
{issue_description}
## Context 
{context}

## Generate one test.
You are an expert in software testing, you are really good at writing test cases and test functions given a requirement. 
Now I will offer you some issues with "Tracebacks" from github as well as the code context the issue relates to.
Please summarize and understand the main content of the issue based on the issue title and description, analyze the reasons for the issue and how to test it, and finally write one test case to test whether the bug has been fixed.
## Tips
1. You should generate test case based on the given issue_tittle, issue_description and context. 
2. When necessery, you can import some libraries or apis.
3. The generated test case must be a class.
4. Please use the special code format for code snippet.
5. If you call some APIs, please pay attention to the data type of the parameters.
'''
    return prompt

# Prompt2
# input: issue_title,issue_description,context,imports_list,example_tests
# output: test case
def generate_test_prompt_2(issue_title,issue_description,context,imports_list,example_tests):
    # 创建包含 f-string 的多行字符串
    prompt = f'''
# {issue_title}
## Issue Description
{issue_description}

## Context 
{context}

## Example Tests
{example_tests}

## Imports List
{imports_list}

## Introduction of a Test Case
A test function can be thought of as containing three parts: 
The first part is the preconditions that the test case must meet. For a certain test case, you must first build the preconditions it needs to use. For example, you must create an object of a certain class and set some properties on it. Otherwise, subsequent tests will not be able to proceed or the expected results will be obtained. 
The second part is the steps required to execute the current test case, which usually includes necessary assignments, a series of API calls, etc. The lines of code that exist in steps that can trigger bugs are called critical lines of code. 
The third part is the expected execution result of the test case, usually corresponding to the assert statement

## Generate one test.
You are an expert in software testing, you are really good at writing test cases and test functions given a requirement. 
Now I will offer you an issue with "Tracebacks" from Github as well as the code context the issue relates to.
Please summarize and understand the main content of the issue based on the issue title and description, analyze the reasons for the issue, the expected normal performance of the issue and how to test it, and finally write one test case to test whether the bug has been fixed.

## Tips
1. You should generate test case based on the given issue_tittle, issue_description and context.
2. The given ##Example Tests are test cases that may be related to the issue. You can refer to it. 
3. When necessery, you can import some libraries or apis from ## Imports List.
4. The generated test case must be a class.
5. Please use the special code format for code snippet.
6. If you call some APIs, please pay attention to the data type of the parameters.
'''
    return prompt

# Prompt3
# input: issue_title,issue_description,imports_list,example_tests
# output: test case
def generate_test_prompt_3(issue_title,issue_description,imports_list,example_tests):
    # 创建包含 f-string 的多行字符串
    prompt = f'''
# {issue_title}
## Issue Description
{issue_description}

## Example Tests
{example_tests}

## Imports List
{imports_list}

## Introduction of a Test Case
A test function can be thought of as containing three parts: 
The first part is the preconditions that the test case must meet. For a certain test case, you must first build the preconditions it needs to use. For example, you must create an object of a certain class and set some properties on it. Otherwise, subsequent tests will not be able to proceed or the expected results will be obtained. 
The second part is the steps required to execute the current test case, which usually includes necessary assignments, a series of API calls, etc. The lines of code that exist in steps that can trigger bugs are called critical lines of code. 
The third part is the expected execution result of the test case, usually corresponding to the assert statement

## Generate one test.
You are an expert in software testing, you are really good at writing test cases and test functions given a requirement. 
Now I will offer you an issue from Github.
Please summarize and understand the main content of the issue based on the issue title and description, analyze the reasons for the issue, the expected normal performance of the issue and how to test it, and finally write one test case to test whether the bug has been fixed.

## Tips
1. You should generate test case based on the given issue_tittle and issue_description.
2. The given ##Example Tests are test cases that may be related to the issue. You can refer to it. 
3. When necessery, you can import some libraries or apis from ## Imports List.
4. The generated test case must be a class.
5. Please use the special code format for code snippet.
6. If you call some APIs, please pay attention to the data type of the parameters.
'''
    return prompt


# 构建prompt，让大模型检索出最相关的一个test_file
def search_test_file_prompt(issue_title,file_paths):
    # 创建包含 f-string 的多行字符串
    prompt = f'''
This is an issue title: "{issue_title}".
Below I will give you a list of test files in the project path, please find out only one path most likely to test this issue. 
Please note that what you need to find is the test file that tests the issue, not the most relevant file for the issue.
The answer format is: "Most likely related path is : 'xxx/xxx/xxx.py'"
The list is:
{file_paths}
'''
    return prompt

# 构建prompt，让大模型检索出最相关的2个test_file
def search_test_file_prompt_final(issue_title,file_paths):
    # 创建包含 f-string 的多行字符串
    prompt = f'''
This is an issue title: "{issue_title}".
Below I will give you a list of test files in the project path, please find out only two path most likely to test this issue. 
Please note that what you need to find is the test file that tests the issue, not the most relevant file for the issue.
The answer format is: "Most likely related path is : 'xxx/xxx/xxx.py','xxx/xxx/xxx.py'"
The list is:
{file_paths}
'''
    return prompt

if __name__ == "__main__":
    print("Fighting!")
    