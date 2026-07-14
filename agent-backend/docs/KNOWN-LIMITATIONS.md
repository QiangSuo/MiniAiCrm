# XERP Demo Known Limitations

## P0 已知限制

- 仅提供本地单机 Demo，SQLite 是事实库；没有生产部署、高可用、备份或并发容量承诺。
- 固定演示客户为 `CUST-DEMO-001`，权限身份为本地种子；没有真实 SSO、完整 RBAC、多租户或组织同步。
- `DemoExtractor` 使用确定性规则，只保证固定中文样例；它不是通用自然语言理解或生产模型能力。
- `FakeFeishuEventGateway` 只提供本地事件重放；没有真实飞书签名校验、事件订阅、机器人回复、Base 或云盘 API。
- 材料只登记文件名、说明与归档状态；不读取文件字节，不做 OCR、PDF/PPT/Excel 解析、全文检索或 RAG。
- 问答基于 SQLite 中已确认事实和固定推断模板；不会检索外部数据，也不会自动更新事实。
- 预算线索保留 `single_source` 置信度；Demo 不替代客户正式预算、采购或合同确认。
- 冲突只覆盖当前演示字段和预算样例；没有通用合并策略、版本历史或人工修改界面。
- 日期与固定样例面向 2026-07-15 Demo；不是可配置的生产业务日历或任务系统。
- TestClient 目前会显示 Starlette 关于 httpx 兼容层的弃用 warning；测试与运行结果不受影响，P0 不为消除 warning 升级依赖栈。

## P1 候选项（未实现）

- 最小真实飞书消息、卡片确认和 Base Adapter。
- OpenAI 兼容结构化抽取 Provider，以及超时、重试、脱敏和成本控制。
- Dockerfile、更丰富的周报卡片与真实通知。

## 明确不在本 Demo 范围

- PostgreSQL、Redis、Kafka、Temporal、RAGFlow、向量数据库。
- 复杂文档解析、Wiki 自动建页、云盘下载和 12 张 Base 表全量同步。
- 生产级权限、审计导出、数据迁移、正式监控和独立 React/Vue 前端。
