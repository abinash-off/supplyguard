"""Environment-backed application settings."""
from functools import lru_cache
from pathlib import Path
import os
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


class Settings:
    app_name: str = os.getenv("APP_NAME", "SupplyGuard")
    secret_key: str = os.getenv("SECRET_KEY", "change-this-secret-before-deploying")
    token_expire_minutes: int = int(os.getenv("TOKEN_EXPIRE_MINUTES", "720"))
    database_path: Path = Path(os.getenv("DATABASE_PATH", str(ROOT / "supplyguard.db"))).expanduser()
    cors_origins: list[str] = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "*").split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
