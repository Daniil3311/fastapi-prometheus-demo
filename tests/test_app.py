from __future__ import annotations


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_get_message_ok(client):
    response = client.get("/message/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_get_message_not_found(client):
    response = client.get("/message/999")
    assert response.status_code == 404


def test_process(client):
    response = client.post("/process", json={"data": "hello"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["echo"] == "hello"
    assert payload["processing_seconds"] >= 0.5
