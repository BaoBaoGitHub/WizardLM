import json

# 定义文件路径
file1 = '/home/baoxuanlin/graduation/WizardLM/Evol_Instruct/data/extracted_batch_question_and_result_data_remove_enomorous_compatible.jsonl'
file2 = '/home/baoxuanlin/graduation/WizardLM/Evol_Instruct/data/extracted_questions_and_answers_compatible.jsonl'
output_file = '/home/baoxuanlin/graduation/WizardLM/Evol_Instruct/data/intersection.jsonl'

# 第一步：读取第一个文件，构建"instruction"集合
instructions_set = set()
with open(file1, 'r', encoding='utf-8') as f1:
    for line in f1:
        try:
            json_obj = json.loads(line.strip())
            instruction = json_obj.get('instruction')
            if instruction is not None and instruction.strip():  # 确保不为空
                instructions_set.add(instruction.strip())  # 去重并去除空白符
        except json.JSONDecodeError:
            print(f"警告：在 {file1} 中发现无效的JSON行")

# 第二步：读取第二个文件，求交集并写入输出
written_instructions = set()  # 记录已写入的"instruction"
with open(file2, 'r', encoding='utf-8') as f2, open(output_file, 'w', encoding='utf-8') as out_f:
    for line in f2:
        try:
            json_obj = json.loads(line.strip())
            instruction = json_obj.get('instruction')
            if instruction is not None and instruction.strip() in instructions_set:
                if instruction.strip() not in written_instructions:  # 确保不重复写入
                    out_f.write(line)
                    written_instructions.add(instruction.strip())
        except json.JSONDecodeError:
            print(f"警告：在 {file2} 中发现无效的JSON行")

print(f"交集已写入 {output_file}，行数应不超过 {len(instructions_set)}")