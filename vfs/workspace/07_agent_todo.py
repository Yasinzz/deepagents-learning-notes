from content_builder_deepagent.agent import graph

message = {
    "role": "user",
    "content": """请完成一次本地课程实验。先用 write_todos 建立阅读资料、撰写并保存报告、回读核对三项 pending 待办。执行某项工作前，把该项更新为 in_progress。
使用 read_source 读取 planning.md，根据它写一份中文短报告，说明三个 Todo 状态，以及为什么计划完成不能代替实际验收。报告须有标题，注明“合成课程资料”，引用 sources/planning.md。
使用 save_report 保存，slug 为 task3-lite；成功后使用 read_report 回读，检查内容和来源。回读检查通过后，才能把报告相关待办标为 completed。
每轮至多调用一次 write_todos。保存、回读、最终完成更新必须分别等待前一步工具成功返回。最后用文字给出报告摘要和保存路径。不联网、不生成图片。"""
}

# result = graph.invoke({"messages": [{"role": "user", "content": message["content"]}]},)

# print(result.get("todos"))
# print(result.get("messages"))
for snapshot in graph.stream({"messages": [message]}, stream_mode="values"):
    if snapshot.get("todos"):
        print(snapshot["todos"])
    snapshot["messages"][-1].pretty_print()