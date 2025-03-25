import os
from openai import OpenAI

client = OpenAI(
    # If the environment variable is not configured, replace the following line with: api_key="sk-xxx",
    api_key="your api key", 
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
)
completion = client.chat.completions.create(
    model="qwen-plus", # Here qwen-plus is used as an example. You can change the model name as needed. Model list: https://www.alibabacloud.com/help/en/model-studio/getting-started/models
    messages=[
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': 'what is today top news?'}],
    )
    
print(completion.model_dump_json())