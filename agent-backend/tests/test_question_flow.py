DEMO_CONTEXT = {"customer_id": "CUST-DEMO-001", "user_id": "u-demo-owner"}


def test_question_answer_separates_facts_inferences_recommendations_and_sources(client):
    progress = client.post(
        "/api/intake/progress",
        json={
            **DEMO_CONTEXT,
            "text": "今天拜访了李总。客户希望财务和采购优先，预算约一亿元，月底提交整体方案。",
        },
    ).json()
    client.post(f"/api/proposals/{progress['proposal_id']}/confirm", json=DEMO_CONTEXT)

    response = client.post(
        "/api/questions",
        json={**DEMO_CONTEXT, "question": "这个客户目前最关键的三个突破口是什么？"},
    )

    assert response.status_code == 200
    answer = response.json()
    assert answer["customer_id"] == "CUST-DEMO-001"
    assert answer["data_cutoff"]
    assert len(answer["facts"]) >= 3
    assert all(fact["source_id"] for fact in answer["facts"])
    budget_fact = next(fact for fact in answer["facts"] if "预算" in fact["statement"])
    assert budget_fact["confidence"] == "single_source"
    assert answer["inferences"]
    assert len(answer["recommendations"]) == 3
    assert answer["sources"]
    assert "预算审批状态" in answer["missing_information"]


def test_question_handles_confirmed_progress_without_budget_amount(client):
    progress = client.post(
        "/api/intake/progress",
        json={**DEMO_CONTEXT, "text": "今天与客户沟通了整体方案。"},
    ).json()
    confirmed = client.post(
        f"/api/proposals/{progress['proposal_id']}/confirm", json=DEMO_CONTEXT
    )
    assert confirmed.status_code == 200

    response = client.post(
        "/api/questions",
        json={**DEMO_CONTEXT, "question": "当前有哪些已确认事实？"},
    )

    assert response.status_code == 200
    facts = response.json()["facts"]
    assert facts
    assert all("预算线索为约" not in fact["statement"] for fact in facts)
    assert all("财务和采购" not in fact["statement"] for fact in facts)
