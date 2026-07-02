import os


class Settings:
    """Runtime configuration, overridable via environment variables."""

    database_url: str = os.getenv(
        "DATABASE_URL", "postgresql+asyncpg://uptime:uptime@db:5432/uptime"
    )
    check_interval_seconds: int = int(os.getenv("CHECK_INTERVAL_SECONDS", "60"))
    request_timeout_seconds: float = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "10"))
    history_limit: int = int(os.getenv("HISTORY_LIMIT", "50"))


settings = Settings()
