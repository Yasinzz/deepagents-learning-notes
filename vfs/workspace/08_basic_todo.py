from deepagents import create_deep_agent
from langchain.agents.middleware import TodoListMiddleware
from content_builder_deepagent.agent import model
from content_builder_deepagent.lesson_tools import read_source, save_report, read_report


graph = create_deep_agent(
    model=model,
    middleware=[TodoListMiddleware()],
    tools=[
        read_source, save_report,
        read_report
    ],
)

# print(type(graph))
message = {
    "role": "user",
    "content": """【目标】
仅根据下列三份合成课程资料，完成一份中文课程报告，解释任务规划、文件产物和记忆边界。

【输入资料】
使用 read_source 依次读取 planning.md、files.md、memory.md。
调用工具时 name 参数只填写文件名；报告引用时写完整来源路径 sources/planning.md、sources/files.md、sources/memory.md。
内容以这些资料为依据，不联网、不生成图片。

【报告要求】
报告须有一个标题，并包含以下四节：
1. Context：说明报告目的，并明确标注“合成课程资料”。
2. Findings：分别讨论规划、文件产物、记忆边界，每个主题引用对应资料。
3. Practical steps：提出至少三个具体、可验证的实践步骤。
4. Sources：列出实际使用的全部三份资料路径。

【执行规则】
1. 自行把工作拆成可验收的待办，只列实际工作，不把“更新待办”本身列为任务。
2. 首次调用 write_todos 只建立全部为 pending 的计划；等工具返回后，再把即将开始的任务更新为 in_progress，等待更新成功后开始实际工作。
3. 每次更新待办都保留完整清单。每轮模型响应最多调用一次 write_todos，但整个任务可以在不同轮次多次更新计划。
4. 读取资料并撰写报告后，用 save_report 保存，slug 固定为 task3-basic。保存成功后，再用 read_report 回读同一 slug。
5. 保存、回读、最终完成更新属于依赖步骤，必须分别等待前一步工具成功返回后再继续。
6. 报告撰写和保存相关任务，只有在回读检查通过后才能标为 completed；失败或尚未完成的任务保持未完成状态。

【验收标准】
1. 三份资料均已通过 read_source 成功读取。
2. 实际报告位于 blogs/task3-basic/post.md，标题、四个章节、合成资料标注和三份来源齐全。
3. 规划部分说明三个状态，并明确 completed 不能代替产物验收。
4. 文件部分说明本项目输入在 sources/、报告在 blogs/<slug>/post.md，以及回读的作用。
5. 记忆部分区分 AGENTS.md 中的固定指导和显式要求保存的偏好，并说明保留同一项目目录时文件可跨线程和应用重启保留，不同副本或机器不自动共享这些文件。
6. 回读正文与保存内容一致，结论有资料依据；不能只凭 todos 全部 completed 就宣称报告合格。

【最终回复】
核对成功后，先完成相关待办的状态更新，再用文字给出报告摘要、保存路径和验收结果。若存在未通过项，如实说明。
""",
}

for snapshot in graph.stream({"messages": [message]}, stream_mode="values"):
    if snapshot.get("todos"):
        print(snapshot["todos"])
    snapshot["messages"][-1].pretty_print()