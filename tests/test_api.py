from __future__ import annotations

from fastapi.testclient import TestClient

from sri_lankan_legal_nlp.api.main import app

client = TestClient(app)


def test_health_and_disclaimer() -> None:
    assert client.get("/health").json() == {"status": "ok"}
    payload = client.get("/").json()
    assert "not legal advice" in payload["disclaimer"]


def test_simplification_endpoint_does_not_invent_english_translation() -> None:
    response = client.post(
        "/simplification/prepare", json={"text": "Legal source text", "language": "en"}
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["translated_sinhala"] is None
    assert payload["simplified_sinhala"] is None
    assert payload["review_status"] == "pending_expert_review"


def test_amendment_endpoint_discloses_candidate_status() -> None:
    response = client.get("/amendments", params={"limit": 1})
    assert response.status_code == 200
    assert response.json()["status"] == "candidates_pending_manual_review"


def test_rejects_unsupported_language() -> None:
    response = client.post("/ner", json={"text": "text", "language": "ta"})
    assert response.status_code == 422
