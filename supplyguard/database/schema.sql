PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    project_name TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'web-upload',
    status TEXT NOT NULL CHECK (status IN ('passed', 'attention', 'blocked')),
    risk_score INTEGER NOT NULL CHECK (risk_score BETWEEN 0 AND 100),
    files_scanned INTEGER NOT NULL,
    findings_count INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    findings_json TEXT NOT NULL DEFAULT '[]'
);

CREATE INDEX IF NOT EXISTS idx_scans_user_created ON scans(user_id, created_at DESC);

CREATE TABLE IF NOT EXISTS policies (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    severity TEXT NOT NULL,
    enabled INTEGER NOT NULL DEFAULT 1 CHECK (enabled IN (0, 1))
);
