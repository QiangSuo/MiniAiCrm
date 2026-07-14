# Findings: XERP 2026-07-15 Demo

## Repository State
- 2026-07-14 检查时仓库只有 `README.md` 与 `00`—`06` 规划文档，没有应用代码、依赖文件或测试。
- Git 分支为 `main`，仅有初始文档提交；`.codebase-memory/` 当前未跟踪。
- 原计划目标是“统一 Codex Agent 后端 + 飞书多维表格 + 飞书 Wiki”，传统节奏为技术 Demo 7—10 天。

## Product Invariants From Existing Plans
- 一个统一 Agent 后端，通过 `customer_id` 隔离客户上下文。
- 正式写入前必须生成变更提案，不能静默修改客户正式数据。
- 每个读写动作携带 `customer_id`、`user_id` 并经过权限校验。
- 回答区分事实、单一来源信息、Agent 推断和建议，并提供来源、截止时间和缺失信息。
- 第一版不引入 PostgreSQL、RAGFlow、Kafka、Temporal 或独立管理后台。

## Local Tooling
- Codex CLI：本地检测为 `codex-cli 0.144.3`。
- Python：3.12.13 已安装；系统默认 `python3` 为 3.9.6，因此项目必须由 uv 固定 Python 3.12。
- uv：0.11.9。
- Node：v24.15.0；npm：11.12.1。
- Docker：29.6.1。
- Git：2.54.0。

## Codex CLI Execution Findings
- 本地 `codex exec` 支持从 stdin 读取 prompt、指定工作目录、sandbox、approval policy 和输出最后消息。
- 推荐首次使用：`codex exec -C . -s workspace-write -a never -o .planning/demo-2026-07-15/last-message.md - < PROMPT-CODEX-EXEC-DEMO.md`。
- 续跑使用：`codex exec resume --last "继续执行 AGENTS.md 和 .planning/demo-2026-07-15/task_plan.md，完成下一个未完成 Phase；不要只汇报。"`。
- `codex doctor` 当前报告 provider route probe 超时；这会影响新的 Codex 会话能否工作，应在离开前先验证命令实际能启动。产品 Demo 本身应保持无模型、无网络可运行。

## Compression Strategy
- 明日 Demo 不是把原 5 个阶段全部做完，而是做一个覆盖核心价值的纵向切片。
- 本地 SQLite 和静态 Demo Console 替代真实 Base/Wiki/飞书 UI，Repository/Adapter 接口保留替换空间。
- “复杂文档处理”缩减为资料元数据登记和处理状态；不做 OCR/RAG。
- “经营看板”缩减为 API 聚合和单页 KPI 卡片；不做正式 Base 仪表盘。

## Demo Data
- 客户：`CUST-DEMO-001` / 中国星海集团（可在实现时调整名称但保持单一固定客户）。
- 授权用户：`u-demo-owner`。
- 未授权用户：`u-outsider`。
- 报进展样例沿用原计划：见李总、财务和采购优先、预算约一亿元、月底提交整体方案。
- 问答样例：这个客户目前最关键的三个突破口是什么？
- 资料样例：集团数字化规划.pdf。

## External Dependencies / Human-only Inputs
- 飞书 App ID、Secret、Verification Token、Encrypt Key。
- 飞书 Base token 与 table IDs。
- 飞书管理员完成事件订阅、机器人权限和公网回调配置。
- 如果这些输入在核心 Gate 通过前不可用，Codex 必须跳过真实飞书接入，不得阻塞。

## Phase 3 Browser Exit Gate Findings (2026-07-14 Resume)
- 浏览器重新加载后页面从 SQLite 当前状态正确渲染，favicon 不再产生页面级 404。
- 点击“一键重置”后 KPI、已确认事实、提案和审计均恢复固定初始状态；保留一条固定 medium 风险和 `demo_seeded` 审计。
- 浏览器“报进展”闭环验证：提案创建时 KPI 仍为 0、待确认为 1；确认后关键人/商机/行动事务写入，KPI 变为 1 / ¥1.0亿 / 1，待确认归零并新增确认审计。
- 浏览器“问客户”验证：回答显示数据截止时间、已确认事实/单一来源、Agent 推断、建议动作、缺失信息和来源引用。
- 浏览器“发材料”验证：生成 pending 提案时资料证据仍为 0，待确认 KPI 变为 1，符合确认前不写正式表。
- 浏览器确认材料后资料证据变为 1，提案状态 confirmed，审计新增 proposal_confirmed。
- 切换 `u-outsider` 后 KPI 全部变为“—”，提案/回答区域、经营摘要、事实和审计均清空，仅显示通用“无权访问该客户”；控制台仅有两条预期的 dashboard/snapshot 403 资源错误，无 JavaScript 异常。

## Phase 4 Implementation Findings
- 当前没有 FeishuEventGateway；Phase 4 将以公共 `/api/integrations/feishu/replay` seam 提供确定性本地事件重放，不实现真实飞书凭据与网络调用。
- 当前 `create_app` 直接实例化 `DemoExtractor`。P0 将通过集中 provider factory 和 health/provider 状态明确无 Key 自动回退为 `demo`，但不实现 P1 OpenAI Provider。
- Phase 4 离线 smoke 已覆盖 Fake Feishu 进展/资料重放、确认前不写、确认后写入、问答口径、dashboard、权限拒绝和最终 reset。
- `run_demo.sh` 在独立 8011 端口启动成功，health 明确返回 `extractor_provider=demo`，外部凭据缺失不影响启动。

## Phase 5 Final Review Findings (2026-07-14)
- 浏览器身份切换必须同步清空 KPI、提案/回答、经营摘要、事实和审计；仅等待异步 403 会造成短暂敏感 DOM 残留。
- 仅保护 dashboard/snapshot 刷新不足以覆盖在途问答、提案创建和确认响应；新增身份 generation 后，旧授权响应不会在切换为未授权用户后回写页面。
- `DemoExtractor` 对非固定样例可能生成 `amount_cny=None`。问答层必须跳过不存在的预算事实，不能执行空值除法或把未提及的财务/采购方向写成事实。
- `priority_direction` 现在作为商机事实持久化；SQLite 启动时为旧 Demo 数据库补列，保持已有本地环境可重复启动和 reset。
- 代码审查修复后未发现其他满足高置信门槛的 P0 阻塞问题；Starlette/httpx 弃用 warning 已在 Known Limitations 记录。
