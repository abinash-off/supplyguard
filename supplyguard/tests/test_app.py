"""Scanner and API smoke tests."""
import json

from fastapi.testclient import TestClient

from backend.main import app
from backend.scanner_engine import scan_files


def test_detects_unpinned_requirements_and_missing_lockfile():
    report = scan_files([{"path": "requirements.txt", "content": "fastapi\nuvicorn==0.30.0\n"}])
    ids = {finding["rule_id"] for finding in report["findings"]}
    assert "SG-DEPS-001" in ids
    assert "SG-LOCK-001" in ids


def test_rejects_traversal_paths():
    try:
        scan_files([{"path": "../secrets.txt", "content": "password=not-a-real-secret"}])
    except ValueError:
        return
    raise AssertionError("Expected traversal path to be rejected")


def test_health_and_authenticated_scan(tmp_path, monkeypatch):
    from backend.config import get_settings

    get_settings().database_path = tmp_path / "test.db"
    with TestClient(app) as client:
        assert client.get("/api/health").status_code == 200
        registered = client.post("/api/auth/register", json={"email": "scanner@example.com", "password": "a-secure-password"})
        assert registered.status_code == 201
        token = registered.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/api/scans", headers=headers, json={
            "project_name": "demo", "files": [{"path": "package.json", "content": json.dumps({"dependencies": {"demo": "*"}})}]
        })
        assert response.status_code == 201
        assert response.json()["findings_count"] >= 1
        assert client.get("/api/scans", headers=headers).json()[0]["project_name"] == "demo"
