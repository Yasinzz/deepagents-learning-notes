# Task2：虚拟文件系统与存储边界

这是 [datawhalechina/deepagents-in-action](https://github.com/datawhalechina/deepagents-in-action) 的个人学习记录。本文根据本机代码、练习输出和无模型接口验证整理，用于理解文件存在哪里、何时保留、哪些调用能够共享数据。Task2 是本次学习阶段的名称，不是原课程的正式任务编号。

## 环境与验证范围

本次环境为 Python 3.12，项目固定 `deepagents==0.7.8`。本机依赖还包括 `langchain==1.4.3`、`langgraph==1.2.14`、`langgraph-checkpoint==4.2.0`。以下结论对应这些版本。

实验直接调用后端，或通过单节点 `StateGraph` 运行。没有调用真实模型，没有进行真实模型的新会话偏好测试。记忆加载的说明来自本机中间件源码核对。

公开记录中的 `<project_root>` 代表本地项目根目录。安全红线：不提交 `.env`、真实密钥、真实偏好正文、私人身份信息或运行产生的敏感文件。实验使用虚构文本，本文不包含个人偏好内容。

## 四种后端分别负责什么

| 后端 | 数据实际保存在哪里 | 共享条件 | 本次实验的保留范围 |
|---|---|---|---|
| FilesystemBackend | `root_dir` 下的真实文件 | 访问同一磁盘位置 | 重启进程后仍可读取已有文件 |
| StateBackend | 图状态的 `files` 通道 | 恢复同一线程状态 | 配合相同 InMemorySaver，可在进程内恢复线程 |
| StoreBackend | 显式 store 中的 namespace 与文件键 | 同一个 store、相同 namespace | InMemoryStore 仅保留进程内数据 |
| CompositeBackend | 由路径选中的底层后端 | 取决于各底层后端 | 自身负责路由，不额外保存文件 |

“跨线程共享”与“重启进程后保留”是两种能力。选择 StoreBackend 并不自动获得磁盘持久化，实际生命周期取决于使用的 store。

## 实验 1：虚拟路径仍然可以落在磁盘

`01_filesystem.py` 以脚本所在目录为 `root_dir`，开启 `virtual_mode=True`。后端中的 `/probe.txt` 对应根目录下的真实 `probe.txt`。

先写入 `hello vfs`，再注释写入并重新启动进程，仍然能够读到正文。随后手动修改真实文件，新进程读到了 `changed-on-disk`。这说明数据来自磁盘，而非上一次进程保留下来的 Python 对象。

`virtual_mode` 控制路径解释与根目录约束，不表示数据只在内存中。当前脚本保留的是只读阶段；全新目录没有 `probe.txt` 时，需要先完成初始化写入。

## 实验 2：StateBackend 需要图执行上下文

0.7.8 使用无参 `StateBackend()`。读写放在图节点内，状态类型使用 `FilesystemState`，文件字段名为 `files`。普通脚本中直接调用后端读写会缺少图执行上下文。

节点调用 `write` 后，即使返回空字典，后端也会自行提交文件更新。节点内立即调用后端 `read`，能够读到刚写的正文；节点入参 `state["files"]` 不会因此原地变化。

加入 `InMemorySaver` 后，按 A、A、B、A 的线程顺序调用。节点初始文件状态依次为空、有 probe、为空、有原来 A 的 probe；初始化写入只发生两次。

切换到 B 没有删除 A 的文件。返回 A 时，检查点恢复了 A 的状态。重启进程则会失去这个内存保存器中的数据。没有检查点或其他显式状态传递时，也不能仅凭相同线程名期待恢复。

## 实验 3：Store 的边界由实例与 namespace 决定

A、B 后端复用同一个 `InMemoryStore`，namespace 都返回 `("vfs-demo",)`，因此能够读取同一份 `hello-store`。C 复用 store、改用 `vfs-other`，读取相同路径时不存在。

D 使用新建的 store，即使 namespace 与 A 相同，也读不到 A 的数据。这验证了两个边界：namespace 隔离同一 store 内的数据；不同 store 实例本身也不共享数据。

本次图外调用显式传入 store，namespace 使用忽略运行时参数的函数。它必须是返回元组的可调用对象，不能直接传入固定元组。这里不需要 `thread_id`。

历史实验现象已观察到，但当前 `03_store.py` 末尾存在未完成的 `if` 语句，尚不能直接运行。详见[错误记录](troubleshooting.md)。

## 实验 4：Composite 会剥掉路由前缀

配置默认后端为 StateBackend，`/memories/` 路由到 StoreBackend。通过 Composite 写入 `/memories/note.txt`，底层 Store 实际保存的键是 `/note.txt`。

因此，直接用底层 StoreBackend 读取 `/note.txt` 成功，读取 `/memories/note.txt` 不存在。Composite 返回的写入路径仍是完整外部路径，不能把它当作底层存储键。

随后在图节点内访问 `/scratch.txt` 与 `/memories/note.txt`，再次执行 A、A、B、A。scratch 分别属于 A、B 的线程状态，只初始化两次；note 在四次读取中均存在，因为实验复用了同一个 store 与固定 namespace。

图最终的 `files` 只有 scratch。Store 中的 note 不会自动出现在这个状态字段中。只走显式 Store 路由可以在图外调用；走默认 StateBackend 路径仍需要图上下文。

## 实验 5：追踪同一个偏好文件的两条读取路径

`05_memory_path.py` 比较了两种读取：Path 直接打开 `<project_root>/memory/preferences.md`，以及后端读取 `/memory/preferences.md`。历史输出中，后端错误为 `None`，正文比较结果为 `True`。

这个结果说明当时两条路径读到了相同文本。它没有验证模型记住偏好，也不能推广为任意长度文件始终完全相等；后端 `read` 默认按行限制读取窗口。

当前脚本仍有条件外重复读取 `file_data` 的语句，成功时重复打印，失败时可能报错。该问题尚未整理，不把它写成已经完成的修正。

## 回到项目：替换 backend 不会迁移所有工具

项目的 `agent.py` 把 FilesystemBackend 传给 DeepAgents 与显式 MemoryMiddleware，并配置 `/AGENTS.md`、`/memory/preferences.md` 和 `/skills/`。

但 `lesson_tools.py` 的 `read_source`、`save_report`、`read_report`、`save_preference` 使用 Path 直接读写项目文件。它们绕过后端，单独替换 backend 不会改变这些工具的保存位置，也不会自动迁移已有文件。

## 记忆加载还存在状态缓存

本机 MemoryMiddleware 在执行开始时检查 `memory_contents`。该字段不存在时，通过后端 `download_files` 读取 sources，解码后保存到状态；模型调用前，再把内容追加到系统消息。

状态已有该字段时会跳过读取，即使值为空字典。`save_preference` 写文件并返回正文，但没有同步刷新该字段。因此，已有会话不保证下一次调用自动重读磁盘。这里的状态缓存也不同于模型提示缓存。

下一步阅读项目时，先标出每次操作访问的是磁盘、线程状态还是 store，再检查它是否经过 backend。遇到“数据怎么没了”或“为什么共享了”，就沿着这三个位置追踪。
