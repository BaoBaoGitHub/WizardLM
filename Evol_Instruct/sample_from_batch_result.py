import json

# 输入和输出文件路径
input_file = '/home/baoxuanlin/graduation/WizardLM/Evol_Instruct/merged_batch_question_and_result_data.jsonl'
output_file = '/home/baoxuanlin/graduation/WizardLM/Evol_Instruct/sampled_content_data.jsonl'

# 读取JSONL文件并提取content数据
content_data = []
with open(input_file, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        content = data.get('response', {}).get('body', {}).get('choices', [{}])[0].get('message', {}).get('content', '')
        if content:
            content_data.append({'content': content})

# 将content数据保存到新的JSONL文件
with open(output_file, 'w', encoding='utf-8') as f:
    for item in content_data:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

print(f"成功从 {input_file} 中提取content数据，并保存到 {output_file}")