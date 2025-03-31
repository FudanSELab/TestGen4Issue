import openai
openai.api_base = "https://openkey.cloud/v1"
openai.api_key = 'sk-75SrDglyrTzvr8N6Df1f7b0eDc5e412aA6028bF1594272Ab'

# 对话LLM
def query_llm(prompt,model_name):
    completion = openai.ChatCompletion.create(
        model=model_name,
        messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
        ],
        n=1,
        temperature=0.1
    )
    # print(completion.choices[0].message['content'])
    return completion.choices[0].message['content']
    # answers = []
    # for i in range(5):
    #     answers.append(completion.choices[i].message['content'])
    # return answers
    # print(completion.choices)
    # print(type(completion.choices))
    
    # print(completion.choices[0].message['content'])
    # print(type(completion.choices[0].message['content']))

# 生成5个测试用例
def query_llm_5(prompt,model_name):
    completion = openai.ChatCompletion.create(
        model=model_name,
        messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
        ],
        n=5,
        temperature=0.1
    )
    answers = []
    for i in range(5):
        answers.append(completion.choices[i].message['content'])
    return answers

if __name__ == "__main__":
    query_llm("Hello!","gpt-3.5-turbo")