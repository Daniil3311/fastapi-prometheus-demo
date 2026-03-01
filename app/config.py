from __future__ import annotations

import os


class Settings:
    """Application settings loaded from environment variables."""

    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://app:app@localhost:5432/app",
    )
    app_name: str = "fastapi-prometheus-demo"
    log_file: str = os.getenv("LOG_FILE", "app.log")


settings = Settings()
