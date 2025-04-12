import json

# 文件路径
prompts_file = '/home/baoxuanlin/graduation/WizardLM/Evol_Instruct/evol_prompts_from_seed_data.jsonl'
batch_result_file = '/home/baoxuanlin/graduation/WizardLM/Evol_Instruct/evol_instruct_batch_result.jsonl'
merged_file = '/home/baoxuanlin/graduation/WizardLM/Evol_Instruct/merged_batch_question_and_result_data.jsonl'

# 步骤1: 读取prompts_file并存储为字典
prompts_dict = {}
with open(prompts_file, 'r') as f:
    for line in f:
        data = json.loads(line)
        custom_id = data.get('custom_id')
        if custom_id:
            prompts_dict[custom_id] = data

# 步骤2: 读取batch_result_file并匹配
merged_data = []
with open(batch_result_file, 'r') as f:
    for line in f:
        data = json.loads(line)
        custom_id = data.get('custom_id')
        if custom_id in prompts_dict:
            # 合并数据，将batch_result的response添加到prompts数据中
            merged_entry = prompts_dict[custom_id].copy()
            merged_entry['response'] = data.get('response')
            merged_data.append(merged_entry)

# 步骤3: 写入新文件
with open(merged_file, 'w') as f:
    for entry in merged_data:
        f.write(json.dumps(entry) + '\n')