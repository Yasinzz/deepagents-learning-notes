# DeepAgents in Action 学习笔记

本仓库是 **[datawhalechina/deepagents-in-action](https://github.com/datawhalechina/deepagents-in-action) 的个人学习笔记与实验记录**，独立维护。内容以原项目、本机代码阅读和实际实验结果为依据，保留版本与验证范围。

原项目的课程、代码与图片归各自作者所有；需要完整教材或运行项目时，请访问上面的原仓库。

## 学习记录

| 学习任务 | 内容 | 状态 |
| --- | --- | --- |
| Task2 | 虚拟文件系统、存储后端对比、项目文件读写链路 | 核心实验已验证；原练习脚本仍有收尾项 |
| Task3 | Todo 机制、显式中间件、固定资料报告与独立验收 | Lite / Basic 核心实验已验证；执行偏差与日志记录改进已注明 |
| Task4 | 子 Agent、task 委派、主子消息边界与回传优化 | Lite / Basic / Advanced 核心实验已验证；收益、额外开销与单次对照限制已记录 |
| Task5 | Skill 匹配、正文读取与课程摘要流程 | Lite / Basic 核心链路已验证；执行偏差已记录，修订版未重跑；Advanced 跳过 |
| Task6 | 跨会话文件记忆、发布审批、用户隔离与风险分层 | Lite / Basic 核心实验已验证；拒绝分支已补自动计数；Advanced 实测跳过，隔离与 edit 仅原理，风险分层仅方案 |

这里的 Task2 是本次学习计划的编号，对应原项目第 3 章中的后端学习内容。

## 笔记导航

- [Task2：虚拟文件系统与存储边界](notes/task2-virtual-filesystem.md)
- [Task3：Todo 机制与中间件](notes/task3-todo.md)
- [Task4：子 Agent、消息边界与回传优化](notes/task4-subagents.md)
- [Task5：Skill 匹配、读取与实际执行](notes/task5-skills.md)
- [Task6：跨会话记忆、工具审批与安全边界](notes/task6-memory-and-approval.md)
- [course-brief Skill 示例（修订版，未重跑）](examples/course-brief/SKILL.md)
- [排错记录与待整理项](notes/troubleshooting.md)
- [安全红线](SECURITY.md)
- [新笔记模板](templates/note-template.md)

## 本次实验环境

| 组件 | 本机核对版本 |
| --- | --- |
| Python | 3.12.3 |
| DeepAgents | 0.7.8 |
| LangGraph | 1.2.14 |
| LangGraph Checkpoint | 4.2.0 |

这些是本次实验使用的版本。阅读其他版本的文档时，要重新核对构造参数和状态更新机制。

## 安全红线

公开仓库只保存脱敏后的学习材料。提交前必须遵守 [SECURITY.md](SECURITY.md)：

- **不提交凭据**：API Key、Token、密码、私钥、真实 `.env`、带认证信息的 URL。
- **不提交个人原始数据**：真实偏好文件、对话、模型请求、运行日志、跟踪文件和私人业务内容。
- **不把虚拟路径当作沙箱或鉴权**：`virtual_mode`、namespace 和 `thread_id` 都有各自的作用边界。
- **不整包上传原项目**：笔记仓库单独维护；原项目中的依赖、运行产物和本地配置不进入提交。

本仓库中的文件名、正文与路径示例使用学习用数据。主机绝对路径统一写为 `<project_root>` 等占位符。

## 记录方式

每次学习后，用模板记录以下内容：

1. 明确问题、环境版本和对应源码入口。
2. 记录自己执行的步骤与真实输出，区分预期、观察和推断。
3. 写清结论的适用范围，例如同一进程、相同 store、固定 namespace。
4. 把已验证的实验结果与当前代码待修项分别记录。
5. 检查脱敏内容和提交差异，再同步到 GitHub。

Task2 的五个实验历史结果已记录在笔记中。`practice/vfs/` 中的脚本作为练习记录保留；运行前请结合笔记核对版本与待修项。
