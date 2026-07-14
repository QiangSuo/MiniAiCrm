# AGENTS.md

## Mission
本仓库的当前最高优先级是在 **2026-07-15 Demo 前**，用 Codex CLI 自主实现一个可本地运行、可重复演示的 XERP 客户情报平台纵向切片。

不要把本次任务理解为一次架构讨论或继续写规划文档。后续 Codex 的默认动作是：**读取计划 → 实现代码 → 运行测试 → 修复问题 → 更新进度 → 继续下一阶段**。

## Required Reading Order
开始任何实现前必须按顺序读取：

1. `07-2026-07-15-CodexCLI自主开发Demo计划.md`
2. `.planning/demo-2026-07-15/task_plan.md`
3. `.planning/demo-2026-07-15/findings.md`
4. `.planning/demo-2026-07-15/progress.md`
5. 与当前任务直接相关的原有 `00`—`06` 文档

如果文档发生冲突，以前四项为准；原有路线只提供领域口径，不能用来扩大明日 Demo 范围。

## Codebase Knowledge Graph
本项目使用 codebase-memory-mcp 维护代码知识图谱。代码发现必须优先使用 MCP 图工具，而不是 grep/glob/file-search。

优先级：

1. `search_graph`
2. `trace_path`
3. `get_code_snippet`
4. `query_graph`
5. `get_architecture`

如果项目未索引，先运行 `index_repository`。只有搜索字符串、配置和非代码文件，或图工具结果不足时，才退回 grep/glob。

## Autonomous Execution Policy
- 不要停在“建议”“方案”“下一步可以……”；直接实施下一个未完成 Phase。
- 除非出现无法本地替代的硬阻塞，不要向用户提问。
- 飞书凭据、管理员授权、网络 API 不可用时，立即使用本地 Adapter/Fake，不等待。
- 每个 Phase 必须完成其 Exit Gate 后才能进入下一 Phase。
- 每完成一个 Phase，更新 `task_plan.md` 的状态和 `progress.md` 的动作、文件、测试结果。
- 每次上下文恢复，先做 5-Question Reboot Check，再继续第一个未完成任务。
- 失败命令不得原样无限重试；记录错误，改变方法。
- 优先保持应用可启动、测试可过、Demo 可重复；不得为“未来扩展”牺牲明日交付。

## Demo Scope Guard
### P0
- Python 3.12 + FastAPI + uv
- SQLite 本地事实库
- 单页 `/demo` 控制台
- 发材料、报进展、问客户
- 变更提案确认后写入
- 权限拒绝、证据引用、审计记录
- 经营概览、Demo 重置、测试、smoke script、Runbook

### P1 only after all P0 gates pass
- 最小真实飞书适配
- OpenAI 结构化抽取提供者
- Dockerfile
- 更丰富的周报卡片

### Explicitly out of scope for 2026-07-15
- PostgreSQL、Redis、Kafka、Temporal、RAGFlow、向量数据库
- OCR 和复杂 PDF/PPT/Excel 解析
- Wiki 自动建页、云盘下载、12 张 Base 表全量同步
- 生产部署、完整 RBAC/SSO、多租户、200 客户迁移
- 独立 React/Vue 前端工程

## Technical Decisions
- 使用 `agent-backend/` 作为应用根目录。
- 使用 uv 固定 Python 3.12；不要依赖系统默认 Python 3.9。
- Demo 默认不能依赖任何密钥、外网或运行时大模型。
- 采用端口/适配器边界：本地 SQLite 为默认实现，Feishu Base 为可选实现。
- 默认使用确定性 `DemoExtractor`，保证固定样例稳定；模型提供者只做可选增强。
- 正式写入必须经过 ProposalEngine 和确认动作。
- 每个业务请求必须带 `customer_id`、`user_id`。
- 使用应用服务封装业务事务，不允许路由直接拼接数据库写入。
- Demo Console 使用服务端静态 HTML/CSS/JS，不建立额外 Node 构建链。

## Optional LLM API Configuration
项目已经约定通过 OpenAI 兼容接口调用可选的大模型能力。实现模型 Provider 时必须遵守：

- 从项目根目录的 `.env` 或进程环境变量读取配置，禁止在源码、测试、日志、文档或示例数据中写入真实 Key。
- 使用以下统一变量名：
  - `OPENAI_API_KEY`：API 密钥。
  - `OPENAI_BASE_URL`：OpenAI 兼容接口地址；当前本地配置使用 `https://api.xairouter.com/v1`。
  - `OPENAI_MODEL`：模型名称；当前本地配置使用 `gpt-5.5`。
- Python 调用优先使用 OpenAI SDK，并显式传入 `api_key`、`base_url` 和 `model`：

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    base_url=os.environ["OPENAI_BASE_URL"],
)

response = client.chat.completions.create(
    model=os.environ["OPENAI_MODEL"],
    messages=[{"role": "user", "content": "你好"}],
)
```

- 应用启动时如果未配置 Key，必须自动回退到 `DemoExtractor`，不得影响无密钥 Demo。
- API 调用应放在独立 Provider/Adapter 中，业务服务不得直接依赖 OpenAI SDK。
- 测试必须 Mock/Fake 模型 Provider，不得真实消耗 API。
- `.env`、`.env.*` 必须保持 Git 忽略；可提交的配置说明只写入 `.env.example`，其中只能使用占位符。
- `OPENAI_BASE_URL` 指向第三方兼容服务时，请求内容会经过该服务；不得发送不必要的客户敏感信息。

## Required Public Behaviors
实现应至少暴露等价行为（路径可微调，但 README 和 smoke test 必须一致）：

- `GET /health`
- `GET /demo`
- `POST /api/demo/reset`
- `POST /api/intake/material`
- `POST /api/intake/progress`
- `POST /api/proposals/{proposal_id}/confirm`
- `POST /api/questions`
- `GET /api/customers/{customer_id}/snapshot`
- `GET /api/dashboard`

## Testing Rules
- 优先在最高可观察边界测试外部行为，API 测试优于实现细节测试。
- 每实现一个闭环，立即运行对应测试，不等到最后。
- 最终至少运行：
  - `uv run ruff check .`
  - `uv run pytest`
  - `uv run python scripts/smoke_demo.py`
- 测试不得依赖外网、真实飞书或 OpenAI API。
- 必测：确认前不写正式表、确认后事务更新、跨客户/未授权访问拒绝、冲突不静默覆盖、问答含来源与缺失信息、重置可重复。

## Git Safety
- 不得 push。
- 不得 force push、reset --hard、clean -fd 或重写历史。
- 不得删除原有规划文档。
- 可以在所有 P0 Gate 通过后创建本地 checkpoint commit；提交信息应明确说明 Demo 状态。
- 保留用户已有改动，不得为了方便还原非本次创建的内容。

## Definition of Done
只有在以下条件全部满足时才能宣布完成：

1. `.planning/demo-2026-07-15/task_plan.md` 的 Phase 1—5 均为 complete。
2. P0 Acceptance Criteria 全部通过并记录到 `progress.md`。
3. `scripts/run_demo.sh` 可启动应用，`scripts/smoke_demo.py` 可重复通过。
4. Demo Runbook 按顺序完成两次彩排。
5. 无密钥、无网络条件下仍能演示核心路径。
6. 已知限制和 P1 项清楚记录，不把未实现能力表述为已完成。
