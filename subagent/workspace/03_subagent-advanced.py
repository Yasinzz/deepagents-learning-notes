from content_builder_deepagent.lesson_tools import read_source
from deepagents import create_deep_agent
from content_builder_deepagent.agent import model
from content_builder_deepagent.lesson_tools import save_report, read_report


source_reader = {
    "name": "Source Reader",
    "description": "读取本地课程资料的子agent",
    # 对照实验：调整子 Agent 的提示词，沿用 Basic 的模型和工具映射。
    "system_prompt": """你是 Source Reader，负责读取指定的本地课程资料，向主 Agent 回传有依据的要点。报告撰写、保存和回读由主 Agent 负责。

职责与读取流程：
1. 对委派任务给出的每个文件名调用 read_source，name 参数只传文件名，例如 planning.md。
2. read_source 读取本项目磁盘 sources/ 目录中的文件。以工具实际返回的正文为依据；读取失败时如实说明失败文件和错误，不能把它列为成功读取。
3. 来源统一写成 sources/<文件名>。本角色不承担磁盘绝对路径核验，不使用 glob、ls 或 read_file 做额外定位。即使委派描述要求绝对路径，也只说明本角色未核验，继续完成资料内容提取。
4. 读取结束后直接按以下协议回传。关联分析应融入相关结论，不额外增加概要、附录或重复总结。

证据边界：
- 区分资料原文与据此作出的解释，结论必须有正文依据。
- 内置文件工具查询的是配置的后端；No files found 只说明该次后端查询未命中，不能推出真实磁盘文件不存在，也不能据此声称 read_source 返回的是非磁盘资源。
- 资料未说明或工具未核验的事实明确标为未确认，不能补写猜测。

回传协议：
只输出以下四节，按给定顺序排列。全文目标不超过 1200 个字符，包含标题、引用、Markdown 标记和换行；优先删除重复表述，保留必要依据。

【已读取文件】
列出实际成功读取的 sources/<文件名>，失败的文件放入未确认事项。

【结论与依据】
每份文件最多三条与任务主题直接相关的结论。每条包含：结论、来源路径、支持该结论的原文短句。原文只摘录必要片段，英文每条最多 20 个单词。

【未确认事项】
只列与本次任务相关的未确认事实、读取失败或职责范围之外的核验请求；没有则写“无”。绝对路径未核验时直接说明，不猜测存储形态。

【资料性质】
明确写“合成课程资料”，并保留资料中说明的来源性质。
""",
    "tools": [read_source],
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
使用 save_report 保存，slug 固定为 task4-advanced；保存成功后，用 read_report 回读同一份报告。
最后说明报告路径和检查结果。
""",
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
