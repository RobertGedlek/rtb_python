import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from src.logging_config import get_logger
from src.ssp.config import get_config
from src.ssp.exception_handlers import validation_exception_handler
from src.ssp.models import BidRequestIn

env = os.getenv("RTB_ENV", "dev")
config = get_config(env)

logger = get_logger("SSP-Server")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info(f"🚀 SSP Server starting | env={env} | seat={config.seat_id}")
    logger.info(f"⚙️  Config: host={config.server.host}, port={config.server.port}, "
                f"workers={config.server.workers}, timeout={config.max_bid_response_time_ms}ms")
    yield
    logger.info("🛑 SSP Server shutting down")


app = FastAPI(title="RTB SSP Receiver", version="0.1.0", lifespan=lifespan)
app.add_exception_handler(RequestValidationError, validation_exception_handler)


@app.post("/bid/request")
async def receive_bid_request(bid_request: BidRequestIn):
    """Receive and validate a BidRequest from a publisher."""
    logger.info(
        f"📥 Received BidRequest: ID={bid_request.id[:8]}... | "
        f"domain={bid_request.domain} | category={bid_request.category} | "
        f"floor={bid_request.bid_floor}$"
    )

    return {"status": "received", "id": bid_request.id}


@app.get("/health")
async def health_check():
    """Health check endpoint for GCP load balancer / readiness probe."""
    return {"status": "ok", "env": env, "seat_id": config.seat_id}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.ssp.server:app",
        host=config.server.host,
        port=config.server.port,
        workers=config.server.workers,
        log_level=config.server.log_level,
        reload=config.server.reload,
    )
