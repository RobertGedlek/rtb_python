import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.logging_config import get_logger
from src.ssp.config import get_config
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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom handler for request validation errors — returns clear RTB-style error messages."""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"],
        })

    logger.warning(f"🚫 Invalid BidRequest received: {errors}")
    return JSONResponse(
        status_code=422,
        content={
            "status": "rejected",
            "reason": "validation_error",
            "errors": errors,
        },
    )


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
