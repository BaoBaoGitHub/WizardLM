import json

# 定义文件路径
input_file = "/home/baoxuanlin/graduation/WizardLM/Evol_Instruct/data/merged_batch_question_and_result_data.jsonl"
output_file = "/home/baoxuanlin/graduation/WizardLM/Evol_Instruct/data/merged_batch_question_and_result_data_remove_enomorous.jsonl"

# 要检查的字符串
target_string = "Provide a piece of erroneous code as a reference to increase misdirection"

# 打开输入文件和输出文件
with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", encoding="utf-8") as outfile:
    for line in infile:
        try:
            # 解析JSON行
            data = json.loads(line)
            # 安全访问body.messages[1].content
            content = data.get("body", {}).get("messages", [{}])[1].get("content", "")
            # 检查是否包含目标字符串
            if target_string not in content:
                # 如果不包含，写入新文件
                outfile.write(line)
        except json.JSONDecodeError:
            # 处理无效JSON行
            print(f"跳过无效JSON行: {line}")
        except IndexError:
            # 处理messages列表索引越界
            print(f"跳过messages不足的行: {line}")
        except Exception as e:
            # 处理其他异常
            print(f"处理行时出错: {line}\n错误: {e}")

print("处理完成，结果已写入到", output_file)