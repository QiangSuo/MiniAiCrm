# Task Plan: XERP Post-Demo MVP

## Goal
在永久保留 `c68d3db` 离线 Demo 回归路径的前提下，由 Codex CLI 按 Sprint 自主把 XERP 纵向切片演进为可接入真实飞书、可供 3—5 个客户试运行的轻量 MVP。

## Baseline
- Branch: `main`
- Baseline commit: `c68d3db feat: complete offline XERP demo vertical slice`
- Baseline validation: `ruff` pass, `pytest` 18 passed, `smoke_demo` pass
- Application root: `agent-backend/`

## Current Sprint
Sprint 0 — Production foundation and typed boundaries

## Current Work Package
S0-01 — 冻结现有行为并建立仓储契约测试

## Source of Truth
1. `AGENTS.md`
2. `08-Demo后CodexCLI持续开发计划.md`
3. 本文件
4. `findings.md`
5. `progress.md`
6. `00`—`06` 产品/领域规划
7. `07` 和 `.planning/demo-2026-07-15/` 仅作为已完成 Demo 历史记录

## Global Invariants
- [ ] 默认无密钥、断网时应用仍可启动和运行离线 Demo
- [ ] SQLite、`DemoExtractor`、`FakeFeishuEventGateway`、`/demo`、smoke test 永久保留
- [ ] 每个业务读写校验 `customer_id` + `user_id`
- [ ] 未确认提案不得写入正式事实
- [ ] 外部事件、回调、任务和确认必须幂等
- [ ] 默认测试不得调用真实飞书或模型
- [ ] 不提交密钥，不 push，不使用危险 Git 命令

## Sprint 0 — Production foundation and typed boundaries

### P0
- [ ] **S0-01** 建立 SQLite 仓储 contract tests，覆盖权限、提案、冲突、确认幂等、快照、看板、审计
- [ ] **S0-02** 将 `DemoRepository` 泛化/拆分为稳定类型化端口，消除应用服务中的任意结构 `dict[str, Any]`
- [ ] **S0-03** 按 schema/migration、seed、proposal、facts、query、audit 拆分 `SQLiteDemoRepository`
- [ ] **S0-04** 建立 composition root/provider selection，默认装配仍为 SQLite + Fake Feishu + DemoExtractor
- [ ] **S0-05** 增加配置校验、SQLite migration/version，固定 Demo ID/日期只留在 seed/fixture

### P1
- [ ] 统一外部错误类型、correlation ID 和结构化日志上下文
- [ ] 在受控升级和完整回归后消除 Starlette/httpx warning

### Exit Gate
- [ ] `uv sync`
- [ ] `uv run ruff check .`
- [ ] `uv run pytest`
- [ ] `uv run python scripts/smoke_demo.py`
- [ ] 原有 18 个测试与新增 contract tests 全绿
- [ ] 核心服务不再依赖 `DemoRepository` 名称或任意结构返回值
- [ ] 迁移可在空库和已有 Demo 库重复执行
- [ ] 创建本地 Sprint 0 checkpoint，并在 `progress.md` 记录 SHA

**Status:** in_progress

## Sprint 1 — Feishu Base schema and BaseRepository

### P0
- [ ] **S1-01** 定义版本化 Base 表/字段映射
- [ ] **S1-02** 实现 token、timeout、retry、pagination、error mapping 的 Feishu API client
- [ ] **S1-03** 实现非破坏性 Base schema validator
- [ ] **S1-04** 实现 BaseRepository，分离业务 ID 与 `record_id`
- [ ] **S1-05** SQLite/Base 共享 contract suite，增加显式 adapter switch 和 shadow validation

### Exit Gate
- [ ] SQLite 与 Base Fake 通过同一 contract suite
- [ ] 无凭据时默认离线测试全绿
- [ ] 有凭据时 sandbox 可完成提案创建、确认、快照查询
- [ ] 完成抽样对账；外部未验证时明确标记 pending

**Status:** pending

## Sprint 2 — Real Feishu events, identity, and routing

### P0
- [ ] **S2-01** challenge、签名/加密验证
- [ ] **S2-02** event receipt、状态与幂等重放
- [ ] **S2-03** tenant/open_id 到内部用户映射
- [ ] **S2-04** `chat_id → customer_id` 路由与歧义处理
- [ ] **S2-05** 文本、文件、确认/拒绝卡片回调和真实回复

### Exit Gate
- [ ] 脱敏 fixture 覆盖安全、重复和失败路径
- [ ] Fake Gateway 回归全绿
- [ ] 有 sandbox 时完成“报进展→卡片→确认→事实更新”
- [ ] 无 sandbox 时标记 external validation pending

**Status:** pending

## Sprint 3 — OpenAI-compatible structured extraction

### P0
- [ ] **S3-01** 严格结构化输出模型
- [ ] **S3-02** OpenAI-compatible Provider、timeout/retry/fallback
- [ ] **S3-03** prompt version、PII 最小化、耗时和成本日志
- [ ] **S3-04** 脱敏中文评估夹具和 FakeModelClient
- [ ] **S3-05** `demo|openai` 显式切换和 health 状态

### Exit Gate
- [ ] DemoExtractor 回归全绿
- [ ] Fake provider 覆盖成功、schema 错误、timeout、rate limit、fallback
- [ ] 真实调用只通过 opt-in integration test
- [ ] 模型结果始终先进入提案

**Status:** pending

## Sprint 4 — Productionize three core loops

### P0
- [ ] **S4-01** 通用进展抽取、字段级冲突、编辑/拒绝/补充
- [ ] **S4-02** 真实材料元数据和准确处理状态
- [ ] **S4-03** 基于权限内已确认事实和证据的问答
- [ ] **S4-04** 提案、错误、权限和未绑定客户卡片
- [ ] **S4-05** fixture e2e 与真实 sandbox 验收脚本

### Exit Gate
- [ ] sandbox 完成材料、进展、确认、问答、权限拒绝、重复事件幂等
- [ ] 无凭据时 fixture/Mock/Fake 全覆盖且不虚报真实完成
- [ ] `/demo` 和 smoke 永久回归全绿

**Status:** pending

## Sprint 5 — Drive, Wiki, and document processing

### P0
- [ ] **S5-01** Local/Feishu Drive FileStore 与原件保全
- [ ] **S5-02** DocumentProcessingTask 状态机、重试、dead letter
- [ ] **S5-03** 第一批文本 PDF、DOCX、TXT/Markdown 解析
- [ ] **S5-04** 可追踪 evidence snippets
- [ ] **S5-05** 只发布已确认事实的 Wiki 展示

### Exit Gate
- [ ] 支持文档可生成原件、任务、片段和候选提案
- [ ] 失败可重试/人工恢复，重复事件不重复生成
- [ ] 无 Drive/Wiki 凭据时本地 Fake 完整测试

**Status:** pending

## Sprint 6 — Reports, reminders, and dashboard

### P0
- [ ] **S6-01** Scheduler port、job run 和幂等时间窗
- [ ] **S6-02** 可追溯客户周报草稿
- [ ] **S6-03** 逾期、高风险、无进展、覆盖不足提醒
- [ ] **S6-04** 指标定义和经营视图
- [ ] **S6-05** Messaging 发送、审计、失败和重试

### Exit Gate
- [ ] 三个客户可生成可追溯周报草稿
- [ ] 规则测试确定且相同时间窗不重复发送
- [ ] 本地 Fake 与真实沙箱有独立验收路径

**Status:** pending

## Sprint 7 — Security, operations, and pilot

### P0
- [ ] **S7-01** RBAC、tenant/customer 隔离和越权测试
- [ ] **S7-02** 生产密钥注入、轮换和泄漏防护
- [ ] **S7-03** 日志、指标、readiness/liveness 和告警
- [ ] **S7-04** Docker/部署、备份、恢复和回滚演练
- [ ] **S7-05** timeout/retry/rate limit/dead letter 可靠性边界
- [ ] **S7-06** 3—5 客户数据、权限、培训和巡检准备

### Exit Gate
- [ ] 越权、恢复、故障和回滚演练通过
- [ ] 客户数据和权限抽样核对
- [ ] Runbook、指标和告警可操作
- [ ] 用户明确批准后才开始真实试运行

**Status:** pending

## Stop / Escalate
Codex 仅在以下情况停止并请求用户：
- 将修改/删除真实 Base、Wiki、Drive 或生产权限
- 将向真实客户发送消息/报告/提醒
- 需要管理员批准、真实密钥、付费资源或部署账户
- 怀疑密钥泄漏、越权或跨客户数据泄漏
- 数据迁移可能不可逆
- 用户未提交修改与任务冲突且无法安全隔离
- 三种合理方案后仍无法推进
- 产品歧义会造成不可逆数据模型或外部副作用

## Next Action
执行 S0-01：先运行基线 Gate，再为当前 SQLite 行为建立仓储 contract tests。不要从真实飞书或模型接入开始。
