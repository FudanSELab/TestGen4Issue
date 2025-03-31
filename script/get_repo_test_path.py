import os

# 获得sklearn项目文件夹下的所有测试文件夹路径
def get_sklearn_test_path(repo,repo_path):
    test_paths = []
    if repo
    for dirpath, dirnames, filenames in os.walk(repo_path):
        # Check if 'tests' is one of the directories
        if 'tests' in dirnames:
            # Add the full path to the list
            test_paths.append(os.path.join(dirpath, 'tests'))
    return test_paths

# 获得pytest项目文件夹下的所有测试文件夹路径
def get_pytest_test_path(repo_path):
    test_paths = []
    test_path = repo_path + "/testing"
    test_paths.append(test_path)
    return test_paths
    
    
if __name__ == "__main__":
    print(1)
    