import json
import random

# 导入演化提示生成函数
from evol_for_code_template import constraints,less_common,reasoning,erroneous,time_space_complexity,oo,design_pattern

# 读取原始数据
with open('/home/baoxuanlin/graduation/WizardLM/Evol_Instruct/leetcode-train.jsonl', 'r') as fr:
    all_objs = [json.loads(line) for line in fr]

evol_records = []

# 定义演化提示生成函数列表及其对应的 base_instruction
evol_prompt_functions = [
    {
        "function": constraints,
    },
    {
        "function": less_common,
    },
    {
        "function": reasoning,
    },
    {
        "function" : erroneous,
    },
    {
        "function" : time_space_complexity,
    },
    # {
    #     "function" : oo,
    # },
    # {
    #     "function" : design_pattern,
    # }
]

# 处理每条原始数据
for cur_obj in all_objs:
    raw_index = cur_obj['id']
    instruction = cur_obj['content'].strip()
    
    # 随机选择两种演化提示函数
    selected_functions = random.sample(evol_prompt_functions, 2)
    
    # 为每种演化提示生成记录
    for func_info in selected_functions:
        func = func_info["function"]
        
        # 生成演化后的 Prompt
        evol_prompt = func(instruction)
        
        # 创建 JSON 记录
        record = {
            "custom_id": "leetcode"+str(raw_index),
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": "deepseek-r1",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant."
                    },
                    {
                        "role": "user",
                        "content": evol_prompt
                    }
                ],
            }
        }
        
        evol_records.append(record)

# 写入 JSONL 文件
with open('/home/baoxuanlin/graduation/WizardLM/Evol_Instruct/evol_prompts.jsonl', 'w') as f:
    for record in evol_records:
        f.write(json.dumps(record) + '\n')