# AGENTS.md

## Mission
本仓库已在提交 `c68d3db` 完成 2026-07-15 离线 Demo。当前最高优先级是按 Demo 后计划，用 Codex CLI 将该纵向切片持续演进为可接入真实飞书、可供 3—5 个客户试运行的轻量 XERP MVP。

后续 Codex 的默认动作是：**读取 active plan → 检查基线 → 实现第一个未完成 P0 工作包 → 测试和修复 → 更新 planning 文件 → 创建本地 checkpoint → 继续**。不要停在重复分析或只给建议。

## Required Reading Order
开始任何实现前按顺序读取：

1. `08-Demo后CodexCLI持续开发计划.md`
2. `.planning/.active_plan` 指向目录中的 `task_plan.md`
3. 同目录 `findings.md`
4. 同目录 `progress.md`
5. 与当前工作包直接相关的 `00`—`06` 产品/领域文档

`07-2026-07-15-CodexCLI自主开发Demo计划.md` 和 `.planning/demo-2026-07-15/` 是已完成历史记录，不再作为当前执行计划，但不得删除。

如果文档冲突，以本文件、`08`、当前 active task plan 为准。

## Codebase Knowledge Graph
本项目使用 codebase-memory-mcp。代码发现优先级：

1. `search_graph`
2. `trace_path`
3. `get_code_snippet`
4. `query_graph`
5. `get_architecture`

如果项目未索引，先使用 `index_repository`。只有搜索字符串/配置/非代码文件，图工具不可用，或图结果不足时，才退回 grep/glob/本地文件搜索；必须在 findings/progress 记录回退原因。

## Autonomous Execution Policy
- 从 active task plan 的第一个未完成 P0 工作包继续，不重新规划已完成内容。
- 每个 Sprint 必须完成 Exit Gate 后才能进入下一 Sprint。
- 外部凭据或管理员授权不可用时，立即用 Port + Fake/Mock + 脱敏 fixture + contract test 继续。
- 未完成真实沙箱验证时，标记 `external validation pending`，不得虚报完成。
- 每完成工作包，更新 task plan、findings（如有新决定）和 progress。
- 每次恢复先做 5-Question Reboot Check：目标、当前工作包、最近完成、测试/阻塞、下一最小动作。
- 失败命令不得原样无限重试；记录错误并改变方法。
- 未经用户明确要求不得 push。

## Non-Negotiable Invariants
- 默认无飞书凭据、无 OpenAI Key、断网时应用仍可启动。
- 永久保留 SQLite、`DemoExtractor`、`FakeFeishuEventGateway`、`/demo` 和 smoke test。
- 每个业务读写必须携带并校验 `customer_id`、`user_id`。
- 真实飞书身份先映射到内部身份，客户端不能自报任意内部用户绕过权限。
- 未确认提案不得写入正式事实。
- 正式写入必须经过 `ProposalEngine` 或等价事务边界。
- 冲突、缺失字段、证据、原始输入、创建人和确认人必须可追溯。
- 事件、卡片回调、确认、外部写入和后台任务必须幂等。
- 原始文件先保全，再解析；解析失败不得伪造成功。
- 默认测试不得调用真实飞书/模型或依赖开发者本机 `.env`。

## Technical Direction
- 应用根目录为 `agent-backend/`，Python 3.12 + FastAPI + uv。
- 采用 Ports/Adapters 小步演进，不做整体重写。
- 应用服务不能直接依赖飞书 SDK、OpenAI SDK 或具体数据库。
- Sprint 0 先类型化端口、拆分仓储、建立 contract tests 和 composition root。
- SQLite 是本地/CI/离线回退；Feishu Base 是真实试运行适配器。
- Wiki 是人读展示层，不是唯一事实库。
- 模型输出只能生成候选提案，不得绕过确认直接写入事实。
- MVP 未出现测量瓶颈前，不引入 PostgreSQL、Redis、Kafka、Temporal、RAGFlow、向量数据库或独立前端重写。

## Configuration and Secrets
- 配置从环境变量或未提交的 `.env` 读取。
- `.env.example` 只能含占位符。
- 真实密钥不得出现在源码、测试、日志、Markdown、截图、commit 或聊天输出中。
- OpenAI-compatible 配置使用 `OPENAI_API_KEY`、`OPENAI_BASE_URL`、`OPENAI_MODEL`；Provider 必须独立于应用服务。
- 飞书和模型真实集成必须显式启用；默认全部指向离线安全适配器。

## Test Gates
每个 Sprint Exit Gate 至少运行：

```bash
cd agent-backend
uv sync
uv run ruff check .
uv run pytest
uv run python scripts/smoke_demo.py
```

先运行工作包相关测试，再运行完整 Gate。不得通过删除权限、幂等、确认或审计逻辑让测试变绿。

## Git Safety
开始任务前运行：

```bash
git status --short --branch
git log -5 --oneline
```

- 不覆盖用户未提交修改。
- 不使用 `git reset --hard`、强制 push、历史重写或删除用户分支。
- 一个工作包形成 1—3 个小提交；Sprint Exit Gate 后记录 checkpoint SHA。
- 除非用户明确要求，否则只创建本地提交，不 push。

## Stop / Escalate
仅在以下硬阻塞停止并向用户说明：

- 将修改/删除真实 Base、Wiki、Drive 数据或生产权限。
- 将向真实客户发送消息、周报或提醒。
- 需要管理员审批、真实密钥、部署账户或付费资源。
- 怀疑密钥泄漏、越权或跨客户数据泄漏。
- 数据迁移可能不可逆。
- 用户改动冲突且无法安全隔离。
- 三种合理方案后仍不能推进。
- 重大产品歧义会造成不可逆数据模型或外部副作用。

停止报告必须包含：已完成、准确失败、已尝试方案、风险、最小所需批准/信息、仍可继续的无阻塞工作。
