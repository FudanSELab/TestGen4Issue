import ast
from query_gpt import query_llm
from utils import get_repo_path,switch2commit,get_json_data,extract_imports_and_functions
from definitions import ROOT_DIR
# 构建prompt，让大模型挑选出最与issue相关的test function
def generate_prompt(issue_title,function_signatures):
    prompt = f'''
This is an issue title: "{issue_title}".
Below I will give you a list of test function signatures. Please select the three method signatures that can best assist you in generating test cases for the given issue.
Please note that the method signature you choose is not necessarily used to test the given issue, but it may provide you with some valuable information.
The answer format is: "['xxx','xxx','xxx']"
The function_signatures list is:
{function_signatures}
'''
    return prompt

# 方法1: 使用大模型在一个test file中选择3个最和issue相关的test function
def choose_function_by_llm(d,test_file):
    issue = d['problem_statement'].split('\n',1)
    issue_title = issue[0]
    imports, function_signatures, function_bodies = extract_imports_and_functions(test_file)
    prompt = generate_prompt(issue_title,function_signatures)
    # print(prompt)
    answer = query_llm(prompt)
    # 使用ast.literal_eval将字符串转换为列表
    answer_list = ast.literal_eval(answer)
    functions = []
    # 输出列表中的每个字符串
    for a in list(answer_list):
        # print(a)
        # print(function_bodies[a])
        functions.append(function_bodies[a])
    return imports,functions

# 方法2: 使用embedding计算方法，将issue title和每一个function body计算得分，取前3个fucntion body
def choose_function_by_emb(d,emb_result):
    repo = d['repo']
    commit_id = d['base_commit']
    repo_path = get_repo_path(repo)
    instance_id = d['instance_id']
    # 若前面的步骤已经切换了commit_id，可跳过
    switch2commit(repo_path,commit_id)
    for e in emb_result:
        if e['instance_id'] == instance_id:
            test_file = ROOT_DIR + "/data/raw_repo" + e['test_file'].split('swe_bench_temp_wy',1)[1]
            imports, function_signatures, function_bodies = extract_imports_and_functions(test_file)
            functions = e['searched_functions'][:3]
            return imports,functions
    return [],[]
    
if __name__ == "__main__":
    example = {
        "repo": "django/django",
        "instance_id": "django__django-15202",
        "base_commit": "4fd3044ca0135da903a70dfb66992293f529ecf1",
        "patch": "diff --git a/django/core/validators.py b/django/core/validators.py\n--- a/django/core/validators.py\n+++ b/django/core/validators.py\n@@ -108,15 +108,16 @@ def __call__(self, value):\n             raise ValidationError(self.message, code=self.code, params={'value': value})\n \n         # Then check full URL\n+        try:\n+            splitted_url = urlsplit(value)\n+        except ValueError:\n+            raise ValidationError(self.message, code=self.code, params={'value': value})\n         try:\n             super().__call__(value)\n         except ValidationError as e:\n             # Trivial case failed. Try for possible IDN domain\n             if value:\n-                try:\n-                    scheme, netloc, path, query, fragment = urlsplit(value)\n-                except ValueError:  # for example, \"Invalid IPv6 URL\"\n-                    raise ValidationError(self.message, code=self.code, params={'value': value})\n+                scheme, netloc, path, query, fragment = splitted_url\n                 try:\n                     netloc = punycode(netloc)  # IDN -> ACE\n                 except UnicodeError:  # invalid domain part\n@@ -127,7 +128,7 @@ def __call__(self, value):\n                 raise\n         else:\n             # Now verify IPv6 in the netloc part\n-            host_match = re.search(r'^\\[(.+)\\](?::\\d{1,5})?$', urlsplit(value).netloc)\n+            host_match = re.search(r'^\\[(.+)\\](?::\\d{1,5})?$', splitted_url.netloc)\n             if host_match:\n                 potential_ip = host_match[1]\n                 try:\n@@ -139,7 +140,7 @@ def __call__(self, value):\n         # section 3.1. It's defined to be 255 bytes or less, but this includes\n         # one byte for the length of the name and one byte for the trailing dot\n         # that's used to indicate absolute names in DNS.\n-        if len(urlsplit(value).hostname) > 253:\n+        if splitted_url.hostname is None or len(splitted_url.hostname) > 253:\n             raise ValidationError(self.message, code=self.code, params={'value': value})\n \n \n",
        "test_patch": "diff --git a/tests/forms_tests/field_tests/test_urlfield.py b/tests/forms_tests/field_tests/test_urlfield.py\n--- a/tests/forms_tests/field_tests/test_urlfield.py\n+++ b/tests/forms_tests/field_tests/test_urlfield.py\n@@ -100,6 +100,10 @@ def test_urlfield_clean_invalid(self):\n             # even on domains that don't fail the domain label length check in\n             # the regex.\n             'http://%s' % (\"X\" * 200,),\n+            # urlsplit() raises ValueError.\n+            '////]@N.AN',\n+            # Empty hostname.\n+            '#@A.bO',\n         ]\n         msg = \"'Enter a valid URL.'\"\n         for value in tests:\n",
        "problem_statement": "URLField throws ValueError instead of ValidationError on clean\nDescription\n\t\nforms.URLField( ).clean('////]@N.AN')\nresults in:\n\tValueError: Invalid IPv6 URL\n\tTraceback (most recent call last):\n\t File \"basic_fuzzer.py\", line 22, in TestOneInput\n\t File \"fuzzers.py\", line 350, in test_forms_URLField\n\t File \"django/forms/fields.py\", line 151, in clean\n\t File \"django/forms/fields.py\", line 136, in run_validators\n\t File \"django/core/validators.py\", line 130, in __call__\n\t File \"urllib/parse.py\", line 440, in urlsplit\n",
        "hints_text": "",
        "created_at": "2021-12-15T15:04:13Z",
        "version": "4.1",
        "FAIL_TO_PASS": "[\"test_urlfield_clean_invalid (forms_tests.field_tests.test_urlfield.URLFieldTest)\", \"test_urlfield_clean_not_required (forms_tests.field_tests.test_urlfield.URLFieldTest)\"]",
        "PASS_TO_PASS": "[\"test_urlfield_clean (forms_tests.field_tests.test_urlfield.URLFieldTest)\", \"test_urlfield_clean_required (forms_tests.field_tests.test_urlfield.URLFieldTest)\", \"test_urlfield_strip_on_none_value (forms_tests.field_tests.test_urlfield.URLFieldTest)\", \"test_urlfield_unable_to_set_strip_kwarg (forms_tests.field_tests.test_urlfield.URLFieldTest)\", \"test_urlfield_widget (forms_tests.field_tests.test_urlfield.URLFieldTest)\", \"test_urlfield_widget_max_min_length (forms_tests.field_tests.test_urlfield.URLFieldTest)\"]",
        "environment_setup_commit": "647480166bfe7532e8c471fef0146e3a17e6c0c9",
    }
    # choose_function_by_llm(example,test_file)
    emb_result = get_json_data(ROOT_DIR + "/data/test_generation/searched_result_61.json")
    imports,functions = choose_function_by_emb(example,emb_result)
    print(imports)
    print('-'*80)
    for f in functions:
        print(f)
        print('-'*80)
    