DEMO_CONTEXT = {"customer_id": "CUST-DEMO-001", "user_id": "u-demo-owner"}
PROGRESS_TEXT = (
    "今天拜访了李总。客户希望财务和采购优先，预算约一亿元，月底提交整体方案。"
)


def test_fake_feishu_progress_event_creates_pending_proposal(client):
    response = client.post(
        "/api/integrations/feishu/replay",
        json={
            **DEMO_CONTEXT,
            "event_type": "message.text",
            "intent": "progress",
            "text": PROGRESS_TEXT,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["adapter"] == "fake-feishu"
    assert body["event_type"] == "message.text"
    assert body["result"]["proposal_type"] == "progress"
    assert body["result"]["status"] == "pending"


def test_fake_feishu_file_event_requires_confirmation_before_material_write(client):
    replayed = client.post(
        "/api/integrations/feishu/replay",
        json={
            **DEMO_CONTEXT,
            "event_type": "file.received",
            "intent": "material",
            "filename": "集团数字化规划.pdf",
            "description": "客户提供的集团数字化规划。",
        },
    )

    assert replayed.status_code == 201
    proposal = replayed.json()["result"]
    snapshot = client.get(
        "/api/customers/CUST-DEMO-001/snapshot",
        params={"user_id": "u-demo-owner"},
    ).json()
    assert snapshot["materials"] == []

    confirmed = client.post(
        f"/api/proposals/{proposal['proposal_id']}/confirm", json=DEMO_CONTEXT
    )
    assert confirmed.status_code == 200
    snapshot = client.get(
        "/api/customers/CUST-DEMO-001/snapshot",
        params={"user_id": "u-demo-owner"},
    ).json()
    assert snapshot["materials"][0]["filename"] == "集团数字化规划.pdf"


def test_fake_feishu_replay_rejects_unauthorized_user(client):
    response = client.post(
        "/api/integrations/feishu/replay",
        json={
            "customer_id": "CUST-DEMO-001",
            "user_id": "u-outsider",
            "event_type": "message.text",
            "intent": "question",
            "text": "这个客户目前最关键的三个突破口是什么？",
        },
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "无权访问该客户"}
