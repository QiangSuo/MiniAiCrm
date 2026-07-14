# XERP 客户情报平台轻量版实施计划

本目录是基于“统一 Codex Agent 后端 + 飞书多维表格 + 飞书 Wiki”的新版轻量路线拆解，并已按“Codex 快速开发 + 人做业务验收”的方式重新调整周期和推进节奏。

与上一版重架构不同，本版第一阶段不建设 PostgreSQL、RAGFlow、MinIO、Kafka、Temporal 或独立管理后台，而是优先利用飞书生态完成业务闭环。


> [!IMPORTANT]
> **2026-07-15 离线 Demo 已在提交 `c68d3db` 完成。** 当前执行入口已切换为 [08-Demo后CodexCLI持续开发计划.md](./08-Demo后CodexCLI持续开发计划.md) 和 `.planning/post-demo-mvp/`。`07` 与 `.planning/demo-2026-07-15/` 作为已完成历史记录保留。后续 Codex 从 Sprint 0 的仓储契约与类型边界开始，逐步接入 Base、真实飞书事件、模型、文档处理、报告提醒和试运行能力。

## 新版路线一句话

```text
飞书做入口和协作界面，
多维表格做轻量结构化事实库，
Wiki 做客户展示页，
统一 Codex Agent 后端做理解、提案、确认、工具调用和自动化。
```

## 文档清单

| 文档 | 用途 |
| --- | --- |
| [00-轻量版总体路线图.md](./00-轻量版总体路线图.md) | 总体架构、阶段路线、角色分工、里程碑和取舍边界 |
| [00-阶段零-Codex快速开发准备.md](./00-阶段零-Codex快速开发准备.md) | 建立项目骨架、开发约束、飞书配置清单和 Codex 每日任务拆法 |
| [01-阶段一-飞书多维表格数据底座.md](./01-阶段一-飞书多维表格数据底座.md) | 设计并搭建 XERP 客户情报 Base、8 张核心表、视图、字段和基础权限 |
| [02-阶段二-统一CodexAgent后端与飞书接入.md](./02-阶段二-统一CodexAgent后端与飞书接入.md) | 建设飞书机器人、消息事件、卡片回调、客户上下文路由和 Agent 工具层 |
| [03-阶段三-三个核心闭环MVP.md](./03-阶段三-三个核心闭环MVP.md) | 实现“发材料、报进展、问客户”三个最小可用闭环 |
| [04-阶段四-周报提醒与经营看板.md](./04-阶段四-周报提醒与经营看板.md) | 增加客户周报、逾期提醒、风险提醒、Base 视图和轻量管理看板 |
| [05-阶段五-权限治理推广与升级边界.md](./05-阶段五-权限治理推广与升级边界.md) | 建立推广批次、权限治理、数据质量巡检和未来升级到 PostgreSQL 的判断标准 |
| [06-Base扩展性与复杂文档处理方案.md](./06-Base扩展性与复杂文档处理方案.md) | 说明 Base 如何预留迁移、分层、字段版本和复杂文档异步解析能力 |
| [07-2026-07-15-CodexCLI自主开发Demo计划.md](./07-2026-07-15-CodexCLI自主开发Demo计划.md) | 已完成的离线 Demo 冻结范围、验收闸门和 5 分钟 Runbook |
| [08-Demo后CodexCLI持续开发计划.md](./08-Demo后CodexCLI持续开发计划.md) | 基于 `c68d3db` 真实代码基线的 Sprint 路线、Codex 工作包、Exit Gate、外部验收和试运行定义 |
| [PROMPT-CODEX-EXEC-POST-DEMO.md](./PROMPT-CODEX-EXEC-POST-DEMO.md) | 让 Codex CLI 从 active plan 继续自主开发的可直接粘贴提示词 |

## 本版核心原则

- 第一版不建设 PostgreSQL，多维表格就是轻量事实库。
- 不把 Wiki 当唯一数据库，Wiki 只做人读的展示层。
- 不做 200 个 Agent，只做一个统一 Agent 后端，靠 `customer_id` 隔离。
- 不让 Agent 直接静默改客户资料，所有写入先形成变更提案。
- 不把复杂业务逻辑塞进 Base workflow，核心逻辑放在统一 Agent 后端。
- 不追求一次性全自动，先把业务人员愿意用的闭环跑通。
- Base 只存结构化事实、证据元数据、处理状态和关键引用，不存大段全文。
- 复杂文档必须先保全原始文件，再异步解析，再生成候选提案，不能假设一次解析成功。

## Codex 快速开发节奏

本计划不再按传统小团队排期估算，而按“Codex 负责快速工程实现，你负责业务验收、飞书授权、真实数据确认”的模式推进。

当前目标分成三层：

```text
2026-07-15 离线纵向 Demo：已完成
可用 MVP：按 08 计划推进，目标 2-4 周
3-5 客户真实试运行：目标 4-6 周，必须经用户批准
```

推荐推进顺序：

1. Sprint 0：先稳定类型边界、仓储契约、迁移和 composition root。
2. Sprint 1：实现 Feishu Base schema validator 与 BaseRepository。
3. Sprint 2：接入真实飞书事件、身份、客户路由和卡片回调。
4. Sprint 3：增加 OpenAI-compatible 结构化抽取，同时保留 DemoExtractor。
5. Sprint 4：生产化“发材料、报进展、问客户”三个核心闭环。
6. Sprint 5：增加 Drive/Wiki、文档任务和 evidence snippets。
7. Sprint 6：增加周报、提醒和经营视图。
8. Sprint 7：补齐权限、部署、监控、备份、恢复并准备 3-5 客户试运行。

详细工作包、Exit Gate、Git 纪律和 Codex 提示词以 `08-Demo后CodexCLI持续开发计划.md` 为准。
