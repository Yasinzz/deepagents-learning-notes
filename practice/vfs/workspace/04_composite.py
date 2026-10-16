from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph
from deepagents.middleware.filesystem import FilesystemState

def file_namespace(runtime):
    return ("vfs-demo",)

def inspect_composite_state(state):
    print(state["files"])
    if "/scratch.txt" not in state["files"]:
        result = backend.write("/scratch.txt", "hello-scratch")
        print("初始化scratch.txt")
        print(result.error)
    read_result = backend.read("/scratch.txt")
    read_result2 = backend.read("/memories/note.txt")
    print(read_result.error)
    print(read_result2.error)
    if read_result.error is None:
        print(read_result.file_data["content"])
    if read_result2.error is None:
            print(read_result2.file_data["content"])
    return {}

store = InMemoryStore()
store_backend = StoreBackend(store=store, namespace=file_namespace)

backend = CompositeBackend(
    default=StateBackend(),
    routes={"/memories/": store_backend},
)

builder = StateGraph(FilesystemState)
builder.add_node("inspect", inspect_composite_state)
builder.set_entry_point("inspect")
builder.set_finish_point("inspect")



result = backend.write("/memories/note.txt", "hello-composite")
# store_read_result1 = store_backend.read("/memories/note.txt")
# print(store_read_result1.error)
# store_read_result2 = store_backend.read("/note.txt")
# print(store_read_result2.error)
# if store_read_result1.error is None:
#     print(store_read_result1.file_data["content"])
# if store_read_result2.error is None:
#     print(store_read_result2.file_data["content"])    

config = {"configurable": {"thread_id": "vfs-a"}}
other_config = {"configurable": {"thread_id": "vfs-b"}}

graph = builder.compile(checkpointer=InMemorySaver())
graph.invoke({"files": {}}, config)
graph.invoke({}, config)
graph.invoke({"files": {}}, other_config)
graph.invoke({}, config)
# print(final_state["files"])