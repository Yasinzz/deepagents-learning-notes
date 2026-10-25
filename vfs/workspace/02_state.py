from langgraph.graph import StateGraph
from deepagents.middleware.filesystem import FilesystemState
from deepagents.backends import StateBackend
from langgraph.checkpoint.memory import InMemorySaver

def inspect_state(state):
    print(state["files"])
    backend = StateBackend()
    if "/probe.txt" not in state["files"]:
        write_result = backend.write("/probe.txt", "hello-state")
        print("执行写入")
    #print(write_result.error)
    read_result = backend.read("/probe.txt")
    #print(read_result.error)
    #if read_result.error is None:
        #print(read_result.file_data["content"])
    return {}

builder = StateGraph(FilesystemState)
builder.add_node("inspect", inspect_state)
builder.set_entry_point("inspect")
builder.set_finish_point("inspect")

graph = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "vfs-a"}}
other_config = {"configurable": {"thread_id": "vfs-b"}}

graph.invoke({"files": {}}, config)
graph.invoke({}, config)
graph.invoke({"files": {}}, other_config)
graph.invoke({}, config)