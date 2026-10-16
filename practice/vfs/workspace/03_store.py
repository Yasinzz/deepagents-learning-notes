from deepagents.backends import StoreBackend
from langgraph.store.memory import InMemoryStore

def file_namespace(runtime):
    return ("vfs-demo",)

def other_namespace(runtime):
    return ("vfs-other",)

store = InMemoryStore()
backend = StoreBackend(store=store, namespace=file_namespace)
backend_b = StoreBackend(store=store, namespace=file_namespace)
backend_c = StoreBackend(store=store, namespace=other_namespace)

result = backend.write("/probe.txt", "hello-store")
print(result.error)
read_result = backend.read("/probe.txt")
read_result_b = backend_b.read("/probe.txt")
read_result_c = backend_c.read("/probe.txt")
print(read_result.error)
print(read_result_b.error)
print(read_result_c.error)
if read_result.error is None:
    print(read_result.file_data["content"])
if read_result_b.error is None:
    print(read_result_b.file_data["content"])
if read_result_c.error is None:
    print(read_result_c.file_data["content"])

another_store = InMemoryStore()
backend_d = StoreBackend(store=another_store, namespace=file_namespace)
read_result_d = backend_d.read("/probe.txt")
print(read_result_d.error)
if read_result_d.error is None: