"""SupplyGuard HTTP API."""
from datetime import datetime, timezone
import json
import sqlite3
from pathlib import Path

import jwt
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from .auth import create_access_token, decode_access_token, hash_password, verify_password
from .config import ROOT, get_settings
from .database import get_connection, initialize_database
from .policy_engine import apply_policy, list_policies
from .scanner_engine import scan_files
from .schemas import PolicyOut, ScanCreate, ScanOut, TokenOut, UserCreate, UserLogin, UserOut

settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0", description="Software supply-chain risk scanning API")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=settings.cors_origins != ["*"],
                   allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["Authorization", "Content-Type"])
app.mount("/static", StaticFiles(directory=str(ROOT / "frontend")), name="static")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(ROOT / "frontend" / "index.html")


@app.on_event("startup")
def startup() -> None:
    initialize_database()


def _user_out(row) -> dict:
    return {"id": row["id"], "email": row["email"], "created_at": row["created_at"]}


def current_user(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sign in to continue.", headers={"WWW-Authenticate": "Bearer"})
    try:
        claims = decode_access_token(authorization.split(" ", 1)[1].strip())
        user_id = int(claims["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Your session is invalid or expired.", headers={"WWW-Authenticate": "Bearer"})
    with get_connection() as conn:
        user = conn.execute("SELECT id, email, created_at FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        raise HTTPException(status_code=401, detail="Account no longer exists.")
    return dict(user)


def _token_response(user) -> dict:
    user_dict = _user_out(user)
    return {"access_token": create_access_token(user_dict["id"], user_dict["email"]), "token_type": "bearer", "user": user_dict}


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "service": settings.app_name}


@app.get("/metrics", response_class=PlainTextResponse, include_in_schema=False)
def metrics() -> PlainTextResponse:
    """Expose local demo telemetry in Prometheus text exposition format."""
    body = """# HELP supplyguard_up Application health (1 = healthy).
# TYPE supplyguard_up gauge
supplyguard_up 1
# HELP supplyguard_inventory_skus Number of mock inventory SKUs tracked by the UI.
# TYPE supplyguard_inventory_skus gauge
supplyguard_inventory_skus 5
# HELP supplyguard_shipments_in_transit Number of mock shipments currently in transit.
# TYPE supplyguard_shipments_in_transit gauge
supplyguard_shipments_in_transit 3
# HELP supplyguard_pipeline_stage_count Number of stages in the mock delivery pipeline.
# TYPE supplyguard_pipeline_stage_count gauge
supplyguard_pipeline_stage_count 7
# HELP supplyguard_demo_mode Demo-mode indicator (1 = all cloud state is simulated).
# TYPE supplyguard_demo_mode gauge
supplyguard_demo_mode 1
"""
    return PlainTextResponse(body, media_type="text/plain; version=0.0.4; charset=utf-8")


@app.post("/api/auth/register", response_model=TokenOut, status_code=201)
def register(payload: UserCreate) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    try:
        with get_connection() as conn:
            cursor = conn.execute("INSERT INTO users(email, password_hash, created_at) VALUES (?, ?, ?)",
                                  (payload.email.lower(), hash_password(payload.password), now))
            user = conn.execute("SELECT id, email, created_at FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    return _token_response(user)


@app.post("/api/auth/login", response_model=TokenOut)
def login(payload: UserLogin) -> dict:
    with get_connection() as conn:
        row = conn.execute("SELECT id, email, password_hash, created_at FROM users WHERE email = ?", (payload.email.lower(),)).fetchone()
    if not row or not verify_password(payload.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Email or password is incorrect.")
    return _token_response(row)


@app.get("/api/auth/me", response_model=UserOut)
def me(user: dict = Depends(current_user)) -> dict:
    return user


@app.get("/api/policies", response_model=list[PolicyOut])
def policies(_: dict = Depends(current_user)) -> list[dict]:
    return list_policies()


@app.post("/api/scans", response_model=ScanOut, status_code=201)
def create_scan(payload: ScanCreate, user: dict = Depends(current_user)) -> dict:
    if sum(len(item.content.encode("utf-8")) for item in payload.files) > 5_000_000:
        raise HTTPException(status_code=413, detail="The scan is larger than the 5 MB limit.")
    try:
        result = apply_policy(scan_files([item.model_dump() for item in payload.files]))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    created_at = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        cursor = conn.execute("""INSERT INTO scans(user_id, project_name, source, status, risk_score, files_scanned,
            findings_count, created_at, findings_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user["id"], payload.project_name, payload.source, result["status"], result["risk_score"],
             result["files_scanned"], len(result["findings"]), created_at,
             json.dumps(result["findings"], ensure_ascii=False)))
        scan_id = cursor.lastrowid
    return {"id": scan_id, "project_name": payload.project_name, "source": payload.source,
            "status": result["status"], "risk_score": result["risk_score"],
            "files_scanned": result["files_scanned"], "findings_count": len(result["findings"]),
            "created_at": created_at, "findings": result["findings"]}


def _scan_response(row) -> dict:
    return {"id": row["id"], "project_name": row["project_name"], "source": row["source"],
            "status": row["status"], "risk_score": row["risk_score"], "files_scanned": row["files_scanned"],
            "findings_count": row["findings_count"], "created_at": row["created_at"],
            "findings": json.loads(row["findings_json"])}


@app.get("/api/scans", response_model=list[ScanOut])
def get_scans(user: dict = Depends(current_user), limit: int = 50) -> list[dict]:
    limit = max(1, min(limit, 100))
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM scans WHERE user_id = ? ORDER BY id DESC LIMIT ?", (user["id"], limit)).fetchall()
    return [_scan_response(row) for row in rows]


@app.get("/api/scans/{scan_id}", response_model=ScanOut)
def get_scan(scan_id: int, user: dict = Depends(current_user)) -> dict:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM scans WHERE id = ? AND user_id = ?", (scan_id, user["id"])).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Scan not found.")
    return _scan_response(row)
