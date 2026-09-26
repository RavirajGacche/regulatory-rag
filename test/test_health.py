from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_ready_reports_checks() -> None:
    r = client.get("/ready")
    assert r.status_code == 200
    assert "postgres" in r.json()["checks"]


def test_unknown_path_is_404() -> None:
    assert client.get("/nope").status_code == 404
