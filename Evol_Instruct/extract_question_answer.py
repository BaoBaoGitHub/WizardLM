import json
import re


def ci_find(text, sub, start=0):
    """
    大小写不敏感的find方法，返回第一次出现的位置，如果未找到则返回 -1
    """
    return text.lower().find(sub.lower(), start)


def find_first_marker(text, markers, start=0):
    """
    在text中，从start位置开始，查找给定markers列表中最先出现的标记
    返回 (index, marker) ，如果都未找到返回 (-1, None)
    """
    lowest_index = -1
    selected_marker = None
    for marker in markers:
        idx = ci_find(text, marker, start)
        if idx != -1 and (lowest_index == -1 or idx < lowest_index):
            lowest_index = idx
            selected_marker = marker
    return lowest_index, selected_marker


def parse_content(content):
    """
    使用多种标记和大小写不敏感查找方式，尽可能兼容地提取出content中的问题和答案。
    支持的问题标记：
      **Optimized Question:**、**Question:**、Optimized Question、Question
    支持的答案标记：
      **Optimized Java Code:**、**Java Code Solution:**、Optimized Java Code、Java Code Solution
    返回 (question, answer)，如果解析失败，则返回 (None, None)
    """
    # 定义可能出现的标记列表
    question_markers = [
        "**Optimized Question:**",
        "Optimized Question",
        "**Question:**",
        "Question",
    ]
    answer_markers = [
        "**Optimized Java Code:**",
        "**Java Code Solution:**",
        "Optimized Java Code",
        "Java Code Solution",
        "**Solution Code**",
        "Solution Code",
        "**Java Code**",
        "Java Code",
        "```java",
    ]

    # 查找第一个问题标记
    q_index, q_marker = find_first_marker(content, question_markers)
    if q_index == -1 or not q_marker:
        return None, None
    question_start = q_index + len(q_marker)

    # 从问题标记后开始，查找答案标记
    a_index, a_marker = find_first_marker(content, answer_markers, start=question_start)
    if a_index == -1 or not a_marker:
        return None, None

    # 截取问题文本，并去除多余前后空白
    question_text = content[question_start:a_index].strip()

    question_text = clean_instruction(question_text)
    
    # 截取答案文本，同时去除答案标记的前缀
    answer_text = content[a_index + len(a_marker) :].strip()
    # 从答案中搜索```java，如果找到则截取到该位置到```之间的内容
    if "```java" in answer_text:
        answer_text = extract_java_code(answer_text)

    return question_text, answer_text

def extract_java_code(text):
    """
    从文本中提取 ```java 和 ``` 之间的内容。
    
    参数：
        text (str): 输入的文本，可能包含Java代码块。
    
    返回：
        str: 提取的Java代码内容，如果未找到则返回空字符串。
    """
    # 正则表达式模式，匹配 ```java 和 ``` 之间的内容
    pattern = r'```java\n(.*?)```'
    
    # 使用 re.search 查找第一个匹配项，启用 DOTALL 模式
    match = re.search(pattern, text, re.DOTALL)
    
    # 如果找到匹配项，返回提取的内容；否则返回空字符串
    if match:
        return "```java\n" + match.group(1).strip() + "\n```"
    else:
        return None
    
def clean_instruction(instruction):
    """清理 instruction 字段，去除开头和结尾的多余部分"""
    # 去除开头的逗号或冒号及其后的空格
    instruction = instruction.lstrip(', :')

    # 去除开头的标题（以 ** 开头并以 ** 结尾的部分）
    if instruction.startswith('**'):
        match = re.search(r'\*\*(.*?)\*\*\s*', instruction)
        if match:
            instruction = instruction[match.end():].strip()

    # 去除结尾的分隔符（###, **, 或 ---）
    instruction = re.sub(r'\s*(###|\*\*|---)$', '', instruction).strip()

    return instruction

if __name__ == "__main__":
    # 使用示例：从当前数据文件中解析问题和答案记录
    input_file = "/home/baoxuanlin/graduation/WizardLM/Evol_Instruct/data/merged_batch_question_and_result_data.jsonl"
    output_file = "/home/baoxuanlin/graduation/WizardLM/Evol_Instruct/data/extracted_questions_and_answers_compatible.jsonl"

    success_count = 0
    raw_index = 0

    with open(input_file, "r", encoding="utf-8") as infile, open(
        output_file, "w", encoding="utf-8"
    ) as outfile:
        for line in infile:
            raw_index += 1
            try:
                data = json.loads(line)
                # 根据具体数据结构提取content字段，此处假设为嵌套结构中的 message.content
                content = (
                    data.get("response", {})
                    .get("body", {})
                    .get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                )
                if not content:
                    print(f"跳过空内容的记录: {line[:50]}...")
                    continue
                question, answer = parse_content(content)
                if question and answer:
                    output_data = {
                        "raw_index": raw_index,
                        "instruction": question,
                        "response": answer,
                    }
                    outfile.write(json.dumps(output_data, ensure_ascii=False) + '\n')
                    success_count += 1
                else:
                    print(f"解析失败的记录: {line[:50]}...")
            except json.JSONDecodeError:
                print(f"跳过无效的JSON行: {line[:50]}...")

    print(f"总共成功解析 {success_count} 条记录")
