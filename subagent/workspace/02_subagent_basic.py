from content_builder_deepagent.lesson_tools import read_source
from deepagents import create_deep_agent
from content_builder_deepagent.agent import model
from content_builder_deepagent.lesson_tools import save_report, read_report


source_reader = {
    "name": "Source Reader",
    "description": "读取本地课程资料的子agent",
    "system_prompt": """你负责读取委派任务指定的本地课程资料。使用 read_source，参数只传文件名，例如 planning.md。按以下格式回传实际读取结果，报告撰写与保存由主 Agent 负责。
    【已读取文件】
列出实际成功读取的文件。

【结论与依据】
每条写清：结论、来源文件、支持该结论的原文短句。
每份文件最多提取三条。

【未确认事项】
资料未说明的内容明确写“资料未说明”，不自行补充。

【资料性质】
明确标注“合成课程资料”。""",
    "tools": [read_source]
}
graph = create_deep_agent(
    model=model,
    tools=[save_report, read_report],
    subagents=[source_reader],
    system_prompt="""你是课程报告的主 Agent。通过 task 将资料读取委派给 Source Reader；收到资料要点后负责撰写报告，使用 save_report 保存，成功后使用 read_report 回读检查。""",
)
messagee = {
    "role": "user",
    "content": """将读取 planning.md、files.md 的工作委派给 Source Reader。
根据回传要点，写一份中文短报告，说明“为什么计划完成还需要检查实际文件”。
标注“合成课程资料”，引用实际使用的来源路径。
使用 save_report 保存，slug 固定为 task4-basic；保存成功后，用 read_report 回读同一份报告。
最后说明报告路径和检查结果。
"""
}

for namespace, update in graph.stream(
    {"messages": [messagee]},
    stream_mode="updates",
    subgraphs=True,
):
    for value in update.values():
        parts = value if isinstance(value, list) else [value]
        for node_update in parts:
            if not isinstance(node_update, dict):
                continue
            for item in node_update.get("messages", []):
                print("消息位置：", namespace or "主 Agent")
                if item.type == "tool":
                    print("对应调用：", item.tool_call_id)
                item.pretty_print()



# print(type(graph).__name__)
# print(source_reader["name"])
# print(source_reader["tools"][0].name)