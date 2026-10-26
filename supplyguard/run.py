"""Run SupplyGuard locally or in a container: python run.py."""
import os
from pathlib import Path

import uvicorn
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parent


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def main() -> None:
    # Read local settings before selecting the listening socket. The API loads
    # .env too, but that happens after Uvicorn has already picked its host/port.
    load_dotenv(ROOT / ".env")
    host = os.getenv("APP_HOST", "127.0.0.1").strip() or "127.0.0.1"
    port = int(os.getenv("PORT", os.getenv("APP_PORT", "5050")))
    reload = _as_bool(os.getenv("APP_RELOAD"), default=False)

    # 0.0.0.0 is a bind address, not a browser destination.
    print(f"SupplyGuard listening on {host}:{port}", flush=True)
    print(f"Open http://127.0.0.1:{port}/ in a browser on this machine.", flush=True)
    uvicorn.run("backend.main:app", host=host, port=port, reload=reload, app_dir=str(ROOT))


if __name__ == "__main__":
    main()
