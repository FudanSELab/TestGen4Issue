import json

def case_study():
    data_file = "../../data/test_generation/stack_trace_data/django_cases_study.json"
    # 读取数据
    with open(data_file, 'r') as json_file:
        data = json.load(json_file)
    # print(data[0]['code_context'])
    for d in data:
        if d['instance_id'] == "django__django-13028":
            print(d['problem_statement'])

if __name__ == "__main__":
    case_study()