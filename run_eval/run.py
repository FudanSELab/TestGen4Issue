from swebench import setup_testbed
import swebench.harness.constants as constants
from swebench.harness.context_manager import TaskEnvContextManager, TestbedContextManager
from swebench.harness.utils import get_instances, split_instances, DotDict
from swebench.harness.constants import PatchType
import json
import os
import subprocess
from definitions import ROOT_DIR

log_suffix = "20240623"
model_name = "gpt4"
SKIP_INSTANCES = {"pytest-dev/pytest": ["6387", "7956", "3805"]}
# os.environ['http_proxy'] = "http://127.0.0.1:7890"
# os.environ['https_proxy'] = "https://127.0.0.1:7890"

def verify_task_instances(data: dict):
    """
    Sets up task environment context manager. Each task instance is then
    installed and validated within the context manager.

    Args:
        data: Dict containing task instances and other data
            task_instances: List of task instances
            + setup_testbed args
    """
    data_dict = DotDict(data)
    for task_instance in data_dict.task_instances:
        with TaskEnvContextManager(
            task_instance,
            data_dict.testbed,
            data_dict.venv,
            data_dict.log_dir,
            data_dict.conda_path,
            verbose=data_dict.verbose,
            timeout=data_dict.timeout,
            log_suffix=data_dict.log_suffix,
        ) as tcm:
            if (
                task_instance["repo"] in SKIP_INSTANCES
                and task_instance["pull_number"]
                in SKIP_INSTANCES[task_instance["repo"]]
            ):
                continue
            if (
                not tcm.reset_task_env(task_instance)
                or not tcm.run_install_task(task_instance)
                
                or not tcm.apply_patch(task_instance["test_patch"], patch_type=PatchType.PATCH_TEST.value)
                or not tcm.run_tests_task(task_instance)
                or not tcm.apply_patch(task_instance["patch"], patch_type=PatchType.PATCH_GOLD.value)
                or not tcm.run_tests_task(task_instance)
            ):
                continue

def post_process(instance_info_dict:dict):
    """
    instance_info_dict包含下面的keys：
        conda_path: self.path_conda---------conda的路径
        log_dir: self.log_dir-----------log文件夹
        task_instances: instances-------------instance的信息，是一个列表
        testbed: os.path.join(self.testbed, env_name)--------------testbed的信息，由testbed路径和env_name拼合而成
        timeout: self.timeout----------------subprocess超时时间
        venv: env_name----------------conda环境名
        version: version----------------instance中的version信息
        verbose: self.verbose
    """
    task_instance = instance_info_dict['task_instances'][0]
    task_instance["model_name_or_path"] = model_name
    
    patch_type = "pred" # 或者gold等
    patch = "diff --git a/django/core/validators.py b/django/core/validators.py\n--- a/django/core/validators.py\n+++ b/django/core/validators.py\n@@ -108,15 +108,16 @@ def __call__(self, value):\n             raise ValidationError(self.message, code=self.code, params={'value': value})\n \n         # Then check full URL\n+        try:\n+            splitted_url = urlsplit(value)\n+        except ValueError:\n+            raise ValidationError(self.message, code=self.code, params={'value': value})\n         try:\n             super().__call__(value)\n         except ValidationError as e:\n             # Trivial case failed. Try for possible IDN domain\n             if value:\n-                try:\n-                    scheme, netloc, path, query, fragment = urlsplit(value)\n-                except ValueError:  # for example, \"Invalid IPv6 URL\"\n-                    raise ValidationError(self.message, code=self.code, params={'value': value})\n+                scheme, netloc, path, query, fragment = splitted_url\n                 try:\n                     netloc = punycode(netloc)  # IDN -> ACE\n                 except UnicodeError:  # invalid domain part\n@@ -127,7 +128,7 @@ def __call__(self, value):\n                 raise\n         else:\n             # Now verify IPv6 in the netloc part\n-            host_match = re.search(r'^\\[(.+)\\](?::\\d{1,5})?$', urlsplit(value).netloc)\n+            host_match = re.search(r'^\\[(.+)\\](?::\\d{1,5})?$', splitted_url.netloc)\n             if host_match:\n                 potential_ip = host_match[1]\n                 try:\n@@ -139,7 +140,7 @@ def __call__(self, value):\n         # section 3.1. It's defined to be 255 bytes or less, but this includes\n         # one byte for the length of the name and one byte for the trailing dot\n         # that's used to indicate absolute names in DNS.\n-        if len(urlsplit(value).hostname) > 253:\n+        if splitted_url.hostname is None or len(splitted_url.hostname) > 253:\n             raise ValidationError(self.message, code=self.code, params={'value': value})\n \n \n"  # 这里放上patch：str
    
    with TaskEnvContextManager(
        task_instance,
        instance_info_dict["testbed"],
        instance_info_dict["venv"],
        instance_info_dict["log_dir"],
        instance_info_dict["conda_path"],
        verbose=instance_info_dict["verbose"],
        timeout=instance_info_dict["timeout"],
        is_eval=True,
        log_suffix=log_suffix,
    ) as tcm:
        reset_result:bool = tcm.reset_task_env(task_instance)
        repo_path = os.path.join(instance_info_dict["testbed"])
        print('*'*50)
        print(repo_path)
        print('*'*50)
        a = subprocess.run(['git','status'],capture_output=True,cwd=repo_path)
        print(a.stdout)
        
        # 在环境中应用patch
        apply_result:bool = tcm.apply_patch(patch,patch_type)
        # 运行测试用例
        test_result:bool = tcm.run_tests_task(task_instance)
        # 重置环境
        reset_result:bool = tcm.reset_task_env(task_instance)
        a = subprocess.run(['git','status'],capture_output=True,cwd=repo_path)
        print(a.stdout)
    

if __name__ == "__main__":
    log_dir = "./log"
    test_bed = "./test_bed"
    temp_dir = "./temp"
    instances = {}
    with open(ROOT_DIR + '/data/our_method_result/scikit-learn/generated_test.json','r') as f:
        js = json.load(f)[0]
        # 包含多个instance
        instances['task_instances'] = [js]
        instances['test_bed'] = test_bed
        instances['log_dir'] = log_dir
        instances['verbose'] = True
        instances['temp_dir'] = temp_dir
        instances['timeout'] = 1800
        instances['func'] = verify_task_instances
        setup_testbed(instances)
        
        