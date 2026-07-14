# Task Plan: XERP 2026-07-15 Demo

## Goal
在 2026-07-15 Demo 前，由 Codex CLI 自主实现并验证一个本地可运行的 XERP 客户情报平台纵向切片，稳定演示“发材料、报进展、问客户、确认写入、经营概览”五个动作；没有飞书凭据时仍可完整演示，有凭据时可追加真实飞书适配。

## Current Phase
Phase 5 — complete

## Source of Truth
1. `AGENTS.md`
2. `07-2026-07-15-CodexCLI自主开发Demo计划.md`
3. 本文件
4. `findings.md`
5. `progress.md`
6. 原有 `00`—`06` 规划文档（用于领域口径，不得扩大明日 Demo 范围）

## Phases

### Phase 0: 计划与环境确认
- [x] 识别仓库当前只有规划文档、没有应用代码
- [x] 确认 Codex CLI、Python 3.12、uv、Node、Docker 可用
- [x] 确定 Demo 使用本地优先、外部适配器可插拔的策略
- [x] 写入 Codex CLI 自主执行入口、范围和验收标准
- **Status:** complete

### Phase 1: 工程骨架与可启动服务
- [x] 创建 `agent-backend/` Python 3.12 + FastAPI + uv 工程
- [x] 建立配置、结构化日志、领域模型、应用服务、仓储接口
- [x] 实现 SQLite DemoRepository 与种子数据
- [x] 实现 `/health`、`/demo`、`/api/demo/reset`
- [x] 添加最小单元测试并通过
- **Status:** complete
- **Exit Gate:** 全新环境执行 `uv sync && uv run pytest` 成功，`/health` 返回 200，`/demo` 可打开

### Phase 2: 三个核心闭环
- [x] “发材料”生成资料归档提案，确认后写入资料证据
- [x] “报进展”生成接触、商机、行动提案，展示冲突并确认写入
- [x] “问客户”基于当前客户数据回答，区分事实、推断、建议并附来源
- [x] 所有读写带 `customer_id`、`user_id` 并经过 PermissionGuard
- [x] 所有正式写入通过 ProposalEngine，禁止静默直写
- **Status:** complete
- **Exit Gate:** 三个闭环 API 测试全部通过；未授权用户返回 403；确认前正式表不变化，确认后事务性更新

### Phase 3: Demo 控制台与经营概览
- [x] 制作单页 Demo Console，不引入独立前端构建链
- [x] 支持选择预设场景、提交、查看提案、确认、查看问答和来源
- [x] 实现经营概览：客户、活跃商机、金额、逾期行动、高风险、待确认提案
- [x] 实现周报预览或经营摘要，作为阶段四能力的视觉占位
- [x] 增加一键重置 Demo 数据
- **Status:** complete
- **Exit Gate:** 浏览器内按既定脚本可在 5 分钟内无命令行改数据完成全流程

### Phase 4: 稳定性、脚本与可选飞书适配
- [x] 添加 `scripts/bootstrap.sh`、`scripts/run_demo.sh`、`scripts/smoke_demo.py`
- [x] 增加 webhook replay 端点或 FeishuEventGateway 假实现
- [x] 若真实飞书凭据齐全且核心 Gate 已通过，再实现最小真实事件/回复适配（P0 使用 Fake，未扩大到 P1）
- [x] 外部模型不可用时自动使用确定性 DemoExtractor，不阻断 Demo
- [x] 完成错误提示、审计日志、README、`.env.example`
- **Status:** complete
- **Exit Gate:** 断网且无密钥时 smoke test 通过；外部凭据缺失不会导致应用启动失败

### Phase 5: 最终验收与交付
- [x] 运行格式检查、静态检查、完整测试和 smoke test
- [x] 按 Demo Runbook 完整彩排至少两次
- [x] 记录已知限制、回退方案和现场操作顺序
- [x] 更新 `progress.md`、测试结果和最终状态
- [x] 生成本地 checkpoint commit；禁止 push
- **Status:** complete
- **Exit Gate:** 所有 P0 验收项通过，无未解释的测试失败，Demo 从重置到结束可重复执行

## P0 Acceptance Criteria
1. `uv run pytest` 全绿。
2. `uv run python scripts/smoke_demo.py` 全绿。
3. `uv run uvicorn app.main:app --host 127.0.0.1 --port 8000` 可启动。
4. `http://127.0.0.1:8000/demo` 可完成报进展→提案→确认→问客户。
5. 发材料可生成提案并在确认后出现资料证据。
6. 未授权用户无法读取客户数据。
7. 回答展示数据截止时间、事实、推断、建议、来源、缺失信息。
8. 无 `FEISHU_*`、`OPENAI_API_KEY` 时仍能完整演示。
9. Demo 数据可一键重置，重复演示结果稳定。
10. 没有 PostgreSQL、RAGFlow、Kafka、Temporal、独立前端工程等非必要依赖。

## Key Questions
1. 没有飞书凭据时能否完成完整 Demo？——能，默认走本地 DemoAdapter；真实飞书为可选加分项。
2. 明日是否需要复杂文档解析？——不需要；只演示原始资料登记、摘要占位、提案确认和可追溯性。
3. 是否依赖运行时大模型？——不依赖；默认确定性抽取，配置密钥后可切换模型提供者。
4. 是否需要生产部署？——不需要；明日以本机可重复运行和稳定演示为准。
5. 是否需要覆盖全部 12 张 Base 表？——不需要；仅实现 Demo 闭环所需核心实体，保留接口边界。

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| Python 3.12 + FastAPI + uv | 与原计划一致，适合 AI/文档场景，本机已具备 Python 3.12 和 uv |
| SQLite 作为 Demo 默认事实库 | 无外部依赖、可事务写入、可重置，明日最稳 |
| Repository/Adapter 隔离本地与飞书 | Demo 不被凭据阻塞，后续可替换为 BaseRepository |
| 单页静态 Demo Console | 降低前端构建和调试成本，同时保证视觉演示 |
| 确定性 DemoExtractor 为默认 | 避免 API、网络和模型输出波动导致现场失败 |
| 真实飞书接入是 P1，不是 P0 | 飞书授权和事件订阅依赖人工及外部环境，不应阻塞明日 Demo |
| 所有正式写入必须经过提案确认 | 保留产品最关键的安全与审计原则 |
| 不做复杂文件解析 | 明日只需要证明闭环，不需要证明 OCR/RAG 能力 |

## Scope Guard
### P0 必须做
- 本地 API、SQLite、Demo Console
- 发材料、报进展、问客户
- 提案确认、权限拒绝、证据引用
- 经营概览、重置、测试、Runbook

### P1 有余力再做
- 最小真实飞书消息接入
- OpenAI 结构化抽取提供者
- 周报卡片预览
- Dockerfile

### 明日明确不做
- 生产级飞书 Base 全量 12 表同步
- Wiki 自动建页与云盘文件下载
- OCR、PPT/Excel 深度解析、向量检索
- PostgreSQL、Redis、消息队列、Temporal
- 多租户、完整 RBAC、SSO、正式部署
- 200 客户迁移与真实数据治理

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| `codex doctor` provider route probe 超时 | 1 | 开工前再次运行；若 Codex 会话本身可用则继续，运行时产品不依赖外部模型 |
| 恢复会话时从 `agent-backend/` 追加根目录进度文件失败 | 1 | 切回仓库根目录写入；测试命令仍在正确目录成功执行 |
| Playwright CLI 使用了不存在的 `select-option` 命令 | 1 | 根据 CLI 输出改用 `select <target> <value>`，不重复失败命令 |
| Phase 4 首次路由生成遗漏 `FeishuReplayEvent` import | 1 | 读取实际 routes import 形式并改为显式多行导入 |
| health 新增 provider 状态后旧测试严格字典断言失败 | 1 | 更新公共 health 契约期望，保留新增字段的显式验证 |
| `uv run python scripts/smoke_demo.py` 无法导入 `app` | 1 | 在脚本启动时显式加入项目根目录，保持用户要求的直接执行命令 |
| Smoke 修复导入后 Ruff 检出 import 顺序 | 1 | 使用 Ruff 自动整理 import block |
| Smoke 使用了错误的 dashboard 金额字段名 | 1 | 依据公共 dashboard 测试改为 `total_amount_cny` |

## Notes
- Codex 每完成一个 Phase，必须立即更新本文件和 `progress.md`。
- 遇到外部凭据、网络、飞书管理员权限等阻塞时，切换本地适配器继续，不等待。
- 不得用“完善架构”为理由扩大范围；优先保持可启动、可测试、可演示。
- 不得 push，不得重写 Git 历史，不得删除原有规划文档。
