import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from src.logging_config import get_logger
from src.ssp.config import get_config

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


@app.post("/bid/request")
async def receive_bid_request(request: Request):
    # Receive raw JSON
    data = await request.json()

    # For now, just log the fact that we received it
    logger.info(f"📥 Received BidRequest: ID={data.get('id')[:8]}... from domain {data.get('domain')}")

    # Return empty status 204 (No Content) - typical in RTB when we're not bidding yet
    return {"status": "received"}


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
