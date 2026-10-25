from content_builder_deepagent.agent import graph

message = {
    "role": "user",
    "content": "请根据本地课程资料 planning.md，整理一份简短的中文学习摘要。保存结果并回读核对，slug 使用 task5-lite。"
}

for namespace, update in graph.stream(
    {"messages": [message]},
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