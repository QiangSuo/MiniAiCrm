# 2026-07-15 Codex CLI 自主开发 Demo 计划

## 1. 这次计划更新解决什么问题

原路线以 7—10 天技术 Demo、2—4 周 MVP 为目标。当前仓库在 2026-07-14 仍只有规划文档，没有应用代码，因此不能按原阶段顺序逐项建设后再 Demo。

本计划把目标改成：

> 在 2026-07-15 前，纯用 Codex CLI 完成一个本地优先、无外部凭据也能运行的 XERP 纵向切片；先证明核心业务闭环，再逐步替换为真实飞书 Base、机器人和模型服务。

“纯用 Codex CLI 开发”是指：

- Codex CLI 负责创建工程、编码、测试、修复、文档和 Demo 脚本。
- 人只负责启动 Codex、必要时提供飞书凭据、做最终业务验收和现场演示。
- 产品运行时不等于依赖 Codex CLI；为了现场稳定，Demo 默认使用本地确定性抽取和 SQLite。

## 2. 明日 Demo 的一句话

```text
在一个本地 Demo 页面中，选择客户后提交材料或拜访进展，
系统先生成可审计的变更提案，人工确认后写入客户事实库，
再基于已确认事实回答客户问题并展示经营概览。
```

## 3. 明日演示范围

### 3.1 P0：必须完成

1. 本地 FastAPI 服务和 `/demo` 页面。
2. 一个固定 Demo 客户和可重复种子数据。
3. “发材料”：资料登记 → 资料归档提案 → 确认 → 资料证据入库。
4. “报进展”：文本抽取 → 接触/商机/行动提案 → 冲突展示 → 确认写入。
5. “问客户”：读取已确认事实 → 输出结论、事实、推断、建议、来源和缺失信息。
6. PermissionGuard：未授权用户不能读取或写入该客户。
7. ProposalEngine：确认前不能修改正式事实，确认后事务性写入。
8. 经营概览：活跃商机、金额、逾期行动、高风险、待确认提案等。
9. 一键重置、自动测试、smoke test 和现场 Runbook。
10. 没有任何飞书或 OpenAI 密钥时仍可完整演示。

### 3.2 P1：P0 全绿后再做

1. 最小飞书消息事件接入。
2. 飞书卡片或 webhook replay 展示。
3. OpenAI 结构化抽取提供者。
4. Dockerfile。
5. 更接近正式产品的周报卡片。

### 3.3 2026-07-15 明确不做

- 飞书 Base 12 张表的全量生产同步。
- Wiki 自动建页和云盘文件下载。
- OCR、扫描件识别、复杂 PPT/Excel 解析、RAG。
- PostgreSQL、Redis、Kafka、Temporal、向量库。
- 完整多租户、RBAC、SSO 和 200 客户数据迁移。
- 独立 React/Vue 管理后台。
- 正式公网部署和生产安全验收。

## 4. 为什么要本地优先

真实飞书集成依赖 App ID、Secret、事件订阅、公网回调、管理员授权、Base token 和字段 ID。任何一项未准备好都会阻塞现场演示。

因此 Demo 采用以下边界：

```text
Demo Console / API
        ↓
Application Services
        ↓
Repository / Gateway Ports
        ├── SQLiteDemoRepository（P0，默认）
        ├── FakeFeishuGateway（P0，用于回放）
        └── FeishuBaseRepository（P1，可选）
```

这样可以保证：

- 业务逻辑、提案确认、权限和证据追溯是真实实现。
- 外部系统只是适配器，不决定 Demo 成败。
- 明日以后可逐步把本地 Adapter 替换为飞书 Adapter，不需要推翻领域逻辑。

## 5. 建议工程结构

后续 Codex 应创建：

```text
agent-backend/
  pyproject.toml
  uv.lock
  .env.example
  README.md
  app/
    main.py
    config.py
    domain/
      models.py
      enums.py
      errors.py
    application/
      intake_service.py
      proposal_service.py
      question_service.py
      dashboard_service.py
      permission_service.py
    ports/
      repository.py
      extractor.py
      feishu_gateway.py
    infrastructure/
      sqlite_repository.py
      demo_extractor.py
      fake_feishu_gateway.py
      openai_extractor.py        # P1
      feishu_base_repository.py  # P1
    api/
      routes.py
      schemas.py
    demo/
      index.html
      app.js
      styles.css
  data/
    .gitkeep
  samples/
    demo_seed.json
    material.json
    progress.json
    questions.json
  scripts/
    bootstrap.sh
    run_demo.sh
    smoke_demo.py
  tests/
    test_health.py
    test_material_flow.py
    test_progress_flow.py
    test_question_flow.py
    test_permissions.py
    test_dashboard.py
  docs/
    DEMO-RUNBOOK.md
    KNOWN-LIMITATIONS.md
```

允许 Codex 根据实现需要微调文件名，但不得改变“领域服务与外部适配器分离”的边界。

## 6. 固定 Demo 数据

### 客户

```text
customer_id: CUST-DEMO-001
客户名称: 中国星海集团
客户负责人: u-demo-owner
```

### 用户

```text
授权用户: u-demo-owner
未授权用户: u-outsider
```

### 发材料样例

```text
文件名：集团数字化规划.pdf
说明：这是今天客户给的集团数字化规划。
```

预期：生成资料归档提案；确认后资料证据表新增一条，保留原始文件名、说明、提交人、提交时间和处理状态。

### 报进展样例

```text
今天见了李总。他表示集团今年先做财务和采购，
预算大约在一亿元左右，要求我们月底前提交整体方案。
```

预期至少抽取：

- 接触记录：见了李总。
- 商机方向：财务、采购。
- 预算线索：约 1 亿元，标注为待确认或单一来源。
- 行动承诺：月底前提交整体方案。
- 缺失信息：李总职位、行动负责人、准确截止日期。

### 问客户样例

```text
这个客户目前最关键的三个突破口是什么？
```

预期回答包含：

- 数据截止时间。
- 三个突破口。
- 支撑事实和来源记录 ID。
- Agent 推断与建议动作。
- 当前缺失信息。
- 不把未确认预算表述为确定事实。

## 7. 必须实现的外部行为

路径可由 Codex 微调，但 README、前端和 smoke test 必须使用同一合同。

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| GET | `/health` | 启动检查 |
| GET | `/demo` | 打开 Demo Console |
| POST | `/api/demo/reset` | 重置种子数据 |
| POST | `/api/intake/material` | 创建资料归档提案 |
| POST | `/api/intake/progress` | 创建进展变更提案 |
| POST | `/api/proposals/{id}/confirm` | 确认并事务性写入 |
| POST | `/api/questions` | 基于客户事实回答 |
| GET | `/api/customers/{id}/snapshot` | 查看客户事实快照 |
| GET | `/api/dashboard` | 查看经营概览 |

所有业务请求至少包含：

```json
{
  "customer_id": "CUST-DEMO-001",
  "user_id": "u-demo-owner"
}
```

## 8. 实施阶段与时间盒

> 时间盒是取舍工具，不是承诺。一个阶段超时后，先删 P1 和视觉增强，不得删测试、权限和提案确认。

### 2026-07-14 晚间：Phase 1—3

#### Phase 1：工程骨架与可启动服务（60—90 分钟）

- 初始化 uv/FastAPI 工程。
- SQLite schema 和种子数据。
- `/health`、`/demo`、reset。
- 配置、日志、基础测试。

退出条件：应用启动、健康检查和首个测试通过。

#### Phase 2：三个核心闭环（150—210 分钟）

- 发材料、报进展、问客户。
- 提案确认、权限、冲突、证据引用。
- 每个闭环完成后立即补 API 测试。

退出条件：三个闭环测试全绿，无密钥可运行。

#### Phase 3：Demo Console 与经营概览（90—120 分钟）

- 单页交互界面。
- 预设样例、一键提交/确认/刷新。
- KPI 卡片、客户快照、数据来源展示。

退出条件：浏览器可完成全流程，不需要手工改数据库。

### 2026-07-15 Demo 前：Phase 4—5

#### Phase 4：稳定性与可选集成（60—90 分钟）

- bootstrap/run/smoke 脚本。
- 错误提示、审计日志、README。
- webhook replay/FakeFeishuGateway。
- 只有 P0 全绿且凭据现成时才做真实飞书。

#### Phase 5：验收和彩排（60 分钟）

- ruff、pytest、smoke test。
- 重置后完整彩排两次。
- 准备已知限制与现场回退。
- 创建本地 checkpoint commit，不 push。

## 9. Codex CLI 自主执行方法

### 9.1 开始前检查

在仓库根目录执行：

```bash
codex doctor
codex --version
uv --version
uv python list --only-installed
```

必须确认：

- Codex 能正常启动会话。
- Python 3.12 可用。
- Git 工作区中的用户已有改动已知且不会被覆盖。

### 9.2 推荐启动命令

```bash
cd /Users/suoqiang/Documents/MiniAiCrm
codex exec \
  -C . \
  -s workspace-write \
  -a never \
  -o .planning/demo-2026-07-15/last-message.md \
  - < PROMPT-CODEX-EXEC-DEMO.md
```

说明：

- `workspace-write` 允许 Codex 修改当前仓库，但不等于解除所有系统保护。
- `never` 表示执行过程中不等待逐条命令审批；失败会返回给 Codex 自己处理。
- 不推荐使用 `--dangerously-bypass-approvals-and-sandbox`。
- 不要添加 `--ephemeral`，否则不利于后续恢复会话。

### 9.3 如果单次执行提前结束

先查看：

```bash
cat .planning/demo-2026-07-15/task_plan.md
cat .planning/demo-2026-07-15/progress.md
cat .planning/demo-2026-07-15/last-message.md
```

然后续跑：

```bash
codex exec resume --last \
  "继续执行 AGENTS.md 和 .planning/demo-2026-07-15/task_plan.md。从第一个 pending Phase 开始直接实施、测试、修复并更新进度，不要只做汇报。"
```

如果最近会话不是本项目，不要使用 `--last`，应从 Codex 会话列表中选择正确会话或重新运行 9.2 的命令。

### 9.4 人只在这些情况介入

- Codex CLI 本身无法连接模型服务。
- 需要提供真实飞书密钥或管理员操作。
- Demo 业务口径与预期明显冲突。
- Codex 准备执行危险 Git 操作或修改仓库外文件。

除此以外，Codex 应自行选择合理默认值继续。

## 10. 自动执行纪律

后续 Codex 必须遵守：

1. 先实现，不再重新规划。
2. 从第一个 pending Phase 开始。
3. 每个 Phase 通过 Exit Gate 后更新计划状态。
4. 外部依赖失败时切换 Fake/Local Adapter。
5. 固定样例优先保证稳定，不用随机模型结果作为唯一 Demo 路径。
6. 测试失败先修复，不把失败留给最终阶段。
7. 不新增非 P0 基础设施。
8. 不 push、不重写历史、不删除原有文档。
9. 不把未实现的飞书、OCR、RAG 能力写成已实现。
10. 只有 P0 全绿后才能做 P1。

## 11. 测试与验收闸门

### 自动测试

最终命令应至少包括：

```bash
cd agent-backend
uv sync
uv run ruff check .
uv run pytest
uv run python scripts/smoke_demo.py
```

### 必测行为

- 确认前：正式客户事实不变化。
- 确认后：相关正式记录一次性写入，提案状态为 confirmed。
- 重复确认：不能重复写入。
- 未授权用户：返回 403 且不泄露客户数据。
- 不同 `customer_id`：不能交叉引用。
- 冲突预算或截止日期：提案中显示冲突，不静默覆盖。
- 问答：包含数据截止、事实、推断、建议、来源、缺失信息。
- 无密钥启动：完整测试和 smoke test 通过。
- reset：多次演示后恢复固定初始状态。

### 完成定义

只有同时满足以下条件，Codex 才能宣布完成：

- `.planning/demo-2026-07-15/task_plan.md` Phase 1—5 全部 complete。
- ruff、pytest、smoke test 全绿。
- `scripts/run_demo.sh` 一条命令可启动。
- `/demo` 能完成完整主路径。
- Demo Runbook 已连续彩排两次。
- 已知限制被记录，没有虚报 P1 能力。

## 12. 5 分钟现场 Demo Runbook

### 0:00—0:30：重置与背景

- 打开 `/demo`。
- 点击“重置 Demo 数据”。
- 说明这是一个客户隔离、提案确认后写入的客户情报平台。

### 0:30—1:30：报进展

- 选择授权用户和 Demo 客户。
- 使用预设拜访文本。
- 点击“生成提案”。
- 展示抽取出的关键人、方向、预算线索、行动承诺和缺失字段。

### 1:30—2:00：确认写入

- 先展示确认前客户快照没有变化。
- 点击确认。
- 展示接触、商机和行动一次性进入事实库，并出现审计记录。

### 2:00—3:00：问客户

- 询问三个突破口。
- 展示回答中的事实、推断、建议、来源和缺失信息。
- 强调预算是单一来源/待确认，不会被说成确定事实。

### 3:00—3:40：发材料

- 使用“集团数字化规划.pdf”预设。
- 生成资料归档提案并确认。
- 展示资料证据、提交人、时间和处理状态。

### 3:40—4:20：经营概览

- 展示活跃商机、预计金额、逾期行动、高风险和待确认提案。
- 展示周报/经营摘要预览。

### 4:20—4:50：权限拒绝

- 切换到 `u-outsider`。
- 重试客户查询。
- 展示 403 和不泄露数据的错误提示。

### 4:50—5:00：收尾

- 说明当前已验证核心闭环。
- 说明下一步是把本地 Repository/Gateway 替换为飞书 Base、机器人和 Wiki 适配器。

## 13. 现场回退方案

1. **浏览器页面异常**：运行 smoke script，并使用 FastAPI `/docs` 演示相同 API。
2. **服务未启动**：执行 `scripts/run_demo.sh`。
3. **数据被改乱**：调用 `/api/demo/reset` 或点击重置。
4. **Codex/OpenAI/网络不可用**：不影响 Demo，默认确定性抽取。
5. **飞书未配置**：明确说明真实飞书是 Adapter 替换，不影响核心业务逻辑证明。
6. **端口冲突**：Runbook 中记录替代端口，并确保前端使用相对路径。

## 14. 明日之后恢复原路线

Demo 完成后再按原 `00`—`06` 路线推进：

1. 把 SQLiteDemoRepository 替换为真实 BaseRepository。
2. 把 FakeFeishuGateway 替换为真实消息、卡片和文件事件。
3. 把 DemoExtractor 替换或增强为模型结构化抽取。
4. 增加 Wiki/云盘和复杂文档处理。
5. 扩展周报、提醒、健康度和经营看板。
6. 完成真实客户权限、数据质量和试运行。

本次本地 Demo 不是一次性废代码；关键要求是边界清楚，使外部适配器可以逐步替换。
