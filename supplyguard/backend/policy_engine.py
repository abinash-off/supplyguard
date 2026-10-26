"""Policy catalog and scan decision helpers."""
from .database import get_connection


def list_policies() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT id, name, description, severity, enabled FROM policies ORDER BY id").fetchall()
    return [{**dict(row), "enabled": bool(row["enabled"])} for row in rows]


def apply_policy(scan: dict) -> dict:
    enabled = {policy["id"] for policy in list_policies() if policy["enabled"]}
    findings = [f for f in scan["findings"] if f["rule_id"] in enabled]
    score = min(100, sum({"critical": 40, "high": 25, "medium": 12, "low": 5, "info": 0}[f["severity"]] for f in findings))
    status = "blocked" if any(f["severity"] == "critical" for f in findings) else (
        "attention" if findings else "passed")
    return {**scan, "findings": findings, "risk_score": score, "status": status}
