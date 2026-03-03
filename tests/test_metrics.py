from __future__ import annotations


def test_metrics_exposed(client):
    client.get("/health")
    client.get("/message/1")
    client.post("/process", json={"data": "slow payload"})

    response = client.get("/metrics")
    assert response.status_code == 200

    body = response.text
    assert "app_requests_total" in body
    assert "app_request_latency_seconds_bucket" in body
    assert "app_warnings_total" in body
