from pathlib import Path
from deepagents.backends import FilesystemBackend

def main():
    workspace = Path(__file__).resolve().parent
    #print(f"Workspace path: {workspace}")
    backend = FilesystemBackend(root_dir=workspace, virtual_mode=True)
    #print(type(backend))
    #result = backend.write("/probe.txt", "hello vfs")
    #print(result.error)
    #print(result.path)
    read_result = backend.read("/probe.txt")
    print(read_result.error)
    if read_result.error is None:
        print(read_result.file_data["content"])



main()