from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def client() -> TestClient:
    base_dir = Path(__file__).resolve().parent
    db_file = base_dir / "test.db"
    log_file = base_dir / "test.log"

    os.environ["DATABASE_URL"] = f"sqlite:///{db_file.as_posix()}"
    os.environ["LOG_FILE"] = log_file.as_posix()

    for module_name in ["app.config", "app.db", "app.main"]:
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])

    from app.main import create_app

    app = create_app()
    with TestClient(app) as test_client:
        yield test_client

    if db_file.exists():
        db_file.unlink()
    if log_file.exists():
        log_file.unlink()
