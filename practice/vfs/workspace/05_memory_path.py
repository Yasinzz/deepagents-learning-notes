from pathlib import Path
from deepagents.backends import FilesystemBackend

project_root = Path("/home/sunyi/projects/deepagent/content_builder_deepagent")
target = project_root.joinpath("memory", "preferences.md")
backend = FilesystemBackend(root_dir=project_root, virtual_mode=True)

direct_text = target.read_text(encoding="utf-8")
read_result = backend.read("/memory/preferences.md")

print(read_result.error)
if read_result.error is None:
    print(read_result.file_data["content"] == direct_text)
# print(read_result.file_data["content"] == direct_text)