from langchain.agents.middleware import TodoListMiddleware
from langchain.agents.middleware.todo import write_todos
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from langchain_core.messages import AIMessage

middleware = TodoListMiddleware()
# print(middleware.tools[0].name)
# print(middleware.state_schema.__annotations__.keys())

todo = [
    {"content": "阅读合成课程资料sources/planning.md", "status": "pending"},
    {"content": "根据资料撰写并保存报告", "status": "pending"},
    {"content": "回读报告，核对内容", "status": "pending"}
]
# print(todo)
# todo[0]["status"] = "in_progress"
# print(todo)

tool_call = {"name": "write_todos", "args": {"todos": todo}, "id": "todo-demo-1", "type": "tool_call"}
result = write_todos.invoke(tool_call)
# print(type(result))
# print(result.update["todos"])   

builder = StateGraph(middleware.state_schema)
builder.add_node(ToolNode(middleware.tools))
builder.set_entry_point("tools")
builder.set_finish_point("tools")

graph = builder.compile()

message = AIMessage(content="", tool_calls=[tool_call])

state_result = graph.invoke({"messages": [message]})
print(state_result["todos"])