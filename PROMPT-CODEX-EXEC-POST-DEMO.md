请直接执行本仓库的 Demo 后持续开发计划，不要只做分析或再写一份重复计划。

必须先读取并遵守：
1. `AGENTS.md`
2. `08-Demo后CodexCLI持续开发计划.md`
3. `.planning/.active_plan` 指向目录中的 `task_plan.md`
4. 同目录 `findings.md`
5. 同目录 `progress.md`

执行规则：
- 先检查 `git status --short --branch`、当前 HEAD 和最近提交，保护用户已有改动。
- 先运行当前基线测试，再从 task plan 第一个未完成的 P0 工作包开始。
- 按“实现 → 测试 → 修复 → 更新 planning 文件 → 本地 checkpoint”持续执行。
- 每个 Sprint 的 Exit Gate 全绿后才能进入下一 Sprint。
- 外部飞书或模型凭据不可用时，不要等待：使用 Port、Fake/Mock、脱敏 fixture 和 contract test 继续；真实沙箱验收标记为 pending。
- 永久保留 SQLite、`DemoExtractor`、`FakeFeishuEventGateway`、`/demo` 和 `scripts/smoke_demo.py` 离线回退路径。
- 默认测试不得调用真实外部 API，不得真实消耗模型额度。
- 不要提交密钥，不要 push，不要使用危险 Git 命令，不要覆盖用户改动。
- 只有涉及真实外部副作用、安全/权限/数据删除、不可逆迁移或无法本地替代的硬阻塞时才询问用户。

当前第一任务：Sprint 0 / S0-01，冻结现有 SQLite 行为并建立仓储 contract tests。不要从真实飞书或模型接入开始。
