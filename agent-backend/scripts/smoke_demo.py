from __future__ import annotations

import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.config import Settings  # noqa: E402
from app.main import create_app  # noqa: E402

CUSTOMER_ID = "CUST-DEMO-001"
OWNER = "u-demo-owner"
OUTSIDER = "u-outsider"
CONTEXT = {"customer_id": CUSTOMER_ID, "user_id": OWNER}
PROGRESS_TEXT = (
    "今天拜访了李总。客户希望财务和采购优先，预算约一亿元，月底提交整体方案。"
)


def expect(response: Any, status_code: int, label: str) -> dict[str, Any]:
    if response.status_code != status_code:
        raise AssertionError(
            f"{label}: expected {status_code}, got {response.status_code}: {response.text}"
        )
    payload = response.json()
    print(f"PASS  {label}")
    return payload


def run_smoke() -> None:
    with TemporaryDirectory(prefix="xerp-smoke-") as temp_dir:
        settings = Settings(
            _env_file=None,
            database_path=Path(temp_dir) / "demo.db",
            openai_api_key=None,
            openai_base_url=None,
            openai_model=None,
        )
        with TestClient(create_app(settings)) as client:
            health = expect(client.get("/health"), 200, "health")
            assert health["mode"] == "offline-demo"
            assert health["extractor_provider"] == "demo"

            expect(client.post("/api/demo/reset"), 200, "reset")

            progress = expect(
                client.post(
                    "/api/integrations/feishu/replay",
                    json={
                        **CONTEXT,
                        "event_type": "message.text",
                        "intent": "progress",
                        "text": PROGRESS_TEXT,
                    },
                ),
                201,
                "fake Feishu progress replay",
            )["result"]
            before_confirm = expect(
                client.get(
                    f"/api/customers/{CUSTOMER_ID}/snapshot",
                    params={"user_id": OWNER},
                ),
                200,
                "snapshot before progress confirmation",
            )
            assert before_confirm["opportunities"] == []
            assert before_confirm["actions"] == []

            expect(
                client.post(
                    f"/api/proposals/{progress['proposal_id']}/confirm",
                    json=CONTEXT,
                ),
                200,
                "confirm progress proposal",
            )

            answer = expect(
                client.post(
                    "/api/questions",
                    json={
                        **CONTEXT,
                        "question": "这个客户目前最关键的三个突破口是什么？",
                    },
                ),
                200,
                "question with evidence",
            )
            assert answer["data_cutoff"]
            assert answer["facts"] and answer["inferences"]
            assert answer["recommendations"] and answer["sources"]
            assert answer["missing_information"]

            material = expect(
                client.post(
                    "/api/integrations/feishu/replay",
                    json={
                        **CONTEXT,
                        "event_type": "file.received",
                        "intent": "material",
                        "filename": "集团数字化规划.pdf",
                        "description": "客户提供的集团数字化规划。",
                    },
                ),
                201,
                "fake Feishu material replay",
            )["result"]
            pending_snapshot = expect(
                client.get(
                    f"/api/customers/{CUSTOMER_ID}/snapshot",
                    params={"user_id": OWNER},
                ),
                200,
                "snapshot before material confirmation",
            )
            assert pending_snapshot["materials"] == []

            expect(
                client.post(
                    f"/api/proposals/{material['proposal_id']}/confirm",
                    json=CONTEXT,
                ),
                200,
                "confirm material proposal",
            )

            dashboard = expect(
                client.get(
                    "/api/dashboard",
                    params={"customer_id": CUSTOMER_ID, "user_id": OWNER},
                ),
                200,
                "dashboard",
            )
            assert dashboard["active_opportunities"] == 1
            assert dashboard["total_amount_cny"] == 100_000_000
            assert dashboard["open_actions"] == 1
            assert dashboard["pending_proposals"] == 0

            denied = client.get(
                f"/api/customers/{CUSTOMER_ID}/snapshot",
                params={"user_id": OUTSIDER},
            )
            expect(denied, 403, "unauthorized access denied")
            assert denied.json() == {"detail": "无权访问该客户"}

            expect(client.post("/api/demo/reset"), 200, "final reset")
            reset_snapshot = expect(
                client.get(
                    f"/api/customers/{CUSTOMER_ID}/snapshot",
                    params={"user_id": OWNER},
                ),
                200,
                "snapshot after reset",
            )
            assert reset_snapshot["contacts"] == []
            assert reset_snapshot["opportunities"] == []
            assert reset_snapshot["actions"] == []
            assert reset_snapshot["materials"] == []

    print("\nXERP offline smoke demo passed.")


if __name__ == "__main__":
    run_smoke()
