#!/usr/bin/env python3
import os

def merge_jsonl_files(input_files, output_file):
    with open(output_file, 'w', encoding='utf-8') as out_f:
        for file in input_files:
            if not os.path.exists(file):
                print(f"警告：文件 {file} 不存在。")
                continue
            with open(file, 'r', encoding='utf-8') as in_f:
                for line in in_f:
                    # 忽略空行
                    if line.strip():
                        out_f.write(line)
    print(f"合并完成，结果已写入 {output_file}")

if __name__ == '__main__':
    input_files = [
        "/home/baoxuanlin/graduation/magicoder/data/decontamination/data/merged_api_and_batch_fixed_instruction_response.jsonl",
        "/home/baoxuanlin/graduation/WizardLM/Evol_Instruct/data/intersection_instruction_response.jsonl"
    ]
    output_file = "/home/baoxuanlin/graduation/oss_evol_new_merged.jsonl"
    merge_jsonl_files(input_files, output_file)
