DEMO_CONTEXT = {"customer_id": "CUST-DEMO-001", "user_id": "u-demo-owner"}


def snapshot(client):
    return client.get(
        "/api/customers/CUST-DEMO-001/snapshot", params={"user_id": "u-demo-owner"}
    ).json()


def test_material_requires_confirmation_before_evidence_is_written(client):
    before = snapshot(client)
    assert before["materials"] == []

    proposed = client.post(
        "/api/intake/material",
        json={
            **DEMO_CONTEXT,
            "filename": "集团数字化规划.pdf",
            "description": "这是今天客户给的集团数字化规划。",
        },
    )

    assert proposed.status_code == 201
    proposal = proposed.json()
    assert proposal["proposal_type"] == "material"
    assert proposal["status"] == "pending"
    assert proposal["changes"][0]["entity_type"] == "material"
    assert snapshot(client)["materials"] == []

    confirmed = client.post(
        f"/api/proposals/{proposal['proposal_id']}/confirm", json=DEMO_CONTEXT
    )

    assert confirmed.status_code == 200
    assert confirmed.json()["status"] == "confirmed"
    materials = snapshot(client)["materials"]
    assert len(materials) == 1
    assert materials[0]["filename"] == "集团数字化规划.pdf"
    assert materials[0]["processing_status"] == "archived"
    assert materials[0]["source_proposal_id"] == proposal["proposal_id"]


def test_proposal_cannot_be_confirmed_twice(client):
    proposal = client.post(
        "/api/intake/material",
        json={
            **DEMO_CONTEXT,
            "filename": "集团数字化规划.pdf",
            "description": "客户材料",
        },
    ).json()
    first = client.post(f"/api/proposals/{proposal['proposal_id']}/confirm", json=DEMO_CONTEXT)
    second = client.post(f"/api/proposals/{proposal['proposal_id']}/confirm", json=DEMO_CONTEXT)

    assert first.status_code == 200
    assert second.status_code == 409
    assert len(snapshot(client)["materials"]) == 1
