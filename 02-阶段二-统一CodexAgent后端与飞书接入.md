# 阶段二：统一 Codex Agent 后端与飞书接入

## 1. 阶段目标

建设一个统一 Agent 后端，负责接入飞书机器人、识别客户上下文、调用模型、读写飞书多维表格、生成变更提案和处理飞书卡片确认。

本阶段不建设复杂后台，不做多 Agent 平台，只做一个可维护的统一服务。

## 2. 建议周期

4-7 天。

本阶段由 Codex 主要负责后端骨架、飞书事件接收、BaseRepository、卡片渲染和工具层实现；你负责提供飞书应用配置、Base token、表字段 ID、机器人入群和回调地址配置。

## 3. 后端职责边界

统一 Codex Agent 后端负责：

- 接收飞书消息事件、文件事件和卡片回调。
- 识别客户上下文。
- 校验用户权限和资料密级。
- 调用模型做意图识别、结构化抽取、摘要和回答。
- 封装飞书多维表格读写工具。
- 生成变更提案。
- 用户确认后写入正式表。
- 推送回复、卡片、提醒和周报。

后端不负责：

- 替代飞书 Wiki 做文档编辑器。
- 替代飞书多维表格做人工管理界面。
- 直接把模型输出写入正式表。
- 在第一版承担复杂 BI、复杂全文检索或复杂审批流。

## 4. 推荐技术栈

任选一种团队熟悉的后端栈：

| 方案 | 适合情况 |
| --- | --- |
| Python FastAPI | 更适合文档解析、模型调用、结构化抽取、后续 AI 能力扩展 |
| Node.js / TypeScript | 更适合飞书 SDK、前端同栈、卡片交互和工程化团队 |

第一版可以采用单体服务：

```text
agent-backend
├── feishu_event_gateway
├── customer_context_router
├── permission_guard
├── agent_orchestrator
├── tool_registry
├── base_repository
├── wiki_drive_repository
├── document_processing
├── proposal_engine
├── card_renderer
└── scheduler
```

## 5. 模块设计

### M1：FeishuEventGateway

职责：

- 接收飞书消息事件。
- 接收文件和图片资源事件。
- 接收卡片按钮回调。
- 验证飞书请求签名。
- 将飞书事件转换为内部标准事件。

内部事件示例：

```json
{
  "event_type": "message.text",
  "chat_id": "oc_xxx",
  "user_id": "ou_xxx",
  "message_id": "om_xxx",
  "text": "今天见了李总，预算约1亿，月底前要方案",
  "created_at": "2026-07-14T10:00:00+08:00"
}
```

验收标准：

- 能接收群消息。
- 能接收单聊消息。
- 能获取文件资源信息。
- 能处理卡片按钮点击。

### M2：CustomerContextRouter

职责：

- 群聊场景：`chat_id -> customer_id`。
- 单聊场景：`user_id + conversation_id -> current_customer_id`。
- 无上下文时要求用户选择客户。
- 每次工具调用都必须带 `customer_id`。

数据来源：

- `客户` 表中的 `客户作战群ID` 字段。
- 后端轻量状态存储。
- 单聊客户选择卡片。

验收标准：

- 客户作战群里无需手动选择客户。
- 单聊中必须明确显示当前客户。
- 无客户上下文时不能写入正式表。

### M3：PermissionGuard

职责：

- 判断用户是否属于客户团队。
- 判断用户是否有管理者权限。
- 判断用户是否能访问某密级资料。
- 限制跨客户分析能力。
- 所有 Base 查询和写入前都先校验权限。

第一版权限来源：

- `客户` 表的客户负责人和客户团队字段。
- 手工维护的角色配置。
- 敏感客户单独配置。

验收标准：

- 普通客户团队不能读取未授权客户。
- 严格保密资料不能进入无权限用户的回答上下文。
- 权限失败时给出明确提示。

### M4：BaseRepository

职责：

- 封装飞书多维表格 API。
- 按真实表 ID、字段 ID 读写记录。
- 提供统一方法给工具层调用。

建议接口：

```text
get_customer(customer_id)
list_evidence(customer_id, filters)
create_evidence(record)
list_interactions(customer_id, filters)
create_interaction(record)
list_stakeholders(customer_id, filters)
upsert_stakeholder(record)
list_opportunities(customer_id, filters)
update_opportunity(record)
list_actions(customer_id, filters)
create_action(record)
list_risks(customer_id, filters)
create_risk(record)
create_proposal(record)
update_proposal_status(proposal_id, status)
```

验收标准：

- 读写逻辑不散落在 Agent 提示词里。
- 表名、字段名和 ID 有配置文件管理。
- 写入失败能记录错误并回传给用户。

### M5：ToolRegistry

职责：

- 给 Agent 暴露受控工具。
- 区分只读工具、提交型工具和确认后执行工具。
- 禁止模型直接写正式表。

只读工具：

```text
get_customer_profile(customer_id)
search_customer_evidence(customer_id, query)
get_stakeholder_map(customer_id)
get_opportunity_list(customer_id)
get_recent_interactions(customer_id)
get_open_actions(customer_id)
get_customer_risks(customer_id)
```

提交型工具：

```text
create_material_proposal(...)
create_interaction_proposal(...)
create_stakeholder_proposal(...)
create_opportunity_proposal(...)
create_action_proposal(...)
create_risk_proposal(...)
```

确认后执行工具：

```text
commit_proposal(proposal_id, approved_payload)
reject_proposal(proposal_id, reason)
save_raw_only(proposal_id)
```

验收标准：

- Agent 只能生成提案。
- 正式写入必须由卡片确认触发。
- 工具调用全量记录日志。

### M6：AgentOrchestrator

职责：

- 识别用户意图。
- 调用相应工具。
- 组织模型上下文。
- 输出结构化提案或回答。

意图分类：

```text
资料归档
商务进展更新
客户问答
客户切换
周报请求
行动查询
风险查询
无法识别
```

验收标准：

- 同一条消息能识别是“报进展”还是“问客户”。
- 无证据时不编造。
- 回答中区分事实、单一来源信息、Agent 推断和建议。

### M7：ProposalEngine

职责：

- 把 Agent 抽取结果转换为变更提案。
- 与现有 Base 数据做冲突检查。
- 生成飞书确认卡片。
- 用户确认后写入正式表。

冲突类型：

```text
同一商机预算不一致
同一关键人职位不一致
商机阶段回退或跳跃
行动截止日期冲突
风险等级变化
资料密级冲突
```

验收标准：

- 有冲突时不能直接写入。
- 卡片展示拟新增、拟修改、冲突和待确认字段。
- 提案状态可追踪。

### M8：CardRenderer

职责：

- 生成飞书交互卡片。
- 支持确认、修改、拒绝、仅保存原始记录。
- 卡片中展示客户、证据来源、变更内容和风险提示。

卡片类型：

```text
资料归档确认卡
商务进展确认卡
新增关键人确认卡
商机更新确认卡
行动承诺确认卡
风险提示确认卡
客户选择卡
周报确认卡
```

验收标准：

- 业务人员能快速理解卡片。
- 按钮回调能更新提案状态。
- 卡片操作失败时给出明确提示。

### M9：WikiDriveRepository

职责：

- 获取或保存飞书云盘文件链接。
- 维护客户 Wiki 链接。
- 第一版只做资料索引和客户首页链接，不做复杂整页重写。

验收标准：

- 原始文件能追溯。
- 资料证据表能保存文件链接。
- Wiki 只作为展示层，不作为唯一事实库。

### M10：DocumentProcessingPipeline

职责：

- 保存原始文件和来源信息。
- 判断文档复杂度。
- 创建和更新文档处理任务。
- 对简单文档做轻量文本提取、摘要和候选事实抽取。
- 对复杂文档标记为异步解析，不阻塞用户。
- 将关键页、章节、表格或摘录写入文档片段索引。
- 解析失败时保留原始资料，并标记为需人工处理。

建议抽象接口：

```text
DocumentStorage
DocumentParser
RetrievalProvider
```

第一版实现：

```text
DocumentStorage：飞书云盘 / 飞书附件链接
DocumentParser：简单文本抽取 + 模型摘要 + 人工确认
RetrievalProvider：资料证据表 + 文档片段索引表
```

未来可替换：

```text
DocumentStorage：MinIO / 企业对象存储
DocumentParser：OCR / 版面分析 / 专业解析服务
RetrievalProvider：RAGFlow / 向量库 / OpenSearch
```

验收标准：

- 上传复杂文档后，用户立即收到“已保存，正在解析”的反馈。
- 资料证据表中能看到解析状态。
- 文档处理任务表中能看到处理步骤、错误和重试次数。
- 解析失败不影响原始文件保全。

### M11：Scheduler

职责：

- 定时生成周报。
- 扫描逾期行动。
- 扫描高风险事项。
- 推送提醒。

第一版可用简单定时任务，不需要 Temporal。

## 6. 阶段实施步骤

1. 创建飞书企业自建应用。
2. 开通机器人能力和消息事件订阅。
3. 建设后端服务骨架。
4. 实现飞书事件接收和卡片回调。
5. 实现 `chat_id -> customer_id` 路由。
6. 实现 BaseRepository 读写 8 张核心表。
7. 实现资料证据扩展字段、文档处理任务和文档片段索引读写。
8. 实现 ToolRegistry。
9. 实现变更提案卡片。
10. 完成端到端测试。

## 7. Codex 开发任务拆分

| 任务 | 交付物 | 人工验收点 |
| --- | --- | --- |
| 后端项目骨架 | 可启动服务、配置加载、健康检查 | 本地能启动 |
| 飞书事件网关 | 文本消息、文件消息、卡片回调接口 | 飞书事件能打到后端 |
| BaseRepository | 读取客户表、写入变更提案表 | 能读写真实 Base |
| 文档处理流水线 | 保存资料证据、创建解析任务、更新解析状态 | 复杂文档不会阻塞主流程 |
| 客户上下文路由 | `chat_id -> customer_id` | 群聊能识别客户 |
| 权限校验占位 | 用户、客户、密级校验入口 | 无权限时能阻止 |
| 卡片渲染 | 提案确认卡片 | 卡片可点击并回调 |
| 工具注册 | 只读工具、提交型工具、确认工具 | Agent 不能绕过提案直接写正式表 |

## 8. 阶段验收标准

- 机器人能加入客户作战群。
- 群消息能到达后端。
- 后端能识别客户上下文。
- 后端能读取客户、商机、行动、风险等 Base 记录。
- 后端能创建变更提案。
- 飞书卡片按钮能触发确认或拒绝。
- 确认后能写入正式表。
- 所有工具调用和写入动作有日志。
- 端到端样例可重复运行，不依赖手工改代码。
- 上传复杂文档时能创建文档处理任务，并在资料证据表更新解析状态。

## 9. 阶段风险

| 风险 | 应对 |
| --- | --- |
| 飞书事件和卡片回调调试成本高 | 先做最小文本消息和一个确认卡片 |
| Base 字段 ID 变化导致写入失败 | 配置化管理表 ID 和字段 ID，启动时校验 |
| Agent 提案太自由 | 用严格 JSON schema 和字段枚举约束输出 |
| 权限校验遗漏 | BaseRepository 入口统一走 PermissionGuard |
| 模型输出不稳定 | 正式写入前强制人工确认 |
