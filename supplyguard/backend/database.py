"""SQLite connection and initialization helpers."""
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .config import ROOT, get_settings


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    path = get_settings().database_path
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def initialize_database() -> None:
    with get_connection() as conn:
        conn.executescript((ROOT / "database" / "schema.sql").read_text(encoding="utf-8"))
        conn.executescript((ROOT / "database" / "seed.sql").read_text(encoding="utf-8"))
