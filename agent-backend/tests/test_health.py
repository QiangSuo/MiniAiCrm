def test_health_reports_offline_ready(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "xerp-demo",
        "mode": "offline-demo",
        "extractor_provider": "demo",
    }


def test_demo_page_is_available(client):
    response = client.get("/demo")

    assert response.status_code == 200
    assert "XERP 客户情报控制台" in response.text


def test_reset_restores_seed_customer(client):
    response = client.post("/api/demo/reset")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "reset"
    assert payload["customer_id"] == "CUST-DEMO-001"


def test_health_reports_deterministic_extractor_without_api_key(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["extractor_provider"] == "demo"
