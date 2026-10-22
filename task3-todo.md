# Task3：Todo 机制与中间件

这是 [deepagents-in-action](https://github.com/datawhalechina/deepagents-in-action) 的个人学习笔记。实验使用的 `sources/planning.md`、`sources/files.md`、`sources/memory.md` 均为合成课程资料。

## 初步复盘（保留原文）

1 验证了工具调用过程 todo状态的变化
2 改了 任务说明 并把invoke改成了stream来观察过程
3 实际结果 没有完全按照content来 初始计划没有改回pending
4 证据就是循环快照中 打印每步的状态
5 下一步进行进一步的约束 检查首次计划是否全部pending 以及 read_report 前是否把回读项更新为 in_progress。强化提示后，仍要核对日志。

## 验收补充（由助手对照日志、资料和报告核对）

上方第 3 条记录的是 Lite 的偏差。下面分别记录 Lite 与 Basic，避免把不同运行的状态混在一起。路径均相对于原项目根目录，原始运行日志留在本地；笔记仓库只记录脱敏后的结果摘要。

### 1. 验证什么

验证 `write_todos` 是否实际调用并更新 `todos`；观察任务状态变化；验证报告保存、回读以及独立内容检查。计划全部 `completed` 与报告验收通过分别判断。

### 2. 改了什么

- `06_todo.py`：先构造计划和工具调用，再通过 `StateGraph`、`ToolNode` 观察更新进入状态。
- `07_agent_todo.py`：修改任务说明，用 `.stream(stream_mode="values")` 观察真实 Agent 执行过程，并保存 Lite 日志。
- `08_basic_todo.py`：自己调用 `create_deep_agent`，显式传入 `TodoListMiddleware()` 和三个业务工具；任务说明按目标、资料、报告要求、执行规则、验收标准、最终回复六部分组织。

### 3. 实际结果

| 运行与阶段 | 阅读资料 | 写作并保存 | 回读核对 |
| --- | --- | --- | --- |
| Lite 首次记录 | in_progress | pending | pending |
| Lite 阅读后 | completed | in_progress | pending |
| Lite 最终记录 | completed | completed | completed |
| Basic 首次记录 | pending | pending | pending |
| Basic 阅读后 | completed | in_progress | pending |
| Basic 最终记录 | completed | completed | completed |

Lite 与 Basic 的保存正文、回读正文及验收时的磁盘报告一致。Basic 报告的四个章节、三个主题、至少三个实践步骤、合成资料标注与来源引用通过独立检查，核心结论与三份资料一致。

执行规范仍有偏差：Lite 未先建立全部 pending 的计划；Basic 做到了这一点，但阅读和回读任务仍跳过了 in_progress。Basic 的三个资料读取请求也出现在同一轮响应中，没有完全遵循“依次读取”的要求。

### 4. 证据与解释

| 证据 | 本地路径与核对位置 |
| --- | --- |
| Lite 状态变化 | `practice/vfs/workspace/task3-lite.log` 第 25、52、143 行 |
| Lite 保存报告 | `blogs/task3-lite/post.md` |
| Basic 状态变化 | `practice/vfs/workspace/task3-basic.log` 第 45、84、222 行 |
| Basic 保存、回读、最终更新返回 | 同一 Basic 日志第 147、161、224 行附近 |
| Basic 保存报告 | `blogs/task3-basic/post.md` |

Basic 日志中，保存成功返回在回读调用之前；回读返回又在最终完成更新之前，最后另有文字摘要与路径。验收同时对照了保存参数正文、回读正文、磁盘文件和三份输入资料。

当前打印代码只显示每个快照的最后一条消息。Basic 一轮发起三个 `read_source` 调用时，日志只展示该批最后一个工具返回，不能据此逐个确认前两个返回内容。这是观测缺口；报告正文已另行对照三份资料核验。

这些实验说明：中间件能提供工具并更新状态，但不会强制每项任务都经过所有状态，也不会自动检查报告质量。原报告中的进度表还可能是保存时的快照，后续更新 todos 不会自动改写 Markdown。

### 5. 下一步修正

- 检查阅读、回读开始前是否真正调用工具记录 in_progress，不能只检查最终 completed。
- 遍历快照中的新增消息，按消息 ID 去重，保留同批次每个工具调用与返回，避免只看最后一条消息。
- 将状态、工具结果、文件内容分别验收；提示加强后仍以日志和实际产物为依据。

本次核心实验和报告内容已验证；上述执行偏差与日志记录改进保留为后续修正项，不把本次描述为“完全遵循了所有提示”。
