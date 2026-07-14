# Progress: XERP Post-Demo MVP

## 2026-07-14 — Plan initialized

### Completed
- Confirmed baseline commit `c68d3db` on `main`.
- Confirmed Demo implementation is committed and the previous Demo plan is complete.
- Verified baseline quality: Ruff pass, Pytest 18 passed, offline smoke pass.
- Created `08-Demo后CodexCLI持续开发计划.md` from the actual code baseline.
- Created post-Demo persistent planning files.
- Switched active planning target from `demo-2026-07-15` to `post-demo-mvp`.

### No application code changes
- This step only establishes the post-Demo execution source of truth.
- No Sprint 0 implementation has started yet.

### Current State
- Sprint: 0
- Work package: S0-01
- Status: ready to implement
- External blockers: none for S0

### Next Action
Run baseline Gate, then implement repository contract tests without changing public behavior.

## 2026-07-14 — Plan/control validation

### Completed
- Updated `AGENTS.md` so future Codex sessions follow the post-Demo plan instead of the completed Demo mission.
- Updated `README.md` document index and current milestone status.
- Added `PROMPT-CODEX-EXEC-POST-DEMO.md` as a copy/paste execution prompt.
- Ran `git diff --check`; no whitespace errors.
- Verified `.planning/.active_plan` resolves to all three post-Demo planning files.

### Baseline Revalidation
- `uv run ruff check .`: pass
- `uv run pytest`: 18 passed, 1 known Starlette/httpx deprecation warning
- `uv run python scripts/smoke_demo.py`: pass
