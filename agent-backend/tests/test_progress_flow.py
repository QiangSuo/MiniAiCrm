DEMO_CONTEXT = {"customer_id": "CUST-DEMO-001", "user_id": "u-demo-owner"}
PROGRESS_TEXT = "今天拜访了李总。客户希望财务和采购优先，预算约一亿元，月底提交整体方案。"


def get_snapshot(client):
    response = client.get(
        "/api/customers/CUST-DEMO-001/snapshot", params={"user_id": "u-demo-owner"}
    )
    assert response.status_code == 200
    return response.json()


def test_progress_proposal_writes_contact_opportunity_and_action_only_after_confirm(client):
    proposed = client.post(
        "/api/intake/progress", json={**DEMO_CONTEXT, "text": PROGRESS_TEXT}
    )

    assert proposed.status_code == 201
    proposal = proposed.json()
    assert proposal["proposal_type"] == "progress"
    assert proposal["status"] == "pending"
    assert {item["entity_type"] for item in proposal["changes"]} == {
        "contact",
        "opportunity",
        "action",
    }
    assert "李总职位" in proposal["missing_fields"]
    before = get_snapshot(client)
    assert before["contacts"] == []
    assert before["opportunities"] == []
    assert before["actions"] == []

    confirmed = client.post(
        f"/api/proposals/{proposal['proposal_id']}/confirm", json=DEMO_CONTEXT
    )

    assert confirmed.status_code == 200
    after = get_snapshot(client)
    assert after["contacts"][0]["name"] == "李总"
    assert after["opportunities"][0]["amount_cny"] == 100_000_000
    assert after["opportunities"][0]["confidence"] == "single_source"
    assert after["actions"][0]["due_date"] == "2026-07-31"
    assert any(log["action"] == "proposal_confirmed" for log in after["audit_logs"])


def test_progress_budget_conflict_is_shown_instead_of_silent_overwrite(client):
    first = client.post(
        "/api/intake/progress", json={**DEMO_CONTEXT, "text": PROGRESS_TEXT}
    ).json()
    client.post(f"/api/proposals/{first['proposal_id']}/confirm", json=DEMO_CONTEXT)

    second = client.post(
        "/api/intake/progress",
        json={
            **DEMO_CONTEXT,
            "text": "再次沟通李总，预算约八千万元，月底提交整体方案。",
        },
    )

    assert second.status_code == 201
    conflicts = second.json()["conflicts"]
    assert conflicts == [
        {
            "field": "opportunity.amount_cny",
            "current": 100_000_000,
            "proposed": 80_000_000,
            "message": "预算线索与已确认记录不一致，需人工确认",
        }
    ]
    assert get_snapshot(client)["opportunities"][0]["amount_cny"] == 100_000_000
