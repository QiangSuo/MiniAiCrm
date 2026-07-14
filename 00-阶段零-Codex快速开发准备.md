# 阶段零：Codex 快速开发准备

## 1. 阶段目标

在正式开发前，先为 Codex 建好稳定的开发上下文、项目骨架、配置清单和验收样例。

这一步的目的不是做业务功能，而是避免后续每次都从零解释项目，让 Codex 能持续、快速、可控地开发。

## 2. 建议周期

1-2 天。

## 3. 分工方式

| 角色 | 职责 |
| --- | --- |
| 你 | 确认技术栈、飞书应用权限、Base 表结构、客户样例、业务验收标准 |
| Codex | 创建项目骨架、配置文件、开发说明、测试脚本、接口占位和任务清单 |
| 飞书管理员 | 如需要，协助创建自建应用、机器人权限、事件订阅、Base 和 Wiki 授权 |

## 4. 技术栈决策

阶段零必须先确定后端栈：

| 选项 | 适合情况 |
| --- | --- |
| Python FastAPI | 更适合文档解析、AI 工作流、结构化抽取和后续检索能力 |
| Node.js / TypeScript | 更适合飞书 SDK、卡片交互、前端同栈和工程化团队 |

建议：

```text
如果你没有明确团队偏好，优先 Python FastAPI。
```

原因：

- 后续文档解析、结构化抽取、模型调用更顺手。
- 单人开发时脚本和调试效率较高。
- 可以较容易补充测试脚本和离线样例。

## 5. 项目骨架

建议目录：

```text
agent-backend/
  app/
    main.py
    config/
    feishu/
    base/
    agent/
    tools/
    proposals/
    cards/
    scheduler/
    common/
  tests/
  samples/
  docs/
  scripts/
  .env.example
  README.md
  AGENTS.md
```

目录职责：

| 目录 | 职责 |
| --- | --- |
| `feishu/` | 飞书事件、消息、卡片、文件资源 |
| `base/` | 多维表格读写、表字段映射、记录转换 |
| `agent/` | 意图识别、模型调用、结构化抽取、问答 |
| `tools/` | Agent 可调用的受控工具 |
| `proposals/` | 变更提案、冲突检测、确认后写入 |
| `cards/` | 飞书交互卡片渲染 |
| `scheduler/` | 周报、逾期提醒、风险提醒 |
| `samples/` | 本地测试用消息、提案、Base 数据样例 |
| `docs/` | 技术设计、接口说明、部署说明 |

## 6. 配置清单

阶段零需要准备 `.env.example`，至少包含：

```text
FEISHU_APP_ID=
FEISHU_APP_SECRET=
FEISHU_VERIFICATION_TOKEN=
FEISHU_ENCRYPT_KEY=

XERP_BASE_TOKEN=
CUSTOMER_TABLE_ID=
EVIDENCE_TABLE_ID=
INTERACTION_TABLE_ID=
STAKEHOLDER_TABLE_ID=
OPPORTUNITY_TABLE_ID=
ACTION_TABLE_ID=
RISK_TABLE_ID=
PROPOSAL_TABLE_ID=

OPENAI_API_KEY=
MODEL_NAME=

APP_BASE_URL=
LOG_LEVEL=
```

真实密钥不写入文档和仓库。

## 7. Codex 开发约束

建议创建 `AGENTS.md` 或同等开发约束文档，写清楚：

```text
1. 第一版不引入 PostgreSQL。
2. 第一版不引入 RAGFlow、Kafka、Temporal。
3. 所有正式写入必须先生成变更提案。
4. Agent 不能直接静默写客户正式表。
5. BaseRepository 是唯一读写多维表格的入口。
6. 每个工具调用都必须带 customer_id 和 user_id。
7. 权限校验必须在后端做，不能只靠提示词。
8. 回答必须区分事实、单一来源信息、推断和建议。
9. 每个开发任务必须附带本地样例或测试方式。
```

## 8. 验收样例

阶段零要准备三类样例，后续每个功能都用这些样例回归。

### 样例一：发材料

```text
用户上传文件：集团数字化规划.pdf
用户说明：这是今天客户给的集团数字化规划。

预期：
生成资料归档提案。
确认后写入资料证据表。
```

### 样例二：报进展

```text
今天见了李总。他表示集团今年先做财务和采购，预算大约在一亿元左右，要求我们月底前提交整体方案。

预期：
生成接触记录、商机线索、行动承诺提案。
关键字段需要确认。
确认后写入 Base。
```

### 样例三：问客户

```text
这个客户目前最关键的三个突破口是什么？

预期：
读取客户、商机、关键人、行动、风险和证据。
回答附来源、数据截止时间和缺失信息。
```

## 9. 每日开发节奏

Codex 单人开发建议按“每天一个可验收闭环”推进：

| 天数 | 建议目标 |
| --- | --- |
| Day 1 | 项目骨架、配置、README、开发约束 |
| Day 2 | Base 表字段映射、客户表读取、样例数据 |
| Day 3 | 飞书消息事件接收和文本回复 |
| Day 4 | `chat_id -> customer_id` 路由和权限占位 |
| Day 5 | 变更提案表写入和确认卡片 |
| Day 6-7 | 资料归档闭环 |
| Day 8-10 | 报进展闭环 |
| Day 11-14 | 客户问答闭环 |
| Day 15-20 | 周报、提醒、试运行修正 |

## 10. 阶段验收标准

- 后端项目可以本地启动。
- 配置项完整。
- Base 表 ID 和字段 ID 有配置位置。
- 三个验收样例已写入 `samples/` 或文档。
- Codex 开发约束已明确。
- 第一批开发任务已拆成可执行小任务。
- 你能清楚判断每个小任务是否完成。

## 11. 阶段风险

| 风险 | 应对 |
| --- | --- |
| Codex 一次性改太多 | 每次只给一个闭环或一个模块，要求测试和说明 |
| 外部配置不全导致卡住 | 阶段零先列出飞书、Base、模型配置清单 |
| 业务验收样例不清 | 先固定 3 个样例，后续都围绕样例回归 |
| 代码能跑但不符合业务 | 你每天只验收业务闭环，不只看代码完成度 |
