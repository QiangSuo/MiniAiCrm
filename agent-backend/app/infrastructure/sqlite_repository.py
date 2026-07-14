import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEMO_CUSTOMER_ID = "CUST-DEMO-001"
DEMO_CUSTOMER_NAME = "中国星海集团"
DEMO_OWNER_USER_ID = "u-demo-owner"


SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    owner_user_id TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS permissions (
    customer_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    role TEXT NOT NULL,
    PRIMARY KEY (customer_id, user_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS proposals (
    proposal_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    created_by TEXT NOT NULL,
    proposal_type TEXT NOT NULL,
    status TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    conflicts_json TEXT NOT NULL DEFAULT '[]',
    missing_fields_json TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL,
    confirmed_at TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS materials (
    material_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    description TEXT NOT NULL,
    submitted_by TEXT NOT NULL,
    processing_status TEXT NOT NULL,
    source_proposal_id TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS contacts (
    contact_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    influence TEXT NOT NULL,
    source_proposal_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS opportunities (
    opportunity_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    name TEXT NOT NULL,
    stage TEXT NOT NULL,
    amount_cny INTEGER,
    budget_note TEXT NOT NULL,
    confidence TEXT NOT NULL,
    priority_direction TEXT NOT NULL,
    source_proposal_id TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS actions (
    action_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    description TEXT NOT NULL,
    owner_user_id TEXT NOT NULL,
    due_date TEXT,
    status TEXT NOT NULL,
    source_proposal_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS risks (
    risk_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    title TEXT NOT NULL,
    level TEXT NOT NULL,
    status TEXT NOT NULL,
    source_proposal_id TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS audit_logs (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    details_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


class SQLiteDemoRepository:
    def __init__(self, database_path: Path):
        self.database_path = Path(database_path)

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connection() as connection:
            connection.executescript(SCHEMA)
            self._ensure_schema_compatibility(connection)
            connection.commit()
            if not connection.execute("SELECT 1 FROM customers LIMIT 1").fetchone():
                self._seed(connection)
                connection.commit()

    def reset_demo(self) -> dict[str, Any]:
        with self.connection() as connection:
            connection.executescript(SCHEMA)
            self._ensure_schema_compatibility(connection)
            for table in (
                "audit_logs",
                "risks",
                "actions",
                "opportunities",
                "contacts",
                "materials",
                "proposals",
                "permissions",
                "customers",
            ):
                connection.execute(f"DELETE FROM {table}")
            self._seed(connection)
            connection.commit()
        return {
            "status": "reset",
            "customer_id": DEMO_CUSTOMER_ID,
            "customer_name": DEMO_CUSTOMER_NAME,
            "authorized_user_id": DEMO_OWNER_USER_ID,
        }

    def customer_exists(self, customer_id: str) -> bool:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT 1 FROM customers WHERE customer_id = ?", (customer_id,)
            ).fetchone()
        return row is not None

    def user_can_access(self, customer_id: str, user_id: str) -> bool:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT 1 FROM permissions WHERE customer_id = ? AND user_id = ?",
                (customer_id, user_id),
            ).fetchone()
        return row is not None

    def counts(self) -> dict[str, int]:
        with self.connection() as connection:
            return {
                table: int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
                for table in (
                    "customers",
                    "proposals",
                    "materials",
                    "contacts",
                    "opportunities",
                    "actions",
                    "risks",
                    "audit_logs",
                )
            }

    def create_proposal(
        self,
        *,
        proposal_id: str,
        customer_id: str,
        created_by: str,
        proposal_type: str,
        changes: list[dict[str, Any]],
        conflicts: list[dict[str, Any]],
        missing_fields: list[str],
        original_input: dict[str, Any],
    ) -> dict[str, Any]:
        created_at = datetime.now(UTC).isoformat()
        payload = {"changes": changes, "original_input": original_input}
        with self.connection() as connection:
            connection.execute(
                """INSERT INTO proposals(
                    proposal_id, customer_id, created_by, proposal_type, status,
                    payload_json, conflicts_json, missing_fields_json, created_at
                ) VALUES (?, ?, ?, ?, 'pending', ?, ?, ?, ?)""",
                (
                    proposal_id,
                    customer_id,
                    created_by,
                    proposal_type,
                    json.dumps(payload, ensure_ascii=False),
                    json.dumps(conflicts, ensure_ascii=False),
                    json.dumps(missing_fields, ensure_ascii=False),
                    created_at,
                ),
            )
            connection.execute(
                """INSERT INTO audit_logs(
                    customer_id, user_id, action, entity_type, entity_id,
                    details_json, created_at
                ) VALUES (?, ?, 'proposal_created', 'proposal', ?, ?, ?)""",
                (
                    customer_id,
                    created_by,
                    proposal_id,
                    json.dumps({"proposal_type": proposal_type}, ensure_ascii=False),
                    created_at,
                ),
            )
            connection.commit()
        return {
            "proposal_id": proposal_id,
            "customer_id": customer_id,
            "created_by": created_by,
            "proposal_type": proposal_type,
            "status": "pending",
            "changes": changes,
            "conflicts": conflicts,
            "missing_fields": missing_fields,
            "created_at": created_at,
        }

    def get_proposal(self, proposal_id: str) -> dict[str, Any] | None:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT * FROM proposals WHERE proposal_id = ?", (proposal_id,)
            ).fetchone()
        return self._proposal_row(row) if row else None

    def detect_conflicts(
        self, customer_id: str, changes: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        proposed_amount = next(
            (
                change["data"].get("amount_cny")
                for change in changes
                if change["entity_type"] == "opportunity"
            ),
            None,
        )
        if proposed_amount is None:
            return []
        with self.connection() as connection:
            row = connection.execute(
                """SELECT amount_cny FROM opportunities
                WHERE customer_id = ? AND opportunity_id = 'OPP-DEMO-001'""",
                (customer_id,),
            ).fetchone()
        if row and row["amount_cny"] != proposed_amount:
            return [
                {
                    "field": "opportunity.amount_cny",
                    "current": row["amount_cny"],
                    "proposed": proposed_amount,
                    "message": "预算线索与已确认记录不一致，需人工确认",
                }
            ]
        return []

    def confirm_proposal(
        self, proposal_id: str, customer_id: str, user_id: str
    ) -> dict[str, Any]:
        confirmed_at = datetime.now(UTC).isoformat()
        with self.connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT * FROM proposals WHERE proposal_id = ? AND customer_id = ?",
                (proposal_id, customer_id),
            ).fetchone()
            if row is None:
                from app.domain.errors import NotFound

                raise NotFound("提案不存在")
            if row["status"] != "pending":
                from app.domain.errors import ConflictError

                raise ConflictError("提案已处理，不能重复确认")
            payload = json.loads(row["payload_json"])
            for change in payload["changes"]:
                self._apply_change(connection, customer_id, proposal_id, change, confirmed_at)
            connection.execute(
                """UPDATE proposals SET status = 'confirmed', confirmed_at = ?
                WHERE proposal_id = ?""",
                (confirmed_at, proposal_id),
            )
            connection.execute(
                """INSERT INTO audit_logs(
                    customer_id, user_id, action, entity_type, entity_id,
                    details_json, created_at
                ) VALUES (?, ?, 'proposal_confirmed', 'proposal', ?, ?, ?)""",
                (
                    customer_id,
                    user_id,
                    proposal_id,
                    json.dumps(
                        {
                            "proposal_type": row["proposal_type"],
                            "conflicts_acknowledged": json.loads(row["conflicts_json"]),
                        },
                        ensure_ascii=False,
                    ),
                    confirmed_at,
                ),
            )
            connection.commit()
        result = self.get_proposal(proposal_id)
        assert result is not None
        return result

    def customer_snapshot(self, customer_id: str) -> dict[str, Any]:
        with self.connection() as connection:
            customer = connection.execute(
                """SELECT customer_id, name, owner_user_id, created_at
                FROM customers WHERE customer_id = ?""",
                (customer_id,),
            ).fetchone()
            if customer is None:
                from app.domain.errors import NotFound

                raise NotFound("客户不存在")
            return {
                "customer": dict(customer),
                "materials": self._rows(
                    connection,
                    """SELECT material_id, filename, description, submitted_by,
                    processing_status, source_proposal_id, created_at
                    FROM materials WHERE customer_id = ? ORDER BY created_at""",
                    customer_id,
                ),
                "contacts": self._rows(
                    connection,
                    """SELECT contact_id, name, role, influence, source_proposal_id, created_at
                    FROM contacts WHERE customer_id = ? ORDER BY created_at""",
                    customer_id,
                ),
                "opportunities": self._rows(
                    connection,
                    """SELECT opportunity_id, name, stage, amount_cny, budget_note,
                    confidence, priority_direction, source_proposal_id, updated_at
                    FROM opportunities WHERE customer_id = ? ORDER BY updated_at""",
                    customer_id,
                ),
                "actions": self._rows(
                    connection,
                    """SELECT action_id, description, owner_user_id, due_date, status,
                    source_proposal_id, created_at
                    FROM actions WHERE customer_id = ? ORDER BY created_at""",
                    customer_id,
                ),
                "risks": self._rows(
                    connection,
                    """SELECT risk_id, title, level, status, source_proposal_id, created_at
                    FROM risks WHERE customer_id = ? ORDER BY created_at""",
                    customer_id,
                ),
                "proposals": self._proposal_rows(connection, customer_id),
                "audit_logs": self._audit_rows(connection, customer_id),
            }

    def dashboard(self, customer_id: str) -> dict[str, Any]:
        today = datetime.now(UTC).date().isoformat()
        with self.connection() as connection:
            customer = connection.execute(
                "SELECT name FROM customers WHERE customer_id = ?", (customer_id,)
            ).fetchone()
            opportunities = connection.execute(
                """SELECT COUNT(*) AS count, COALESCE(SUM(amount_cny), 0) AS total
                FROM opportunities WHERE customer_id = ? AND stage != 'closed'""",
                (customer_id,),
            ).fetchone()
            open_actions = connection.execute(
                """SELECT COUNT(*) FROM actions
                WHERE customer_id = ? AND status = 'open'""",
                (customer_id,),
            ).fetchone()[0]
            overdue_actions = connection.execute(
                """SELECT COUNT(*) FROM actions
                WHERE customer_id = ? AND status = 'open'
                AND due_date IS NOT NULL AND due_date < ?""",
                (customer_id, today),
            ).fetchone()[0]
            high_risks = connection.execute(
                """SELECT COUNT(*) FROM risks
                WHERE customer_id = ? AND status = 'open' AND level = 'high'""",
                (customer_id,),
            ).fetchone()[0]
            pending_rows = connection.execute(
                """SELECT proposal_id, proposal_type, created_by, created_at,
                conflicts_json FROM proposals
                WHERE customer_id = ? AND status = 'pending'
                ORDER BY created_at DESC""",
                (customer_id,),
            ).fetchall()
        pending_items = [
            {
                "proposal_id": row["proposal_id"],
                "proposal_type": row["proposal_type"],
                "created_by": row["created_by"],
                "created_at": row["created_at"],
                "conflict_count": len(json.loads(row["conflicts_json"])),
            }
            for row in pending_rows
        ]
        customer_name = customer["name"] if customer else customer_id
        amount = int(opportunities["total"])
        return {
            "customer_count": 1 if customer else 0,
            "active_opportunities": int(opportunities["count"]),
            "total_amount_cny": amount,
            "open_actions": int(open_actions),
            "overdue_actions": int(overdue_actions),
            "high_risks": int(high_risks),
            "pending_proposals": len(pending_items),
            "pending_proposal_items": pending_items,
            "weekly_summary": (
                f"{customer_name}当前有{int(opportunities['count'])}个活跃商机，"
                f"金额线索约{amount // 10_000}万元；"
                f"{int(open_actions)}项行动待推进，{len(pending_items)}个提案待确认。"
            ),
            "generated_at": datetime.now(UTC).isoformat(),
        }

    @staticmethod
    def _ensure_schema_compatibility(connection: sqlite3.Connection) -> None:
        opportunity_columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(opportunities)").fetchall()
        }
        if "priority_direction" not in opportunity_columns:
            connection.execute(
                "ALTER TABLE opportunities ADD COLUMN priority_direction TEXT "
                "NOT NULL DEFAULT '业务方向待确认'"
            )

    def _apply_change(
        self,
        connection: sqlite3.Connection,
        customer_id: str,
        proposal_id: str,
        change: dict[str, Any],
        timestamp: str,
    ) -> None:
        data = change["data"]
        entity_type = change["entity_type"]
        if entity_type == "material":
            connection.execute(
                """INSERT INTO materials(
                    material_id, customer_id, filename, description, submitted_by,
                    processing_status, source_proposal_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    data["material_id"],
                    customer_id,
                    data["filename"],
                    data["description"],
                    data["submitted_by"],
                    data["processing_status"],
                    proposal_id,
                    timestamp,
                ),
            )
        elif entity_type == "contact":
            connection.execute(
                """INSERT INTO contacts(
                    contact_id, customer_id, name, role, influence,
                    source_proposal_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(contact_id) DO UPDATE SET
                    name = excluded.name,
                    role = excluded.role,
                    influence = excluded.influence,
                    source_proposal_id = excluded.source_proposal_id,
                    created_at = excluded.created_at""",
                (
                    data["contact_id"],
                    customer_id,
                    data["name"],
                    data["role"],
                    data["influence"],
                    proposal_id,
                    timestamp,
                ),
            )
        elif entity_type == "opportunity":
            connection.execute(
                """INSERT INTO opportunities(
                    opportunity_id, customer_id, name, stage, amount_cny, budget_note,
                    confidence, priority_direction, source_proposal_id, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(opportunity_id) DO UPDATE SET
                    name = excluded.name,
                    stage = excluded.stage,
                    amount_cny = excluded.amount_cny,
                    budget_note = excluded.budget_note,
                    confidence = excluded.confidence,
                    priority_direction = excluded.priority_direction,
                    source_proposal_id = excluded.source_proposal_id,
                    updated_at = excluded.updated_at""",
                (
                    data["opportunity_id"],
                    customer_id,
                    data["name"],
                    data["stage"],
                    data.get("amount_cny"),
                    data["budget_note"],
                    data["confidence"],
                    data.get("priority_direction", "业务方向待确认"),
                    proposal_id,
                    timestamp,
                ),
            )
        elif entity_type == "action":
            connection.execute(
                """INSERT INTO actions(
                    action_id, customer_id, description, owner_user_id, due_date,
                    status, source_proposal_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(action_id) DO UPDATE SET
                    description = excluded.description,
                    owner_user_id = excluded.owner_user_id,
                    due_date = excluded.due_date,
                    status = excluded.status,
                    source_proposal_id = excluded.source_proposal_id,
                    created_at = excluded.created_at""",
                (
                    data["action_id"],
                    customer_id,
                    data["description"],
                    data["owner_user_id"],
                    data.get("due_date"),
                    data["status"],
                    proposal_id,
                    timestamp,
                ),
            )
        else:
            raise ValueError(f"Unsupported proposal entity type: {entity_type}")

    @staticmethod
    def _rows(
        connection: sqlite3.Connection, sql: str, customer_id: str
    ) -> list[dict[str, Any]]:
        return [dict(row) for row in connection.execute(sql, (customer_id,)).fetchall()]

    def _proposal_rows(
        self, connection: sqlite3.Connection, customer_id: str
    ) -> list[dict[str, Any]]:
        rows = connection.execute(
            "SELECT * FROM proposals WHERE customer_id = ? ORDER BY created_at DESC",
            (customer_id,),
        ).fetchall()
        return [self._proposal_row(row) for row in rows]

    @staticmethod
    def _proposal_row(row: sqlite3.Row) -> dict[str, Any]:
        payload = json.loads(row["payload_json"])
        return {
            "proposal_id": row["proposal_id"],
            "customer_id": row["customer_id"],
            "created_by": row["created_by"],
            "proposal_type": row["proposal_type"],
            "status": row["status"],
            "changes": payload["changes"],
            "conflicts": json.loads(row["conflicts_json"]),
            "missing_fields": json.loads(row["missing_fields_json"]),
            "created_at": row["created_at"],
            "confirmed_at": row["confirmed_at"],
        }

    @staticmethod
    def _audit_rows(
        connection: sqlite3.Connection, customer_id: str
    ) -> list[dict[str, Any]]:
        rows = connection.execute(
            """SELECT audit_id, user_id, action, entity_type, entity_id,
            details_json, created_at FROM audit_logs
            WHERE customer_id = ? ORDER BY audit_id DESC""",
            (customer_id,),
        ).fetchall()
        return [
            {
                "audit_id": row["audit_id"],
                "user_id": row["user_id"],
                "action": row["action"],
                "entity_type": row["entity_type"],
                "entity_id": row["entity_id"],
                "created_at": row["created_at"],
                "details": json.loads(row["details_json"]),
            }
            for row in rows
        ]

    def _seed(self, connection: sqlite3.Connection) -> None:
        now = datetime.now(UTC).isoformat()
        connection.execute(
            """INSERT INTO customers(
                customer_id, name, owner_user_id, created_at
            ) VALUES (?, ?, ?, ?)""",
            (DEMO_CUSTOMER_ID, DEMO_CUSTOMER_NAME, DEMO_OWNER_USER_ID, now),
        )
        connection.execute(
            "INSERT INTO permissions(customer_id, user_id, role) VALUES (?, ?, ?)",
            (DEMO_CUSTOMER_ID, DEMO_OWNER_USER_ID, "owner"),
        )
        connection.execute(
            """INSERT INTO risks(
                risk_id, customer_id, title, level, status, source_proposal_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                "RISK-DEMO-001",
                DEMO_CUSTOMER_ID,
                "预算和决策链仍需客户正式确认",
                "medium",
                "open",
                None,
                now,
            ),
        )
        connection.execute(
            """INSERT INTO audit_logs(
                customer_id, user_id, action, entity_type, entity_id, details_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                DEMO_CUSTOMER_ID,
                "system",
                "demo_seeded",
                "customer",
                DEMO_CUSTOMER_ID,
                json.dumps({"mode": "offline-demo"}, ensure_ascii=False),
                now,
            ),
        )
