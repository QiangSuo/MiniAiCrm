def test_unauthorized_user_cannot_read_customer_data(client):
    response = client.get(
        "/api/customers/CUST-DEMO-001/snapshot", params={"user_id": "u-outsider"}
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "无权访问该客户"}
    assert "中国星海集团" not in response.text


def test_unauthorized_user_cannot_create_or_confirm_proposals(client):
    created = client.post(
        "/api/intake/progress",
        json={
            "customer_id": "CUST-DEMO-001",
            "user_id": "u-outsider",
            "text": "预算约一亿元",
        },
    )

    assert created.status_code == 403


def test_customer_context_cannot_cross_reference_another_customer(client):
    response = client.post(
        "/api/questions",
        json={
            "customer_id": "CUST-OTHER-999",
            "user_id": "u-demo-owner",
            "question": "客户情况？",
        },
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "无权访问该客户"}
