# XERP Customer Intelligence Demo

一个面向 2026-07-15 演示的离线优先纵向切片。默认使用 Python 3.12、FastAPI、SQLite、`uv` 与确定性 `DemoExtractor`，不需要飞书或 OpenAI 密钥，也不访问外网。

## 快速启动

```bash
./scripts/bootstrap.sh
./scripts/run_demo.sh
```

浏览器打开 `http://127.0.0.1:8000/demo`。如需更换端口：

```bash
PORT=8010 ./scripts/run_demo.sh
```

## 验证

```bash
uv run ruff check .
uv run pytest
uv run python scripts/smoke_demo.py
```

Smoke script 使用临时 SQLite 数据库并从 reset 开始，覆盖报进展、确认写入、问客户、发材料、经营概览、权限拒绝和再次重置，不会调用真实飞书或模型 API。

## Demo 身份与固定数据

- 客户：`CUST-DEMO-001` / 中国星海集团
- 授权用户：`u-demo-owner`
- 未授权用户：`u-outsider`
- 默认进展：见李总、财务和采购优先、预算约一亿元、月底提交整体方案
- 默认资料：`集团数字化规划.pdf`

## 公共接口

- `GET /health`
- `GET /demo`
- `POST /api/demo/reset`
- `POST /api/intake/material`
- `POST /api/intake/progress`
- `POST /api/proposals/{proposal_id}/confirm`
- `POST /api/questions`
- `GET /api/customers/{customer_id}/snapshot`
- `GET /api/dashboard`
- `POST /api/integrations/feishu/replay`：本地 Fake Feishu 事件重放

每个业务请求都必须携带 `customer_id` 和 `user_id`。材料与进展只先生成 pending 提案；正式事实只在确认后事务写入，并保留审计记录。

## 离线与可选配置

无需创建 `.env` 即可运行。`GET /health` 的 `extractor_provider` 应为 `demo`。即使本机存在 OpenAI 配置，P0 仍固定走确定性 Provider；真实 OpenAI 与飞书接入属于 P1，不能阻塞本 Demo。

如需准备未来配置，可复制 `.env.example`，但不得提交真实密钥：

```bash
cp .env.example .env
```

根目录和 `agent-backend/` 下的 `.env` 都会被读取；`.env` 与 `.env.*` 已被 Git 忽略，只有占位符 `.env.example` 可提交。

## 设计边界

- 默认 SQLite 是本地事实源，Repository Port 保留替换边界。
- 所有正式写入经 `ProposalEngine` 和人工确认。
- 回答区分事实、单一来源、推断、建议、来源与缺失信息。
- P0 不包含 PostgreSQL、RAG、OCR、复杂文档解析、独立前端、真实飞书或 OpenAI Provider。
