# Progress Log: XERP 2026-07-15 Demo

## Session: 2026-07-14

### Phase 0: 计划与环境确认
- **Status:** complete
- **Started:** 2026-07-14
- Actions taken:
  - 阅读现有 `00`—`06` 规划文档并提取核心产品约束。
  - 确认仓库为纯文档状态。
  - 检查 Codex CLI、Python、uv、Node、Docker 与 Git 环境。
  - 将 7—10 天技术 Demo 压缩为 2026-07-15 本地纵向切片。
  - 定义 P0/P1/不做范围、验收闸门和自动续跑规则。
- Files created/modified:
  - `.gitignore`
  - `.planning/.active_plan`
  - `.planning/demo-2026-07-15/task_plan.md`
  - `.planning/demo-2026-07-15/findings.md`
  - `.planning/demo-2026-07-15/progress.md`
  - `AGENTS.md`
  - `07-2026-07-15-CodexCLI自主开发Demo计划.md`
  - `PROMPT-CODEX-EXEC-DEMO.md`
  - `README.md`
  - `00-轻量版总体路线图.md`
  - `00-阶段零-Codex快速开发准备.md`

### Phase 1: 工程骨架与可启动服务
- **Status:** complete
- **Started/Completed:** 2026-07-14
- Actions taken:
  - 创建 Python 3.12、FastAPI、uv 工程与锁文件。
  - 建立配置、JSON 结构化日志、领域模型、Repository Port 和应用服务骨架。
  - 实现 SQLite schema、固定客户/权限/风险种子和可重复 reset。
  - 实现 `/health`、`/demo`、`/api/demo/reset`。
  - 以 API 公共边界完成健康检查、页面和重置测试。
- Files created/modified:
  - `agent-backend/pyproject.toml`, `agent-backend/uv.lock`
  - `agent-backend/app/config.py`, `agent-backend/app/logging.py`, `agent-backend/app/main.py`
  - `agent-backend/app/domain/*`, `agent-backend/app/ports/repository.py`
  - `agent-backend/app/infrastructure/sqlite_repository.py`
  - `agent-backend/app/application/demo_service.py`
  - `agent-backend/app/demo/index.html`
  - `agent-backend/tests/conftest.py`, `agent-backend/tests/test_health.py`

### Phase 2: 三个核心闭环
- **Status:** complete
- **Started/Completed:** 2026-07-14
- Actions taken:
  - 实现确定性 `DemoExtractor`，抽取李总、优先方向、一亿元预算线索和月底方案承诺。
  - 实现 PermissionGuard、IntakeService、ProposalEngine、QuestionService。
  - 材料和进展只创建 pending 提案；确认动作在 SQLite 单事务内写入正式事实并记录审计。
  - 实现重复确认 409、跨客户/未授权 403、预算冲突展示和不静默覆盖。
  - 问答输出数据截止、事实、推断、建议、来源、置信口径和缺失信息。
- Files created/modified:
  - `agent-backend/app/application/{permission_service,intake_service,proposal_service,question_service}.py`
  - `agent-backend/app/infrastructure/demo_extractor.py`
  - `agent-backend/app/infrastructure/sqlite_repository.py`
  - `agent-backend/app/api/{schemas,routes}.py`, `agent-backend/app/main.py`
  - `agent-backend/tests/test_{material_flow,progress_flow,question_flow,permissions}.py`

### Phase 3: Demo 控制台与经营概览
- **Status:** in_progress
- Actions taken:
  - 已进入经营概览 API 和单页控制台实现。
- Files created/modified:
  - 待补充。

## Test Results
| Test | Input | Expected | Actual | Status |
|------|-------|----------|--------|--------|
| 规划文件存在 | `test -f` 检查 | 全部存在 | 全部存在，内部 Markdown 链接有效 | pass |
| Codex CLI 可执行 | `codex --version` | 输出版本 | `codex-cli 0.144.3` | pass |
| Python 3.12 可用 | `uv python list --only-installed` | 存在 3.12 | 3.12.13 | pass |
| Phase 1 API 测试 | `uv run pytest` | health/demo/reset 全绿 | 3 passed | pass |
| Phase 1 Ruff | `uv run ruff check .` | 无违规 | All checks passed | pass |
| Phase 2 核心闭环 | `uv run pytest` | 材料/进展/问答/权限全绿 | 11 passed | pass |

## Error Log
| Timestamp | Error | Attempt | Resolution |
|-----------|-------|---------|------------|
| 2026-07-14 | `codex doctor` provider route probe 超时 | 1 | 在正式自主执行前重试；Demo 产品设计为离线可运行 |
| 2026-07-14 | 初次 API 测试找不到 `app` 模块 | 1 | 在 pytest 配置中加入项目根目录并创建应用模块 |
| 2026-07-14 | Ruff 报导入顺序和超长行 | 1 | 使用 Ruff 自动修复导入并手工拆分 SQL |
| 2026-07-14 | shell 中无 `python` 命令 | 1 | 改用项目固定解释器 `uv run python` |
| 2026-07-14 | 第一次写 Phase 2 文件时工作目录已在 `agent-backend`，路径重复 | 1 | 改用相对当前目录的 `app/...` 路径 |
| 2026-07-14 | SQLite Row 被当作键迭代导致 snapshot 500 | 1 | 审计行改为显式字段映射 |

## 5-Question Reboot Check
| Question | Answer |
|----------|--------|
| Where am I? | Phase 1—2 已完成，正在实施 Phase 3 Demo Console 与经营概览 |
| Where am I going? | 完成工程骨架、三个闭环、Demo Console、稳定性与最终彩排 |
| What's the goal? | 2026-07-15 前交付可重复演示的本地 XERP 纵向切片 |
| What have I learned? | 见 `findings.md` |
| What have I done? | 已完成工程骨架以及材料、进展、问答、权限、提案确认闭环 |

### 2026-07-14 Context Resume — 5-Question Reboot Check
| Question | Answer |
|----------|--------|
| Where am I? | Phase 3 in progress；经营概览与单页控制台已实现，待完成修复后的浏览器 Exit Gate |
| Where am I going? | 完成 Phase 3 浏览器全流程，再实现 Phase 4 离线脚本/Fake Adapter，最后完成 Phase 5 全量验收与两次彩排 |
| What's the goal? | 交付无密钥、无外网也可重复演示的 2026-07-15 XERP P0 纵向切片 |
| What have I learned? | 图索引可用；当前实现已包含 Dashboard、Demo Console 和敏感视图清理，需重新浏览器验证 |
| What have I done? | Phase 1—2 complete，Phase 3 代码与 13 项测试已完成，恢复后继续 Exit Gate |

### Phase 3: Demo 控制台与经营概览
- **Status:** complete
- **Started/Completed:** 2026-07-14
- Actions taken:
  - 实现 `/api/dashboard`，聚合活跃商机、金额线索、待办/逾期行动、高风险、待确认提案与经营摘要。
  - 完成无构建链单页 `/demo` 控制台，支持报进展、发材料、问客户、提案确认、经营概览、快照、审计和一键重置。
  - 修复切换未授权用户时保留先前敏感视图的问题；现在立即清空 KPI、提案/回答、事实和审计。
  - 使用 Playwright 从 reset 开始完成报进展→确认→问客户→发材料→确认→未授权拒绝全流程。
- Files created/modified:
  - `agent-backend/app/application/dashboard_service.py`
  - `agent-backend/app/api/routes.py`
  - `agent-backend/app/infrastructure/sqlite_repository.py`
  - `agent-backend/app/demo/{index.html,styles.css,app.js}`
  - `agent-backend/tests/test_dashboard.py`
- Verification:
  - `uv run ruff check .`：pass
  - `uv run pytest`：13 passed
  - 浏览器 Exit Gate：pass；全流程无需命令行改数据，未授权视图不泄露已加载数据。

### Phase 4: 稳定性、脚本与本地 Feishu Replay
- **Status:** complete
- **Started/Completed:** 2026-07-14
- Actions taken:
  - 新增 `FakeFeishuEventGateway` 和 `POST /api/integrations/feishu/replay`，支持进展、资料和问答的离线事件重放。
  - 新增 extractor provider selection；无 `OPENAI_API_KEY` 时明确选择 `DemoExtractor`，`/health` 返回 `extractor_provider: demo`。P0 不启用真实模型。
  - 新增 bootstrap、run_demo 与覆盖完整业务路径的离线 smoke script。
  - 新增 `.env.example` 与 `agent-backend/README.md`，说明离线启动、公共接口、密钥规则与 P0 边界。
  - 验证未授权 replay 仍返回通用 403；Fake gateway 复用应用服务、提案确认与已有审计事务。
- Files created/modified:
  - `agent-backend/app/infrastructure/{extractor_provider,fake_feishu_gateway}.py`
  - `agent-backend/app/api/{schemas,routes}.py`
  - `agent-backend/app/main.py`
  - `agent-backend/tests/test_feishu_replay.py`, `agent-backend/tests/test_health.py`
  - `agent-backend/scripts/{bootstrap.sh,run_demo.sh,smoke_demo.py}`
  - `agent-backend/.env.example`, `agent-backend/README.md`
- Verification:
  - `uv run ruff check .`：pass
  - `uv run pytest`：17 passed
  - `uv run python scripts/smoke_demo.py`：pass，使用临时 SQLite、无 Key、无外部网络
  - `./scripts/bootstrap.sh`：pass
  - `PORT=8011 ./scripts/run_demo.sh` 后 `/health` 与 `/demo`：HTTP 200

### 2026-07-14 Phase 5 Context Resume — 5-Question Reboot Check
| Question | Answer |
|----------|--------|
| Where am I? | Phase 1—4 complete，Phase 5 in progress；功能、测试、smoke 和 Runbook 已就绪，待两次完整彩排、代码审查与最终验收。 |
| Where am I going? | 完成两次浏览器 Runbook 彩排，审查并修复 working-tree 改动，执行用户指定的最终命令并关闭全部 P0 Gate。 |
| What's the goal? | 交付可本地重复运行、无密钥无外网可演示的 2026-07-15 XERP 客户情报纵向切片。 |
| What have I learned? | 8000 端口仍有旧 Uvicorn 进程；Playwright wrapper 需通过 bash 调用；当前代码图已可用但需在最终代码后刷新。 |
| What have I done? | 已恢复并按顺序复核必读文档、Runbook、Phase 5 状态、技能说明、Git 状态、端口和 npx 环境。 |

### Phase 5 Runbook Rehearsal 1 — 2026-07-14 21:07–21:09 CST
- **Result:** pass
- Started from reset and completed progress proposal → pre-confirmation fact check → confirmation → evidence-backed question → material proposal → pre-confirmation evidence check → confirmation → dashboard → outsider denial → owner reset.
- Verified dashboard: 1 active opportunity, ¥1.0 亿 amount clue, 1 open action, 0 high risks, 0 pending proposals.
- Verified answer sections: data cutoff, facts/single-source clues, Agent inferences, recommendations, sources, and missing information.
- Verified outsider view: all KPIs became `—`; proposal/answer, facts, business summary, and audit were cleared. The only console errors were the two expected 403 responses for dashboard and snapshot; no JavaScript exception occurred.
- Final reset restored zero contacts/opportunities/actions/materials and the single `demo_seeded` audit.

### Phase 5 Runbook Rehearsal 2 — 2026-07-14 21:10–21:12 CST
- **Result:** pass, with one automation timing observation retained for code review.
- Repeated the complete Runbook from reset through final reset and re-verified confirmation gating, ¥1.0 亿 dashboard amount, evidence-backed answer sections, material evidence after confirmation, and outsider denial.
- The immediate Playwright snapshot emitted by the identity-select command raced the asynchronous denied refresh and still contained the prior fact/audit DOM. After the two expected 403 responses settled (1 second), the outsider view contained no prior sensitive facts or audits and displayed the denial state. No product command was retried unchanged; verification changed to an explicit settled snapshot.
- Final reset passed. Browser CLI evidence is under `agent-backend/output/playwright/rehearsal-2-*.log`; Playwright session snapshots are under `agent-backend/.playwright-cli/`.

### Phase 5 Final Security Verification and Code Review — 2026-07-14 21:36–21:59 CST
- Restarted the application with the latest `app/demo/app.js` and verified the identity selector's immediate DOM state, before denied API responses settled.
- Immediate and settled outsider views contained none of `李总`, `集团数字化建设机会`, material/proposal details, or `proposal_confirmed`; KPI, result, summary, facts, and audit were synchronously cleared.
- Simulated delayed authorized refresh responses followed by a rapid owner → outsider switch; generation checks prevented stale authorized responses from repopulating the outsider DOM.
- Simulated a delayed evidence-backed question response followed by an identity switch; the in-flight answer did not render after the user became unauthorized.
- Extended the identity guard to progress intake, material intake, questions, and proposal confirmation so all sensitive in-flight responses are discarded after an identity change.
- Fixed question handling for confirmed progress without a budget amount and persisted `priority_direction` so the answer does not invent finance/procurement facts for non-matching input.
- Added a SQLite compatibility migration for existing local databases and verified `priority_direction` was added to the existing `data/demo.db` on startup.
- Added regression coverage in `tests/test_question_flow.py`; focused verification passed with 4 tests.
- Code review result: no remaining high-confidence P0 correctness, security, transaction, permission, or documentation issue found.
- Final codebase-memory re-index was attempted, but the MCP server returned `Transport closed`; the prior persisted index artifacts were retained. This does not affect the application or Demo acceptance gates.

### Phase 5 Final Commands — 2026-07-14 21:59 CST
Executed from `agent-backend/` exactly as required:

- `uv sync` — pass; 31 packages resolved, 29 checked.
- `uv run ruff check .` — pass.
- `uv run pytest` — pass; **18 passed**, with the documented Starlette/httpx deprecation warning only.
- `uv run python scripts/smoke_demo.py` — pass; complete offline flow, permission denial, and final reset all passed.
- `uv run uvicorn app.main:app --host 127.0.0.1 --port 8000` — pass.
- Live `GET /health` — HTTP 200 with `mode=offline-demo` and `extractor_provider=demo`.
- Live `GET /demo` — HTTP 200 and page title/content verified.
- Live final `POST /api/demo/reset` — pass; repository returned to the fixed initial state.

### P0 Acceptance Criteria — Final Result
1. **PASS** — `uv run pytest`: 18 passed.
2. **PASS** — `uv run python scripts/smoke_demo.py`: complete offline smoke passed.
3. **PASS** — required Uvicorn command starts successfully on `127.0.0.1:8000`.
4. **PASS** — `/demo` completed progress → proposal → confirmation → question in browser rehearsals.
5. **PASS** — material proposal writes evidence only after explicit confirmation.
6. **PASS** — `u-outsider` receives generic 403 and the browser clears previously loaded customer data immediately.
7. **PASS** — answers show data cutoff, facts/single-source clues, inferences, recommendations, sources, and missing information.
8. **PASS** — no Feishu or OpenAI key/network is required; Fake Feishu Replay + DemoExtractor are the P0 defaults.
9. **PASS** — reset is repeatable; both Runbook rehearsals started and ended with reset, and final live reset passed.
10. **PASS** — no PostgreSQL, RAGFlow, Kafka, Temporal, OCR pipeline, vector database, or independent frontend build was introduced.

### Phase 5 Completion
- **Status:** complete
- Phase 1—5 Exit Gates are complete.
- Two full browser Runbook rehearsals are recorded above.
- P0 is ready for the 2026-07-15 local Demo; P1 remains explicitly unimplemented and documented.
