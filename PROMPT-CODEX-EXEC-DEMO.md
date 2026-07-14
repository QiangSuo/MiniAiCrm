请直接执行本仓库的 2026-07-15 XERP Demo 开发计划，不要只做分析或再写一份计划。

必须先读取并遵守：
1. `AGENTS.md`
2. `07-2026-07-15-CodexCLI自主开发Demo计划.md`
3. `.planning/demo-2026-07-15/task_plan.md`
4. `.planning/demo-2026-07-15/findings.md`
5. `.planning/demo-2026-07-15/progress.md`

执行规则：
- 从 task_plan 中第一个 pending Phase 开始，持续实施、测试、修复并更新进度。
- 不要等待飞书凭据或 OpenAI API；默认实现无密钥、离线可运行的本地 Demo。
- 不要扩大范围。先完成全部 P0 Gate，再考虑 P1。
- 每完成一个 Phase，更新 task_plan 和 progress；测试失败必须修复或记录明确阻塞。
- 使用 Python 3.12、FastAPI、uv、SQLite 和单页 Demo Console。
- 禁止 push，禁止危险 Git 命令，保留现有文档和用户改动。
- 最终必须运行 ruff、pytest、smoke demo，并按 Demo Runbook 彩排。

完成目标：让用户在 2026-07-15 打开本机 `/demo`，稳定展示“发材料、报进展、提案确认、问客户、经营概览、权限拒绝”，且可以一键重置后再次演示。
