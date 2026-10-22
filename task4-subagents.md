# Task4：子 Agent、消息边界与回传优化

这是 [deepagents-in-action](https://github.com/datawhalechina/deepagents-in-action) 的个人学习笔记与实验记录。整理日期：2026-10-22。

本次由本人动手实验，助手协助解释代码、编写 Advanced 提示词，并对照日志、工具实现和报告核对结果。使用的 `sources/planning.md`、`sources/files.md` 均为合成课程资料，不属于网络研究。

环境沿用本次项目：Python 3.12.3、DeepAgents 0.7.8、LangGraph 1.2.14。下文代码与证据路径均相对于原项目根目录；原始日志、请求、报告和本地配置保留在本地，公开仓库只记录脱敏摘要。

## 1. 验证什么

- Lite：定义一个职责明确的 `Source Reader`，验证主 Agent 实际通过 `task` 调用它，并根据回传完成报告。
- Basic：修改子 Agent 的提示词，要求结论附来源与原文依据；记录子图内部工具消息、主图的 `task` 回传和报告文件回读。
- Advanced：采用“改进回传内容”的路线，继续使用同一资料与报告主题，对比回传质量、长度和执行开销。

本次最终报告的主题为“为什么计划完成还需要检查实际文件”。内容验收与 Agent 自述、待办状态分别判断。

## 2. 改了什么

| 阶段 | 原项目练习文件 | 主要改动 |
| --- | --- | --- |
| Lite | `practice/subagent/workspace/01_subagent.py` | 用字典定义子角色，通过 `subagents=[source_reader]` 注册；主 Agent 负责撰写、保存和回读报告 |
| Basic | `practice/subagent/workspace/02_subagent_basic.py` | 加入已读文件、结论与依据、未确认事项、资料性质的回传要求；使用子图日志观察实际执行 |
| Advanced | `practice/subagent/workspace/03_subagent-advanced.py` | 收紧子角色职责、读取入口、证据边界和四段回传协议，增加 1200 字符的回传目标 |

Advanced 与 Basic 的静态代码对照确认：只调整了子 Agent 的 `system_prompt` 和用于区分产物的报告 slug。模型配置入口、主提示词、工具映射、输入资料、报告主题和日志方式一致。未据此声称两次执行路径完全相同。

### 角色与工具的分工

子角色配置包含四个字段：

| 字段 | 作用 |
| --- | --- |
| `name` | 委派时匹配的角色标识，本例为 `Source Reader` |
| `description` | 帮助主 Agent 判断何时委派 |
| `system_prompt` | 指导子 Agent 的工作范围、依据和回传格式 |
| `tools` | 指定子角色的业务工具，本例为 `[read_source]` |

主 Agent 的业务工具为 `save_report`、`read_report`。子 Agent 提取资料要点；主 Agent 使用回传撰写报告，再保存与回读。

角色字典只是配置；`create_deep_agent` 组装执行图；遍历 `graph.stream(...)` 时才开始运行。主 Agent 调用 `task` 时，`subagent_type` 匹配角色名字，`description` 携带本次委派任务。

### Advanced 回传协议

子 Agent 按固定顺序输出：`【已读取文件】`、`【结论与依据】`、`【未确认事项】`、`【资料性质】`。每份文件最多三条结论，每条附来源相对路径和支持结论的原文短句；英文引用每条最多 20 个单词。整份回传目标不超过 1200 个字符。

文件名已由任务给出，读取入口明确为 `read_source`。绝对路径核验不属于该角色职责，资料未说明或工具未核验的事实如实列为未确认。

这些是提示词要求，当前代码没有强制格式或长度校验；是否遵守仍以实际日志为准。

### 日志中的 Python 知识

- `for namespace, update in ...`：将每次产生的两个值拆包赋给变量。
- `update.values()`：遍历各节点的更新值；`updates` 模式记录每一步的更新。
- `value if isinstance(value, list) else [value]`：把单份、多份更新统一成列表。
- `isinstance(..., dict)` 与 `continue`：跳过不符合当前解析结构的条目。
- `.get("messages", [])`：没有消息字段时使用空列表。
- `namespace or "主 Agent"`：空 namespace 显示为主 Agent；非空值标识子图路径。
- `tool_call_id`：把工具返回与产生它的调用对应起来。

`subgraphs=True` 用于观察子图事件。日志解析代码覆盖了本次实际出现的更新结构，不把它描述成适用于所有自定义图的通用记录器。

## 3. 实际结果

Lite 实际发生两次 `task` 调用，分别读取两份资料；这属于同一角色的两次运行。两份要点回传后，主 Agent 保存并回读了报告。

Basic 的子图日志补齐了真实读取与回传证据，但也暴露了偏差：主 Agent 自行要求查找绝对路径，子 Agent 额外调用 `glob`，并从查询未命中推断资料不是普通磁盘文件。回传还增加了多余分析，没有严格遵守四段格式。

下面比较的是带子图日志的 Basic 与最后一次有完整日志的 Advanced。此前未保存日志的 Advanced 运行不计入这张对照表。

| 指标 | Basic | Advanced |
| --- | ---: | ---: |
| 主 Agent 可见 AI 消息 | 4 | 4 |
| 子 Agent 可见 AI 消息合计 | 3 | 4 |
| `task` 委派 | 1 | 2 |
| 子 Agent `read_source` 调用 | 2 | 2 |
| 子 Agent `glob` 调用 | 2 | 0 |
| 主、子全部工具调用 | 7 | 6 |
| 子 Agent 回传正文字符合计 | 2754 | 1144 |
| 子 `system_prompt` 字符数 | 218 | 847 |

字符按 Unicode 字符统计，包含正文内部空格、标点、Markdown 标记和换行，排除日志标头及首尾换行。每份回传只计算一次，不重复累计子图和主图中展示的相同文本。

Advanced 的两份回传分别为 593 字符（files）和 551 字符（planning），均低于 1200 字符。四段顺序、每文件三条结论、英文短句长度和合成资料标注均通过核对，引用与资料一致；未继续虚构磁盘存储形态。

### 收益与额外成本

本轮回传正文合计减少 1610 字符，约 58.5%；无关 `glob` 从两次降为零。结论与依据更容易核对，主 Agent 收到的回传也更精简。

与此同时，提示词增加了 629 字符；主 Agent 将一次联合委派拆成两次委派，子 Agent 可见 AI 消息由三条增至四条，全部可见 AI 消息由七条增至八条。工具总调用减少，不代表模型执行开销也一定减少。

两份日志都没有 token、耗时和费用记录。字符数不是 token 数，可见 AI 消息数也不等于底层 HTTP 请求数。因此，本次不能证明整体费用或延迟降低。

这是两次单次运行的对比。主 Agent 的任务拆分发生变化，不能把全部差异归因于子提示词，也不能据此声称已经验证稳定收益。

## 4. 证据与解释

| 本地证据 | 原项目路径与位置 |
| --- | --- |
| Lite 真实委派 | `practice/subagent/workspace/task4-lite.log` 第 13、18 行 |
| Basic 委派与子读取 | `practice/subagent/workspace/task4-basic-trace.log` 第 6、24、28 行 |
| Basic 多余查询与错误推断 | 同一 Basic 日志第 54、58、88 行 |
| Basic 主图收到回传 | 同一 Basic 日志第 157 行附近 |
| Advanced 两次委派 | `practice/subagent/workspace/task4-advanced.log` 第 6、18 行 |
| Advanced 子图读取与返回 | 同一 Advanced 日志第 34、39、51、56 行附近 |
| Advanced 四段回传 | 同一 Advanced 日志第 68、103 行起 |
| Advanced 主图收到结果 | 同一 Advanced 日志第 82、117 行附近，返回 ID 与各次 task 调用匹配 |
| Advanced 保存与回读 | 同一 Advanced 日志第 139、194 行起 |
| 最终报告 | `blogs/task4-advanced/post.md` |

本次核对确认：子图的最后总结与主图收到的对应 `task` 正文一致；两份 `read_source` 返回与磁盘源文件一致；保存参数、回读正文和运行验收时的磁盘报告一致。

### 消息边界与存储边界

日志能显示子 Agent 的内部工具消息，但这些消息不会因为开启日志而全部进入主 Agent 的消息历史。本例中，主 Agent 收到的是对应的 `task` 回传总结。namespace 是观测与组织标识，不构成执行沙箱或身份授权。

`tools=[read_source]` 指定的是子角色业务工具；框架仍可能附加内置文件工具。本例没有显式配置 backend，新图使用默认 `StateBackend`。内置 `glob` 查询该后端，而 `lesson_tools.py` 中的 `read_source` 通过 `Path.read_text` 读取真实磁盘的 `sources/<文件名>`。

因此，虚拟后端查询为空，只说明该次查询未命中，不能推出真实磁盘文件不存在。提示词中“不调用 glob”属于行为约定；若需要强制限制工具，应通过相应工具或中间件配置实现。

### 报告人工修订

运行报告来源说明中的“完成后回读”表述不准确，整理笔记时人工修订为“保存后回读，验收后标记完成”。原始日志保留不改；修订后的磁盘报告与原始日志存在这一处文字差异。该规则来自本次合成课程资料，不是 SDK 自动强制的验收机制。

## 5. 下一步修正

- 改进主 Agent 的委派描述：明确使用 `read_source`、传文件名、返回来源相对路径，减少不属于任务目标的绝对路径请求。
- 如需更严格的对照，固定委派策略，例如一次委派读取两份资料，再收集多次运行结果，避免任务拆分差异干扰判断。
- 若需要验证实际运行成本，记录各次模型调用的 usage、耗时与计价依据；不能只拿最后一条回复的 token 代替整个任务总量。
- 若回传格式与长度必须严格满足要求，增加程序化验收，再明确失败后的处理方式。
- 继续分别核对任务状态、工具结果和报告内容，保持“保存 → 回读验收 → 标记完成”的顺序。

Lite、Basic 和 Advanced 的核心实验均已有本地证据；Basic 的偏差、Advanced 的收益、额外开销和对照限制一并保留。公开材料遵守仓库的 [安全红线](../SECURITY.md)。
