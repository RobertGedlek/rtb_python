import asyncio
import os
import random
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.logging_config import get_logger
from src.advertiser.config import get_config_2
from src.advertiser.models import BidResponse
from src.ssp.models import BidRequestIn

env = os.getenv("RTB_ENV", "dev")
config = get_config_2(env)

logger = get_logger("Advertiser2")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info(f"🚀 Advertiser 2 starting | env={env} | id={config.advertiser_id}")
    logger.info(f"⚙️  Config: host={config.server.host}, port={config.server.port}, "
                f"delay={config.response_delay_ms}ms, bid_range=[{config.min_bid}, {config.max_bid}]")
    yield
    logger.info("🛑 Advertiser 2 shutting down")


app = FastAPI(title="RTB Advertiser 2 (DSP)", version="0.1.0", lifespan=lifespan)


@app.post("/bid", response_model=BidResponse)
async def handle_bid_request(bid_request: BidRequestIn):
    """Process incoming bid request and return a bid response."""
    logger.info(
        f"📥 Received bid request: ID={bid_request.id[:8]}... | "
        f"domain={bid_request.domain} | floor={bid_request.bid_floor}$"
    )

    await asyncio.sleep(config.response_delay_ms / 1000.0)

    bid_price = round(random.uniform(config.min_bid, config.max_bid), 2)

    response = BidResponse(
        request_id=bid_request.id,
        advertiser_id=config.advertiser_id,
        bid_price=bid_price,
        ad_id=str(uuid.uuid4()),
    )

    logger.info(
        f"📤 Sending bid response: ID={bid_request.id[:8]}... | "
        f"price={bid_price}$ | ad={response.ad_id[:8]}..."
    )

    return response


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "env": env, "advertiser_id": config.advertiser_id}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.advertiser.server2:app",
        host=config.server.host,
        port=config.server.port,
        workers=config.server.workers,
        log_level=config.server.log_level,
        reload=config.server.reload,
    )

