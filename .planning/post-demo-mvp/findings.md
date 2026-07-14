# Findings: XERP Post-Demo MVP

## Baseline Snapshot — 2026-07-14

- HEAD: `c68d3db feat: complete offline XERP demo vertical slice`
- Branch: `main`, working tree clean at plan creation start
- Application root: `agent-backend/`
- Stack: Python 3.12, FastAPI, uv, SQLite, static HTML/CSS/JS
- Tests: `18 passed`
- Ruff: pass
- Offline smoke: pass
- One non-blocking Starlette/httpx deprecation warning

## Current Architecture

- `app/main.py` directly composes `SQLiteDemoRepository`, application services, `DemoExtractor` selection, and `FakeFeishuEventGateway`.
- `app/ports/repository.py` defines `DemoRepository`, returning many `dict[str, Any]` values.
- `app/infrastructure/sqlite_repository.py` is a large combined adapter responsible for schema, seeds, permissions, proposals, conflict detection, writes, snapshots, dashboard, and audit.
- `select_progress_extractor()` always chooses `DemoExtractor`, even when OpenAI settings exist.
- `FakeFeishuEventGateway` supports local replay only.
- Materials store metadata only; no file bytes, Drive, parsing, OCR, snippets, or indexing.
- Question answering is deterministic and based on confirmed SQLite facts plus fixed templates.

## Existing Business Invariants

- Business requests carry `customer_id` and `user_id`.
- `PermissionGuard` denies unauthorized access.
- Intake creates pending proposals.
- Formal facts are written only after confirmation.
- SQLite confirmation is transactional.
- Question responses distinguish facts, clues, inference, recommendations, sources, and missing information.

## Main Risks

1. Repository boundary is too Demo-specific and weakly typed for a second adapter.
2. Splitting repository and adding Base simultaneously would make regressions hard to localize.
3. Real Feishu events without idempotency and identity routing could create duplicate or cross-customer writes.
4. Model output without strict schema and proposal confirmation could pollute formal facts.
5. File processing without original-file preservation and task state could lose evidence.
6. Old Demo control files would misdirect future Codex sessions if active plan is not switched.

## Decisions

- Preserve the offline Demo as a permanent adapter/regression path.
- Start with Sprint 0 typed boundaries and contract tests.
- Use adapter replacement, not a rewrite.
- SQLite and Base must share repository contract tests.
- Default test suite never calls real external services.
- Real integration validation is opt-in and may remain pending when credentials are unavailable.
- Do not introduce PostgreSQL, queues, or vector databases without measured evidence.

## Tooling Note

codebase-memory-mcp was attempted during plan preparation but returned `Transport closed`. Local file/AST inspection was used as the documented fallback. Future sessions should retry graph tools first.
