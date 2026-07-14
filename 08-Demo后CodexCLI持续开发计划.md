# Demo 后 Codex CLI 持续开发计划

> 计划起点：2026-07-16（2026-07-15 Demo 完成后）  
> 当前代码基线：`c68d3db feat: complete offline XERP demo vertical slice`  
> 应用根目录：`agent-backend/`  
> 执行方式：Codex CLI 按 Sprint 和 Exit Gate 自主实现、测试、修复、记录和提交本地 checkpoint  
> 目标：保留离线 Demo 的同时，逐步把当前纵向切片升级为可接入真实飞书、可供 3—5 个客户试运行的轻量 XERP MVP

---

## 1. 本计划解决什么问题

2026-07-15 Demo 已经由提交 `c68d3db` 完成。后续开发不再从零搭建，也不能继续把 Demo 计划当作当前任务。Codex 必须从**已提交、已测试、可离线运行的真实代码**继续演进，通过替换适配器和补齐生产能力，把以下链路逐步落地：

```text
飞书消息 / 文件 / 卡片
        ↓
身份与客户上下文路由
        ↓
统一应用服务与 ProposalEngine
        ↓
结构化抽取 / 问答 / 文档处理 / 报告提醒
        ↓
SQLite 离线适配器 + 飞书 Base 真实适配器
        ↓
审计、权限、监控、备份与试运行治理
```

本计划同时解决四个执行问题：

1. Codex 每次重新进入仓库时知道从哪个任务继续，而不是重新分析整套系统。
2. 外部凭据未准备好时仍能在本地完成绝大多数开发和测试。
3. 每个 Sprint 都有明确 P0、Exit Gate、测试命令和 Git checkpoint。
4. 任何真实集成都不能破坏 `c68d3db` 已建立的离线 Demo 回退路径。

---

## 2. 已完成基线：不要重复实现

### 2.1 已提交能力

当前 `agent-backend/` 已经具备：

- Python 3.12、FastAPI、uv、SQLite 工程骨架。
- 单页静态 `/demo` 控制台。
- “发材料、报进展、问客户”三个本地闭环。
- 变更提案创建、冲突展示、确认后事务性写入。
- `customer_id` + `user_id` 权限检查。
- 客户快照、经营概览、审计记录和 Demo 重置。
- 确定性 `DemoExtractor`。
- `FakeFeishuEventGateway` 本地事件重放。
- bootstrap、run、smoke、Demo Runbook 和已知限制文档。

### 2.2 当前公开端点

```text
GET  /health
GET  /demo
POST /api/demo/reset
POST /api/intake/material
POST /api/intake/progress
POST /api/proposals/{id}/confirm
POST /api/questions
GET  /api/customers/{id}/snapshot
GET  /api/dashboard
POST /api/integrations/feishu/replay
```

### 2.3 已验证质量基线

在 `agent-backend/` 下已经验证：

```bash
uv run ruff check .
uv run pytest
uv run python scripts/smoke_demo.py
```

当前结果：

```text
ruff: pass
pytest: 18 passed
smoke_demo: pass
```

Starlette/httpx 有一个不影响功能的弃用 warning。除非依赖升级是当前任务的一部分，否则不要为了消除该 warning 擅自扩大依赖升级范围。

### 2.4 已完成能力的保护规则

后续所有 Sprint 都必须满足：

- 默认无飞书凭据、无 OpenAI Key、断网时，应用仍可启动。
- `DemoExtractor`、`FakeFeishuEventGateway` 和 SQLite 本地路径作为回归适配器保留。
- `/demo` 和 `scripts/smoke_demo.py` 不得失效。
- 旧 API 如需变更，先提供兼容层和迁移说明，不得直接破坏。
- 新增真实适配器必须通过配置显式启用，禁止“配置了一半就启动失败”。

---

## 3. 当前明确未实现的能力

Codex 不得把下面内容描述成“已完成”：

1. `SQLiteDemoRepository` 仍同时承担建表、种子、权限、提案、冲突、正式写入、快照、看板和审计，尚未拆分。
2. 仓储端口仍叫 `DemoRepository`，并大量返回 `dict[str, Any]`，尚未形成稳定类型边界。
3. 固定 Demo 客户、用户、中文样例、日期和推荐仍存在于运行路径中。
4. 尚无真实飞书 Base Repository，也没有完整 Base Schema 校验与同步。
5. 尚无真实飞书事件签名/加密校验、事件幂等、身份映射、群聊路由、机器人回复和卡片回调。
6. `select_progress_extractor()` 即使存在 OpenAI 配置也仍选择 `DemoExtractor`。
7. 问答仍是固定模板，不是生产模型加结构化事实检索流程。
8. 材料只登记文件名和说明，不保存文件字节，不下载飞书文件，不解析、OCR 或建立证据片段。
9. SQLite 当前仅有 customers、permissions、proposals、materials、contacts、opportunities、actions、risks、audit_logs 等 Demo 表，并非完整 Base 设计。
10. 尚无任务调度、周报、提醒、正式部署、监控、备份、数据库迁移、重试策略、限流和生产密钥管理。
11. 尚未完成真实客户数据导入、数据质量验收和 3—5 客户试运行。

---

## 4. 后续目标、边界与里程碑

### 4.1 一句话目标

```text
先把离线纵向切片变成可替换、可测试的工程边界，
再逐个接通飞书 Base、飞书事件、模型抽取和文档处理，
最后补齐报告提醒、权限运维和 3—5 客户试运行。
```

### 4.2 推荐里程碑

| 里程碑 | 推荐范围 | 完成标志 |
| --- | --- | --- |
| M1 工程化基座 | Sprint 0 | 端口类型化、仓储拆分、迁移和配置选择完成，离线回归全绿 |
| M2 真实数据底座 | Sprint 1 | SQLite 与 Base 通过同一仓储契约测试，Base Schema 可校验 |
| M3 真实飞书闭环 | Sprint 2—4 | 飞书沙箱中完成消息/文件→提案→卡片确认→正式事实→问答 |
| M4 文档与经营自动化 | Sprint 5—6 | 支持文档任务、证据片段、周报、提醒和经营视图 |
| M5 试运行就绪 | Sprint 7 | 安全、部署、监控、备份、Runbook 和试运行清单通过 |

### 4.3 推荐时间盒

以下时间只用于防止任务无限膨胀，不是承诺：

```text
Sprint 0：1—2 天
Sprint 1：2—4 天
Sprint 2：2—4 天
Sprint 3：1—3 天
Sprint 4：2—4 天
Sprint 5：3—5 天
Sprint 6：2—4 天
Sprint 7：3—5 天，随后进入 3—5 客户试运行
```

在 Codex CLI 高速实现模式下，可用 MVP 目标仍按 2—4 周管理，真实客户试运行按 4—6 周管理。不得以赶时间为由跳过 Exit Gate。

### 4.4 本阶段明确不优先

除非有实际瓶颈证据或用户明确要求，后续 MVP 期间不优先引入：

- PostgreSQL、Redis、Kafka、Temporal。
- RAGFlow 或独立向量数据库。
- 独立 React/Vue 前端重写。
- 200 客户全量迁移。
- 通用“万能 Agent 平台”。
- 一次支持所有 PDF/PPT/Excel/OCR 场景。

---

## 5. 不可破坏的业务与工程约束

以下规则优先于单个 Sprint 的实现便利：

### 5.1 业务不变量

1. 每个业务读写必须携带并校验 `customer_id` 和 `user_id`；真实飞书身份必须先映射为内部身份。
2. 未确认的提案不得写入正式客户事实。
3. 正式写入必须经过 `ProposalEngine` 或等价的应用服务事务边界。
4. 冲突、缺失字段、证据来源和原始输入必须可追溯。
5. 问答必须区分：已确认事实、单一来源线索、推断、建议、来源和缺失信息。
6. 客户之间必须数据隔离；任何“默认取第一个客户”的实现都不允许进入真实适配器。
7. 重放事件、重复回调和重复确认不得造成重复正式事实。
8. 原始文件先保全，再解析；解析失败不得丢失原文件或伪造成功状态。

### 5.2 工程不变量

1. 应用服务依赖 Port/Protocol，不直接依赖飞书 SDK、OpenAI SDK 或具体数据库实现。
2. 外部 API 统一放在 Infrastructure Adapter 中，必须有 timeout、错误映射、重试边界和可替换 Fake。
3. 单元测试和默认完整测试不得调用真实外部 API 或消耗真实模型额度。
4. 配置、密钥和 token 不得写入源码、测试、日志、Markdown、Git 历史或截图。
5. 所有新表/字段变更必须可迁移、可重复执行、可回滚或至少有恢复说明。
6. 所有后台任务和外部事件都必须有幂等键。
7. 失败必须显式记录，禁止吞掉异常后返回“成功”。
8. 每个任务尽量形成小提交，避免一次跨越多个 Sprint 的大改。

---

## 6. 目标架构

### 6.1 推荐模块边界

在不进行无价值重写的前提下，将当前代码逐步演进为：

```text
agent-backend/app/
├── api/                       # HTTP/webhook/card callback 边界
├── application/               # 用例、事务、权限、提案、问答、任务编排
├── domain/                    # 领域模型、值对象、枚举、错误和不变量
├── ports/
│   ├── repositories.py        # Customer/Proposal/Material/Audit 等稳定端口
│   ├── extractor.py           # 结构化抽取端口
│   ├── messaging.py           # 消息回复与卡片端口
│   ├── file_store.py          # 原始文件保存/读取端口
│   ├── document_processor.py  # 文档解析端口
│   ├── scheduler.py           # 调度端口
│   └── identity.py            # 飞书身份与内部身份映射端口
├── infrastructure/
│   ├── sqlite/                # 本地仓储、迁移和 Demo seed
│   ├── feishu/
│   │   ├── client.py          # token、HTTP、分页、重试和错误映射
│   │   ├── base_repository.py
│   │   ├── event_gateway.py
│   │   ├── messaging.py
│   │   ├── drive.py
│   │   └── wiki.py
│   ├── llm/                   # OpenAI-compatible provider、prompt/version/eval
│   ├── documents/             # L1/L2 解析器、片段与处理任务
│   └── scheduler/             # 本地/部署环境调度实现
├── composition.py             # 唯一依赖装配入口
├── config.py
└── main.py
```

目录名可根据现有代码小步调整；不要只为匹配目录树做大规模搬家。优先保证依赖方向和测试边界正确。

### 6.2 数据存储策略

MVP 阶段采用双适配器：

```text
本地/CI/离线 Demo：SQLite
真实试运行：Feishu Base
原始文件：飞书 Drive 或可配置 FileStore
Wiki：人读展示层，不作为唯一事实库
```

业务主键和飞书 `record_id` 必须分离。建议所有正式实体保留：

- 内部业务 ID。
- `customer_id`。
- 外部系统和外部记录 ID。
- 来源类型、来源 ID、证据引用。
- 版本号或 `updated_at`。
- 创建人、确认人和审计时间。

### 6.3 适配器切换原则

配置至少支持：

```text
XERP_REPOSITORY=sqlite|feishu_base
XERP_FEISHU_GATEWAY=fake|real
XERP_EXTRACTOR=demo|openai
XERP_FILE_STORE=local|feishu_drive
XERP_SCHEDULER=disabled|local|external
```

配置命名可以在 Sprint 0 最终确定，但必须满足：

- 默认值全部指向离线安全实现。
- 真实适配器缺少配置时给出可操作错误，不影响离线模式。
- `/health` 能展示启用的适配器，但不得泄露密钥。

---

## 7. Codex CLI 自主执行总规则

### 7.1 执行顺序

Codex 每次运行必须：

1. 读取 `AGENTS.md`、本文件和当前 `.planning` 目录。
2. 查看 `git status --short --branch` 和最近提交，确认没有覆盖用户改动。
3. 优先使用 codebase-memory-mcp 搜索代码；图工具不可用时记录原因，再使用本地搜索。
4. 运行当前基线 Gate，确认不是从红灯状态开始。
5. 从当前 Sprint 第一个未完成的 P0 工作包开始。
6. 先写或更新测试，再完成最小实现。
7. 运行任务级测试，再运行 Sprint 级 Gate。
8. 更新 `task_plan.md`、`findings.md`、`progress.md`。
9. 形成小型本地 checkpoint commit；未经用户明确要求不得 push。
10. Exit Gate 全绿后才能进入下一个 Sprint。

### 7.2 每个工作包的统一完成定义

一个工作包只有同时满足以下条件才可标记完成：

- 代码或文档已写入仓库。
- 正常路径、权限/错误路径和幂等路径至少有对应测试。
- 现有 18 个基线测试和 smoke test 未被破坏。
- 外部凭据缺失时有 Fake/fixture/contract test。
- 变更已记录到 `progress.md`。
- 没有遗留未解释的测试失败。

### 7.3 P0/P1/P2 解释

- **P0**：当前 Sprint 的退出必需项；未完成不得进入下一 Sprint。
- **P1**：P0 全绿后，在同一 Sprint 内优先补齐的可靠性或体验项。
- **P2**：可记录但不得阻塞路线；只有用户要求或有明确收益时才做。

---

## 8. Sprint 0：生产化基座与类型边界

### 8.1 目标

先消除当前 Demo 代码中最阻碍后续适配器替换的耦合，不接任何真实外部系统。

### 8.2 P0 工作包

#### S0-01 基线冻结与仓储契约测试

- 把当前 SQLite 行为整理为仓储 contract tests。
- 覆盖权限、提案创建、冲突、确认幂等、客户快照、看板和审计。
- 保留现有 API 测试，不用重写替代已有测试。

#### S0-02 类型化端口

- 将 `DemoRepository` 泛化为稳定的 Repository 端口或多个聚合端口。
- 为 Proposal、Conflict、Snapshot、Dashboard、Material、Audit 等返回值建立 Pydantic model/dataclass/TypedDict。
- 应用服务不再依赖任意形状的 `dict[str, Any]`。
- API schema 与领域/应用 DTO 分离，避免将飞书字段泄漏到核心层。

#### S0-03 拆分 SQLite 适配器

- 将 656 行 `SQLiteDemoRepository` 按 schema/migration、seed、proposal、facts、query、audit 等责任拆分。
- 保证事务边界仍覆盖“确认提案→写入事实→更新提案→写审计”。
- 拆分过程中不得改变公开行为。

#### S0-04 Composition Root

- 把 `main.py` 中的具体对象装配移动到唯一 composition/provider 层。
- 增加 repository、gateway、extractor、file store、scheduler 的显式选择入口。
- 默认仍为 SQLite + Fake Feishu + DemoExtractor。

#### S0-05 配置与迁移策略

- 清理固定 Demo ID、日期和模式判断，使其只存在于 Demo seed/fixture，而不是核心服务。
- 增加可重复执行的 SQLite migration/version 机制。
- 校验配置并提供不泄密的 health/config summary。
- 更新 `.env.example`，只提交占位符。

### 8.3 P1

- 消除 Starlette/httpx warning，但只能通过受控依赖验证完成。
- 增加统一外部错误类型、结构化日志上下文和 request/correlation ID。
- 对 repository contract tests 增加属性化或参数化场景。

### 8.4 P2

- 为未来 PostgreSQL 预留 SQL 方言抽象。
- 重写 Demo Console 前端。

### 8.5 Exit Gate

```bash
cd agent-backend
uv sync
uv run ruff check .
uv run pytest
uv run python scripts/smoke_demo.py
```

并满足：

- 原有 18 个测试与新 contract tests 全绿。
- `main.py` 不直接构造所有具体外部适配器。
- 核心应用服务不再依赖 `DemoRepository` 名称和任意结构字典。
- SQLite 迁移能在空数据库和已有 Demo 数据库上重复执行。
- 无任何真实外部凭据也能完整运行。

---

## 9. Sprint 1：飞书 Base Schema 与真实 BaseRepository

### 9.1 依赖

必须在 Sprint 0 Exit Gate 全绿后开始。

### 9.2 目标

实现真实飞书 Base 数据适配器，同时让 SQLite 与 Base 通过同一套仓储契约。

### 9.3 P0 工作包

#### S1-01 Base 字段映射清单

- 以 `01-阶段一-飞书多维表格数据底座.md` 为领域输入。
- 明确 MVP 所需表、字段、字段类型、唯一键、关联、枚举和必填项。
- 建立“内部字段 ↔ Base 表/字段”的版本化映射文件。
- 第一批只覆盖当前三个闭环需要的表，不一次实现所有未来字段。

#### S1-02 Feishu API Client

- 实现 tenant token 获取与缓存。
- 实现 timeout、有限重试、指数退避、分页、错误码映射和限流处理。
- 日志不得记录 App Secret、token 或完整敏感内容。
- 使用 `httpx.MockTransport` 或等价 Fake 编写客户端测试。

#### S1-03 Base Schema Validator

- 启动或独立命令中读取 Base 元数据并验证表、字段和类型。
- 默认只报告差异；未经用户明确授权不得自动删除或破坏 Base 字段。
- 缺少权限时输出准确的人工操作清单。

#### S1-04 BaseRepository

- 实现当前仓储契约所需的 customer、permission、proposal、facts、audit、snapshot、dashboard 能力。
- 内部业务 ID 与 Base `record_id` 分离。
- 支持分页和幂等创建/更新。
- 外部失败不得伪装为成功。

#### S1-05 契约与切换

- SQLiteRepository 和 BaseRepository 运行同一套 contract tests。
- Base 测试默认使用 Fake HTTP fixture，不依赖真实凭据。
- 增加显式 `XERP_REPOSITORY=feishu_base` 切换。
- 首次真实接入先采用 shadow read/对账，不立即取消 SQLite 回退。

### 9.4 P1

- Base 批量读取和批量写入优化。
- 简单缓存及 ETag/更新时间冲突检查。
- Schema 差异生成可审阅的修复建议。
- 双写或影子验证工具，但必须有失败补偿和明确开关。

### 9.5 P2

- 自动创建全部 12 张表和复杂视图。
- PostgreSQL 同步。

### 9.6 Exit Gate

- SQLite 与 Base Fake Adapter 通过同一 contract suite。
- 真实 Base 凭据存在时，sandbox 中可创建提案、确认并查询客户快照。
- 真实凭据不存在时，所有默认测试和离线 Demo 仍全绿。
- Base Schema 不匹配时失败信息能指出具体表、字段和需要的人为动作。
- 完成一次 SQLite 与 Base 的抽样对账并记录结果。

---

## 10. Sprint 2：真实飞书事件、身份与客户路由

### 10.1 目标

把 `FakeFeishuEventGateway` 扩展为可替换的真实事件入口，完成身份、客户和事件幂等基础。

### 10.2 P0 工作包

#### S2-01 Webhook 安全边界

- 实现飞书 URL challenge。
- 按当前飞书开放平台规范实现签名/加密验证。
- 将验证失败映射为明确 HTTP 状态，不进入业务服务。
- 保存最小必要事件元数据，避免记录敏感正文。

#### S2-02 事件幂等与状态

- 以 event_id 或稳定组合键建立 event receipt。
- 状态至少包括 received、processing、succeeded、failed、ignored。
- 重放相同事件不得重复创建提案或正式事实。
- 支持安全重试和失败诊断。

#### S2-03 身份映射

- 建立 tenant/open_id/user_id 与内部用户的映射。
- 明确未知用户、离职用户、无权限用户的处理。
- 不允许客户端直接声明任意内部 `user_id` 绕过映射。

#### S2-04 客户上下文路由

- 建立 `chat_id → customer_id` 映射。
- 支持显式客户选择或绑定流程。
- 无法唯一确定客户时必须询问/返回选择卡片，不得猜测。

#### S2-05 消息、文件和卡片入口

- 接收文本消息并路由到 progress/question intent。
- 接收文件消息并生成材料处理入口。
- 发送提案确认卡片。
- 处理确认/拒绝/查看详情回调。
- 卡片重复点击保持幂等。

### 10.3 P1

- 群聊 @机器人 与私聊差异处理。
- 友好的错误卡片和重试入口。
- 事件 fixture 录制与脱敏回放工具。
- 卡片版本兼容策略。

### 10.4 P2

- 自动识别所有自由文本意图。
- 支持大量群聊的自动客户归属推断。

### 10.5 Exit Gate

- 脱敏事件 fixture 覆盖 challenge、文本、文件、卡片、重复事件和非法签名。
- Fake Gateway 回归测试保持全绿。
- 有飞书沙箱时，完成一次“报进展→收到卡片→确认→客户事实更新”。
- 没有飞书沙箱时，fixture + Mock HTTP 必须完整覆盖上述链路，并在进度中标记“真实沙箱待人工验收”。

---

## 11. Sprint 3：OpenAI 兼容结构化抽取

### 11.1 目标

在 `ProgressExtractor` 后实现真实模型 Provider，但保留确定性 `DemoExtractor` 和可重复离线测试。

### 11.2 P0 工作包

#### S3-01 结构化输出模型

- 为 contact、opportunity、action、risk、missing_fields、evidence 建立严格 schema。
- 对枚举、日期、金额、货币、置信度和来源做验证。
- 模型输出不可直接成为正式事实，只能形成候选提案。

#### S3-02 OpenAI-Compatible Provider

- 从环境读取 `OPENAI_API_KEY`、`OPENAI_BASE_URL`、`OPENAI_MODEL`。
- 使用独立 adapter，不让应用服务依赖 SDK。
- 支持结构化输出或严格 JSON schema 验证。
- 实现 timeout、有限重试、不可重试错误和 fallback。

#### S3-03 Prompt 版本与隐私

- Prompt 模板进入版本控制并带版本号。
- 仅发送完成任务所需文本，避免不必要的客户信息。
- 日志记录模型、耗时、token/cost 估计和 prompt version，但不记录密钥与完整敏感正文。

#### S3-04 评估夹具

- 建立脱敏中文进展样例集。
- 评估字段完整性、日期金额准确性、幻觉、冲突和缺失字段。
- 默认测试使用 FakeModelClient，不消耗额度。

#### S3-05 Provider 选择

- `XERP_EXTRACTOR=demo|openai` 显式切换。
- Key 缺失或 Provider 不可用时按配置回退或明确失败。
- `/health` 展示 provider 名称和可用状态，不展示敏感配置。

### 11.3 P1

- 问题修复重试、JSON repair，但必须保留原始错误诊断。
- 多模型兼容测试。
- 成本预算和单请求 token 上限。
- PII 脱敏策略。

### 11.4 P2

- Agent 自主执行正式写入。
- 未经确认根据模型输出覆盖客户事实。

### 11.5 Exit Gate

- `DemoExtractor` 仍通过原有固定样例测试。
- FakeModelClient 覆盖成功、schema 错误、timeout、rate limit 和 fallback。
- 有配置时运行一个 opt-in integration test，且不会被默认 `pytest` 自动触发。
- 模型结果始终先进入提案；无路径绕过确认。

---

## 12. Sprint 4：三个核心闭环生产化

### 12.1 目标

把 Demo 中针对固定样例的三个闭环扩展为真实飞书沙箱可使用的 MVP。

### 12.2 P0 工作包

#### S4-01 通用报进展

- 支持多种中文表达、相对日期、金额单位、负责人和下一步行动。
- 冲突检测从固定预算样例扩展为字段级规则。
- 支持用户在确认前编辑、拒绝或补充提案。
- 提案确认必须幂等并保留版本和审计。

#### S4-02 真实发材料

- 保存飞书文件 token、名称、类型、大小、来源消息和提交人。
- 下载或异步排队前先登记 material 与原始来源。
- 失败状态可见，不把“仅登记元数据”标记为“解析完成”。

#### S4-03 基于事实的问客户

- 查询只使用当前用户有权访问的客户事实和证据。
- 回答明确数据截止时间、事实、单一来源线索、推断、建议、来源和缺失信息。
- 当数据不足时明确说不知道，不得编造。
- 问答模板或模型回答必须可追踪其使用的事实 ID。

#### S4-04 卡片与错误体验

- 为提案、确认结果、权限拒绝、客户未绑定、处理失败提供稳定卡片。
- 用户可查看冲突、缺失项和证据。
- 错误消息给出下一步，而不是暴露堆栈。

#### S4-05 端到端回归

- 建立从飞书 fixture 到 Base Fake/SQLite 的端到端测试。
- 建立真实沙箱手工验收脚本。
- 保留本地 `/demo` 作为永久回归入口。

### 12.3 P1

- 批量确认或合并相关提案。
- 提案过期策略。
- 问答回答卡片和来源展开。
- 简单反馈按钮。

### 12.4 P2

- 通用自然语言数据库管理。
- 自动确认低风险写入。

### 12.5 Exit Gate

真实飞书沙箱中至少完成：

1. 发送一段真实进展。
2. 收到提案卡片并查看冲突/缺失字段。
3. 确认后 Base 中出现正式事实和审计。
4. 上传一份材料并看到准确处理状态。
5. 询问客户并得到带来源、截止时间和缺失信息的回答。
6. 未授权用户无法读取或修改该客户。
7. 重复事件和重复确认不会生成重复数据。

若凭据不可用，以上场景必须由 fixture/Mock/Fake 全部通过，并明确标记真实验收未完成，不得宣称 Sprint 已达到“真实沙箱完成”。

---

## 13. Sprint 5：Drive/Wiki 与文档处理

### 13.1 目标

实现可追踪、可重试的 L1/L2 文档处理链，不一次追求复杂文档全覆盖。

### 13.2 P0 工作包

#### S5-01 FileStore 与原件保全

- 定义 FileStore port。
- 实现本地 Fake/LocalFileStore 和 FeishuDriveFileStore。
- 保存 source file token/hash/size/mime/owner/customer_id。
- 校验大小、类型和下载完整性。

#### S5-02 DocumentProcessingTask

- 建立任务表和状态机：pending、downloading、parsing、review_required、succeeded、failed、dead_letter。
- 每次任务有幂等键、attempt、last_error、next_retry_at 和人工重试入口。
- 任务失败不影响原始 material 记录。

#### S5-03 L1/L2 解析器

第一批只支持：

- 文本型 PDF。
- DOCX 或可稳定提取文本的文档。
- 简单 TXT/Markdown。

暂不承诺：

- 扫描件 OCR。
- 复杂 PPT 图表语义。
- 多 Sheet Excel 业务规则。
- 任意版式合同解析。

#### S5-04 Evidence Snippet

- 将解析结果切为可引用片段。
- 每个片段保留文件、页码/段落、字符范围、解析版本和 hash。
- 提案与问答引用 snippet ID，不把整份全文塞进 Base 单元格。

#### S5-05 Wiki 展示

- 按客户生成或更新人读页面。
- Wiki 只展示已确认事实、摘要和来源链接。
- Wiki 发布失败不得回滚已确认事实，但必须记录待重试状态。

### 13.3 P1

- 简单 OCR adapter。
- 文档摘要和候选提案批量生成。
- 解析器质量评分与人工复核队列。
- 文件去重。

### 13.4 P2

- 全格式复杂文档平台。
- 自建向量数据库。
- 自动理解任意 Excel/PPT。

### 13.5 Exit Gate

- 支持的文档可从文件事件进入任务队列，保全原件，生成可引用片段和候选提案。
- 解析失败可重试、可进入 dead letter、可人工重新触发。
- 相同文件/事件重放不会重复生成任务和片段。
- Wiki 页面只展示已确认内容。
- 无飞书 Drive/Wiki 凭据时，本地 FileStore + Fake Publisher 完整通过测试。

---

## 14. Sprint 6：周报、提醒与经营看板

### 14.1 目标

在已确认事实基础上增加可追踪、幂等的经营自动化。

### 14.2 P0 工作包

#### S6-01 Scheduler Port

- 定义 scheduler/job port。
- 本地默认 disabled 或可手动触发。
- 每个 job run 有时间窗、幂等键、状态和审计。
- 生产调度实现不得和业务逻辑耦合。

#### S6-02 客户周报

- 汇总本周接触、商机变化、风险、行动、材料和缺失信息。
- 区分事实、推断和建议。
- 生成草稿，默认需要人工确认后发送。
- 保存报告版本和来源事实 ID。

#### S6-03 提醒规则

- 逾期行动提醒。
- 高风险未处理提醒。
- 商机长期无进展健康检查。
- 关键干系人覆盖不足提醒。
- 同一时间窗内不得重复发送相同提醒。

#### S6-04 经营视图

- 在 Base 或当前看板中展示客户数、活跃商机、金额、逾期行动、高风险、待确认提案和处理失败任务。
- 指标定义进入文档和测试。
- 展示数据截止时间。

#### S6-05 发送与审计

- 报告和提醒通过 Messaging port 发送。
- 记录接收人、发送结果、失败原因和重试状态。
- 权限变化后不得继续发送给已失去权限的用户。

### 14.3 P1

- 周报卡片反馈与确认。
- 可配置提醒阈值和免打扰时间。
- 团队级经营摘要。
- 指标趋势。

### 14.4 P2

- 完整 BI 平台。
- 高复杂度预测模型。

### 14.5 Exit Gate

- 三个种子/试运行客户可生成可追溯周报草稿。
- 逾期、高风险、无进展和覆盖不足规则有确定性测试。
- 重复运行同一时间窗不重复发送。
- 报告中的每条关键结论可追到事实或证据。
- 本地手动调度、Fake Messaging 和真实飞书沙箱发送均有对应验收路径。

---

## 15. Sprint 7：安全、运维与 3—5 客户试运行

### 15.1 目标

把“功能可用”推进到“可控试运行”，但不宣称已经达到大规模生产成熟度。

### 15.2 P0 工作包

#### S7-01 权限与租户隔离

- 完成用户、角色、客户成员关系和最小 RBAC。
- 所有查询和写入验证 tenant/customer scope。
- 增加越权、ID 枚举和跨客户访问测试。
- 支持权限撤销立即生效或明确缓存上限。

#### S7-02 密钥与配置

- 生产密钥只通过部署环境注入。
- 增加启动时配置校验和密钥轮换说明。
- 日志、错误、审计导出和备份中不得泄漏 token/secret。

#### S7-03 可观测性

- 结构化日志、correlation ID、event ID、customer scope。
- readiness/liveness。
- 关键指标：事件成功率、提案确认率、外部 API 错误、模型耗时/成本、文档任务积压、提醒失败。
- 最小告警规则和故障定位说明。

#### S7-04 部署、备份与恢复

- 增加 Dockerfile/部署配置。
- 明确运行进程、数据持久化、网络入口和 webhook URL。
- Base/本地状态、配置和必要元数据有备份/导出策略。
- 实际演练一次恢复流程并记录 RTO/RPO 观察值。

#### S7-05 可靠性边界

- 外部 API timeout、retry、rate limit、circuit/open state 或降级策略。
- webhook 请求体大小限制和基本限流。
- 后台任务 dead letter 与人工恢复。
- 不可恢复错误进入可操作队列。

#### S7-06 试运行准备

- 选择 3—5 个真实客户。
- 为每个客户确认 owner、成员、数据范围和敏感级别。
- 执行小批量数据导入和抽样核对。
- 完成用户培训、反馈入口、回滚开关和每日巡检。
- 试运行期间默认保留人工确认，不启用静默自动写入。

### 15.3 P1

- 审计导出和数据质量周检。
- 更细粒度字段权限。
- 灰度发布和 feature flag。
- 负载与容量基线。

### 15.4 P2

- 200 客户推广。
- 多地域高可用。
- 完整企业级 SSO/SCIM，除非试运行明确需要。

### 15.5 Exit Gate

- 试运行清单全部有负责人和状态。
- 越权测试、恢复演练、故障演练和回滚演练通过。
- 3—5 个客户完成数据抽样核对。
- 关键链路有指标和告警。
- Runbook 能让非开发者判断“正常、降级、停止使用、联系谁”。
- 用户明确批准后才进入真实客户试运行。

---

## 16. 全局自动化测试与验收命令

### 16.1 每个工作包至少运行

```bash
cd agent-backend
uv run ruff check .
uv run pytest <与当前工作包直接相关的测试>
```

### 16.2 每个 Sprint Exit Gate 必须运行

```bash
cd agent-backend
uv sync
uv run ruff check .
uv run pytest
uv run python scripts/smoke_demo.py
```

### 16.3 建议逐步增加的测试层

```text
unit                 领域规则、DTO、解析和错误映射
contract             SQLite/Base/FileStore/Messaging 适配器共同契约
api                   FastAPI 路由、权限和异常响应
fixture integration   脱敏飞书事件 + Mock HTTP + Fake Model
opt-in integration    真实飞书沙箱 / 真实模型，不在默认 pytest 中运行
e2e                   飞书事件→提案→确认→Base→问答/看板
smoke                 永久保留的离线 Demo 回归
```

### 16.4 禁止的测试方式

- 默认 `pytest` 真实调用飞书或模型。
- 测试依赖某个开发者本机 `.env` 才能通过。
- 为让测试变绿而删除权限、幂等或确认逻辑。
- 用 sleep 和无限重试掩盖竞态或外部失败。
- 将真实客户内容保存为 fixture。

---

## 17. 外部凭据与必须人工完成的事项

纯 Codex CLI 可以完成代码、Fake、fixture、测试、配置模板、校验脚本和 Runbook，但下面事项需要用户或飞书管理员参与。

### 17.1 飞书人工清单

- [ ] 创建或确认飞书企业自建应用。
- [ ] 提供 App ID、App Secret 的安全注入方式。
- [ ] 配置事件订阅 URL、Verification Token/Encrypt Key（按实际模式）。
- [ ] 开通机器人、消息、文件、云盘、Wiki、Base 所需权限。
- [ ] 管理员完成权限审批。
- [ ] 提供 sandbox 群聊并邀请机器人。
- [ ] 确认 Base app token、table IDs 和字段。
- [ ] 确认 `chat_id → customer_id` 的初始绑定。
- [ ] 提供试运行用户与客户成员关系。

### 17.2 模型人工清单

- [ ] 选择允许使用的 OpenAI 兼容提供者和模型。
- [ ] 通过环境安全注入 API Key。
- [ ] 确认第三方兼容服务的数据处理边界。
- [ ] 批准可发送给模型的字段和脱敏规则。
- [ ] 确认月度成本/调用上限。

### 17.3 试运行人工清单

- [ ] 选择 3—5 个客户和业务 owner。
- [ ] 确认哪些数据是真实事实、哪些是样例或历史线索。
- [ ] 抽样验收迁移数据和权限。
- [ ] 批准试运行开始、暂停、回滚和结束。
- [ ] 每周审核数据质量、错误和用户反馈。

### 17.4 凭据不可用时 Codex 的处理

凭据缺失不是停止本地开发的理由。Codex 应按以下顺序继续：

1. 实现 Port 和配置校验。
2. 实现 Fake/Mock adapter。
3. 使用官方协议形状制作脱敏 fixture。
4. 完成 contract、API 和 e2e fixture tests。
5. 生成 `docs/external-validation-checklist.md`。
6. 在 `progress.md` 标记 `code complete / external validation pending`。
7. 跳过会产生真实外部副作用的命令，继续当前 Sprint 其他独立工作。

但是，未完成真实沙箱验证时不得把相关 Exit Gate 标记为完全通过，也不得声称“已完成真实飞书接入”。

---

## 18. Git checkpoint 与变更纪律

### 18.1 开始任务前

```bash
git status --short --branch
git log -5 --oneline
```

如果工作区存在用户未提交修改：

- 不覆盖、不 reset、不 checkout 丢弃。
- 先判断是否与当前工作包冲突。
- 可安全隔离时继续，不可安全隔离时记录并向用户说明。

### 18.2 提交粒度

推荐一个工作包 1—3 个小提交，例如：

```text
test(repository): define proposal repository contract
refactor(repository): split sqlite proposal persistence
feat(feishu): add base schema validator
feat(feishu): handle idempotent card confirmation
```

### 18.3 每个 Sprint 的 checkpoint

Exit Gate 全绿后生成本地 checkpoint：

```text
chore(checkpoint): complete post-demo sprint N
```

提交信息可按实际变更调整。必须在 `progress.md` 记录 commit SHA 和测试结果。

### 18.4 禁止行为

未经用户明确授权，Codex 不得：

- `git push`。
- `git reset --hard`。
- 强制 push。
- 删除用户分支或标签。
- 修改或提交真实 `.env`/密钥。
- 用 amend/历史重写覆盖用户已有提交。

---

## 19. Codex 启动、继续与恢复提示词

### 19.1 第一次开始 Demo 后持续开发

在仓库根目录运行 Codex CLI，然后粘贴：

```text
请直接执行本仓库的 Demo 后持续开发计划，不要只做分析或再写一份重复计划。

必须先读取并遵守：
1. AGENTS.md
2. 08-Demo后CodexCLI持续开发计划.md
3. .planning/.active_plan 指向目录中的 task_plan.md
4. 同目录 findings.md
5. 同目录 progress.md

先检查 git status、当前 HEAD 和基线测试。从 task_plan 中第一个未完成的 P0 工作包开始，按“实现→测试→修复→记录→本地 checkpoint”持续执行。每个 Sprint 的 Exit Gate 全绿后才能进入下一 Sprint。

外部飞书或模型凭据不可用时，不要等待：使用 Port + Fake/Mock + 脱敏 fixture + contract test 继续；把真实沙箱验收标记为 pending。永久保留 SQLite、FakeFeishuEventGateway、DemoExtractor、/demo 和 smoke_demo 离线回退路径。

不要 push，不要使用危险 Git 命令，不要覆盖用户已有改动。除非遇到无法本地替代、会产生真实外部副作用、涉及安全/数据删除或需求存在重大歧义的硬阻塞，否则不要停下来问问题。
```

### 19.2 Codex 中断后继续

```text
继续执行当前 post-demo active plan。先读取 AGENTS.md、08-Demo后CodexCLI持续开发计划.md、当前 task_plan.md、findings.md、progress.md，并执行 5-Question Reboot Check：
1. 当前目标是什么？
2. 当前 Sprint 和第一个未完成 P0 工作包是什么？
3. 最近完成了什么、对应 commit 是什么？
4. 当前测试状态和已知阻塞是什么？
5. 下一步最小可验证动作是什么？

然后直接实施下一步，不要重新规划已完成内容。先检查 git status，保护用户改动；完成后更新计划和进度，运行相关测试。不要 push。
```

### 19.3 只执行一个 Sprint

```text
只执行 Demo 后计划的 Sprint N。完成该 Sprint 所有 P0 和 Exit Gate 后停止，不进入 Sprint N+1。保持离线 Demo 回归全绿，更新 .planning 文件并创建本地 checkpoint；不要 push。
```

### 19.4 只做外部沙箱验收

```text
当前只执行 Sprint N 的真实外部沙箱验收。先运行离线基线测试，再检查必需配置是否齐全；不得打印或提交密钥。只执行清单中已批准的非破坏性操作，记录请求结果、外部对象 ID、验收证据和清理方式。若权限不足，停止外部操作并输出精确权限/人工操作清单，不要伪造成功。
```

---

## 20. Codex 必须停止或升级给用户的情况

以下情况允许且要求 Codex 停止自动执行并向用户说明：

1. 需要创建、删除、覆盖真实 Base、Wiki、Drive 数据或修改生产权限。
2. 需要发送真实客户消息、周报或提醒，且用户尚未批准接收人和内容。
3. 需要真实密钥、管理员审批、域名、部署账户或付费资源。
4. 检测到疑似密钥泄漏、跨客户数据泄漏或权限绕过。
5. 数据迁移可能丢失、覆盖或不可逆修改真实数据。
6. 现有用户未提交改动与当前任务冲突，无法安全合并。
7. 同一失败连续采用三种合理方案仍不能推进。
8. 产品口径有重大歧义，会导致不同的数据模型或不可逆外部行为。
9. Exit Gate 出现无法解释的回归，且继续开发会扩大问题。

停止时必须给出：

- 已完成内容。
- 当前失败的准确命令/场景。
- 已尝试方法。
- 风险。
- 需要用户提供的最小信息或批准。
- 可继续进行的无阻塞工作。

---

## 21. 可用 MVP 与试运行就绪定义

### 21.1 “可用 MVP”必须同时满足

- 飞书沙箱中三个核心闭环可重复完成。
- Base 是可选真实事实适配器，SQLite 是稳定离线回退。
- 真实身份和客户路由有效。
- 所有正式写入都经过提案确认和审计。
- 模型抽取失败可回退或明确失败，不会写入脏事实。
- 支持至少一种真实文档格式的可追踪处理。
- 有周报草稿和关键提醒的幂等生成能力。
- 默认测试、fixture e2e 和离线 smoke 全绿。
- 已知限制和人工操作有文档。

### 21.2 “试运行就绪”必须额外满足

- 3—5 个客户和用户权限已抽样核对。
- 真实数据导入有对账记录。
- 监控、告警、备份、恢复和回滚演练通过。
- 故障/权限/数据质量 Runbook 可执行。
- 成本、限流、重试和 dead letter 有边界。
- 用户明确批准开始试运行。

### 21.3 仍不能宣称“生产成熟”的情况

即使 Sprint 7 完成，也不自动代表：

- 已支持 200 客户规模。
- 已达到高可用或灾备 SLA。
- 已完成所有复杂文档解析。
- 已完成企业级 SSO/SCIM/合规认证。
- 已验证长期模型成本和质量稳定性。
- 已经不需要人工确认和数据质量巡检。

这些结论必须基于试运行数据和明确验收，不得由 Codex 自行推断。

---

## 22. 后续扩容与升级触发条件

只有出现证据时才从 Base/SQLite MVP 升级：

### 考虑 PostgreSQL 的信号

- Base 查询/写入延迟持续影响用户体验。
- 事务、一致性、复杂查询或历史版本需求超出 Base 能力。
- 数据量、并发或权限模型明显增长。
- 多系统同步成为主要故障源。

### 考虑队列/工作流系统的信号

- 文档任务和外部事件积压无法靠简单任务表管理。
- 重试、补偿、长任务、人工节点显著复杂化。
- 需要可视化工作流和可靠调度。

### 考虑专业检索组件的信号

- Evidence snippets 数量和检索质量超出简单过滤/全文索引能力。
- 问答评估显示召回率成为主要问题。
- 已有脱敏评估集证明引入组件能显著改善结果。

升级前 Codex 必须先记录测量数据、候选方案、迁移成本和回退方案，不能仅因“架构更先进”而引入。

---

## 23. Sprint 依赖总览

```text
Sprint 0 类型边界与工程基座
    ↓
Sprint 1 BaseRepository
    ↓
Sprint 2 飞书事件/身份/路由
    ↓
Sprint 3 模型结构化抽取
    ↓
Sprint 4 三个真实核心闭环
    ↓
Sprint 5 Drive/Wiki/文档处理
    ↓
Sprint 6 周报/提醒/经营视图
    ↓
Sprint 7 安全/运维/3—5 客户试运行
```

允许的有限并行：

- Sprint 1 的 Base Fake contract tests 可与 Sprint 2 的事件 fixture 设计并行。
- Sprint 3 的模型评估集可在 Sprint 2 外部凭据等待期间开发。
- Sprint 5 的 LocalFileStore/解析器可在 Drive 权限等待期间开发。
- Sprint 6 的规则测试可在真实 Messaging 权限等待期间开发。

不允许的越级：

- 未完成 Sprint 0 就同时重写 SQLite、Base、飞书和模型。
- 未完成身份/客户路由就接真实客户数据。
- 未完成事件幂等就开放真实 webhook。
- 未完成权限和审计就开始真实客户试运行。

---

## 24. 本计划的落地方式

本文件是 Demo 后产品和工程路线的总 source of truth。Codex 的日常执行状态应落到：

```text
.planning/post-demo-mvp/task_plan.md
.planning/post-demo-mvp/findings.md
.planning/post-demo-mvp/progress.md
```

其中：

- `task_plan.md`：只保存当前 Sprint、工作包状态、Exit Gate 和阻塞。
- `findings.md`：保存代码发现、外部 API 约束、设计决定和风险。
- `progress.md`：按时间记录修改文件、测试、commit、失败和下一步。

已完成的 `.planning/demo-2026-07-15/` 必须保留为历史记录，不得删除或改写成新计划。

---

## 25. 下一步

Demo 完成并提交后，Codex 的第一个后续开发任务是：

```text
Sprint 0 / S0-01：冻结现有行为并建立仓储契约测试。
```

开始前先确认：

```bash
git status --short --branch
git log -3 --oneline
cd agent-backend
uv run ruff check .
uv run pytest
uv run python scripts/smoke_demo.py
```

基线全绿后，再开始类型化和拆分。不得直接从真实飞书或模型接入开始，因为当前最大的工程风险是端口不稳定和具体实现耦合，而不是缺少更多功能。
