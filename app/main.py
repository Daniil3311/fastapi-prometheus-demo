from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Path
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy.orm import Session

from app.db import Base, engine, get_db
from app.logging_config import setup_logging
from app.metrics import MetricsMiddleware, increment_warning
from app.models import Message
from app.schemas import ProcessRequest, ProcessResponse

setup_logging()
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize schema and seed mock messages at startup."""
    Base.metadata.create_all(bind=engine)

    with Session(engine) as db:
        existing_count = db.query(Message).count()
        if existing_count < 10:
            db.query(Message).delete()
            db.add_all(
                [
                    Message(id=i, text=f"Mock message #{i}")
                    for i in range(1, 11)
                ]
            )
            db.commit()
            logger.info("db_seeded", extra={"records": 10})

    yield


def create_app() -> FastAPI:
    """Create and configure FastAPI application instance."""
    app = FastAPI(title="fastapi-prometheus-demo", lifespan=lifespan)
    app.add_middleware(MetricsMiddleware)

    @app.get("/health")
    def health() -> dict[str, str]:
        logger.info("health_check")
        return {"status": "healthy"}

    @app.get("/message/{id}")
    def get_message(
        id: int = Path(ge=1, le=1_000_000),
        db: Session = Depends(get_db),
    ) -> dict[str, str | int]:
        message = db.get(Message, id)
        if not message:
            logger.warning("message_not_found", extra={"message_id": id})
            raise HTTPException(status_code=404, detail="Message not found")

        logger.info("message_read", extra={"message_id": id})
        return {"id": message.id, "text": message.text}

    @app.post("/process", response_model=ProcessResponse)
    def process(payload: ProcessRequest) -> ProcessResponse:
        start = time.perf_counter()

        delay = 0.5
        if "slow" in payload.data.lower():
            delay = 1.2

        time.sleep(delay)
        elapsed = time.perf_counter() - start
        if elapsed > 1.0:
            logger.warning("slow_processing", extra={"latency_seconds": round(elapsed, 3)})
            increment_warning()

        logger.info("payload_processed", extra={"payload_size": len(payload.data)})
        return ProcessResponse(echo=payload.data, processing_seconds=round(elapsed, 3))

    Instrumentator(should_group_status_codes=False).instrument(app).expose(
        app,
        endpoint="/metrics",
        include_in_schema=False,
    )

    return app


app = create_app()
