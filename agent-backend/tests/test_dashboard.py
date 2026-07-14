DEMO_CONTEXT = {"customer_id": "CUST-DEMO-001", "user_id": "u-demo-owner"}


def test_dashboard_aggregates_opportunity_actions_risks_and_pending_proposals(client):
    pending_material = client.post(
        "/api/intake/material",
        json={
            **DEMO_CONTEXT,
            "filename": "集团数字化规划.pdf",
            "description": "客户材料",
        },
    ).json()
    progress = client.post(
        "/api/intake/progress",
        json={
            **DEMO_CONTEXT,
            "text": "今天拜访了李总。财务和采购优先，预算约一亿元，月底提交整体方案。",
        },
    ).json()
    client.post(f"/api/proposals/{progress['proposal_id']}/confirm", json=DEMO_CONTEXT)

    response = client.get("/api/dashboard", params=DEMO_CONTEXT)

    assert response.status_code == 200
    dashboard = response.json()
    assert dashboard["customer_count"] == 1
    assert dashboard["active_opportunities"] == 1
    assert dashboard["total_amount_cny"] == 100_000_000
    assert dashboard["open_actions"] == 1
    assert dashboard["overdue_actions"] == 0
    assert dashboard["high_risks"] == 0
    assert dashboard["pending_proposals"] == 1
    assert dashboard["pending_proposal_items"][0]["proposal_id"] == pending_material["proposal_id"]
    assert "中国星海集团" in dashboard["weekly_summary"]


def test_dashboard_rejects_unauthorized_user(client):
    response = client.get(
        "/api/dashboard",
        params={"customer_id": "CUST-DEMO-001", "user_id": "u-outsider"},
    )

    assert response.status_code == 403
