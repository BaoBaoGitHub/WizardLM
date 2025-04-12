import argparse
import pprint
import sys
import os
import re
from tqdm import tqdm
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
from human_eval.data import write_jsonl, read_problems, stream_jsonl

if torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"

try:
    if torch.backends.mps.is_available():
        device = "mps"
except:
    pass

def generate_prompt(input):
    INSTRUCTION = f"""Below is an instruction that describes a task. Write a response that appropriately completes the request.


### Instruction:
Create a Java code for this problem:
{input}

### Response:"""
    return INSTRUCTION

def get_model(
    load_8bit: bool = False,
    base_model: str = "bigcode/starcoder",
):
    # 断言 base_model 必须被指定
    assert base_model, (
        "Please specify a --base_model, e.g. --base_model='bigcode/starcoder'"
    )

    # 加载预训练的 tokenizer
    tokenizer = AutoTokenizer.from_pretrained(base_model)

    # 根据 device 类型加载模型
    if device == "cuda":
        # 加载 8bit 模型或 16bit 浮点数模型到 CUDA 设备
        model = AutoModelForCausalLM.from_pretrained(
            base_model,
            load_in_8bit=load_8bit,
            torch_dtype=torch.float16,
            device_map="auto",
        )
    elif device == "mps":
        # 加载 16bit bfloat 类型模型到 MPS 设备
        model = AutoModelForCausalLM.from_pretrained(
            base_model,
            device_map={"": device},
            torch_dtype=torch.bfloat16,
        )

    # 设置模型的 pad token id
    model.config.pad_token_id = tokenizer.pad_token_id

    # 如果不是加载 8bit 模型，则将模型转换为半精度浮点数
    if not load_8bit:
        model.half()  # 似乎可以解决某些用户的问题。

    # 将模型设置为评估模式
    model.eval()

    # 如果 torch 版本大于等于 2 且不在 Windows 平台上，则使用 torch.compile 编译模型
    if torch.__version__ >= "2" and sys.platform != "win32":
        model = torch.compile(model)
    
    return tokenizer, model


def main():
    # 创建参数解析器
    parser = argparse.ArgumentParser()

    # 添加命令行参数
    parser.add_argument('--model', type=str, default='bigcode/starcoder', help="指定模型名称")
    parser.add_argument('--output_path', type=str, help="指定输出路径")
    parser.add_argument('--start_index', type=int, default=0, help="指定起始索引")
    parser.add_argument('--end_index', type=int, default=164, help="指定结束索引")
    parser.add_argument('--temperature', type=float, default=0.8, help="指定温度参数")
    parser.add_argument('--N', type=int, default=200, help="指定生成序列的数量")
    parser.add_argument('--max_len', type=int, default=512, help="指定最大序列长度")
    parser.add_argument('--decoding_style', type=str, default='sampling', help="指定解码风格")
    parser.add_argument('--num_seqs_per_iter', type=int, default=50, help="指定每次迭代生成的序列数量")
    parser.add_argument('--greedy_decode', action='store_true', help="指定是否使用贪心解码")
    parser.add_argument('--overwrite', action='store_true', help="指定是否覆盖已存在的输出文件")

    # 解析命令行参数
    args = parser.parse_args()

    # 将命令行参数转换为字典
    argsdict = vars(args)
    print(pprint.pformat(argsdict))

    # 读取问题
    problems = read_problems()

    # 获取任务ID列表
    task_ids = sorted(problems.keys())[args.start_index: args.end_index]
    prompts = [problems[task_id]['prompt'] for task_id in task_ids]
    num_samples = len(prompts)
    print("样本数量: {}".format(num_samples))

    # 获取分词器和模型
    tokenizer, model = get_model(base_model=args.model)

    # 配置生成参数
    generation_config = GenerationConfig(
        pad_token_id=tokenizer.pad_token_id,
        do_sample=False if args.greedy_decode else True,
        temperature=args.temperature,
        max_length=args.max_len,
        num_return_sequences=args.num_seqs_per_iter,
        eos_token_id=tokenizer.eos_token_id,
        top_p=0.95
    )

    print(f"已加载 {args.model}。")

    # 生成输出
    for i in tqdm(range(num_samples), ncols=0, total=num_samples):
        output_file = args.output_path + '/{}.jsonl'.format(args.start_index + i)

        # 如果文件已存在且不允许覆盖，则跳过
        if os.path.exists(output_file) and not args.overwrite:
            print(f'跳过已存在的文件 {output_file}')
            continue

        # 处理提示文本
        prompt = prompts[i].replace('    ', '\t')
        prompt_batch = [generate_prompt(prompt)]

        # 获取任务ID列表
        ids_batch = [task_ids[i]]

        # 初始化完成序列列表
        completion_seqs = []

        # 对提示文本进行编码
        encoding = tokenizer(prompt_batch, return_tensors="pt", truncation=True, max_length=args.max_len).to(device)

        # 根据解码风格确定循环次数
        if args.decoding_style == 'sampling':
            loops = int(args.N / args.num_seqs_per_iter)
        else:
            loops = 1

        # 生成序列
        for _ in tqdm(range(loops), total=loops, leave=False, ncols=0):

            with torch.no_grad():
                # 生成序列
                gen_tokens = model.generate(
                    **encoding,
                    generation_config=generation_config
                )

            # 解码生成的序列
            if gen_tokens is not None:
                gen_seqs = tokenizer.batch_decode(gen_tokens, skip_special_tokens=True)
            else:
                gen_seqs = None

            # 处理生成的序列
            if gen_seqs is not None:
                assert len(ids_batch) == 1
                task_id = ids_batch[0]

                for seq_idx, gen_seq in enumerate(gen_seqs):
                    # 提取完成序列
                    completion_seq = gen_seq.split("### Response:")[1]
                    completion_seq = completion_seq.replace('\t', '    ')
                    all_code = gen_seq.replace('\t', '    ')

                    # 将完成序列添加到列表中
                    completion_seqs.append(
                        {'task_id': task_id,
                         'completion': completion_seq,
                         'all_code': all_code,
                         }
                    )

        # 保存结果
        print("将结果保存到 {}".format(output_file))
        write_jsonl(output_file, completion_seqs)


if __name__ == '__main__':
    main()