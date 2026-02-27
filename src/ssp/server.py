import asyncio
import os
from contextlib import asynccontextmanager

import httpx
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


async def fetch_bid_from_advertiser(client: httpx.AsyncClient, url: str, bid_data: dict) -> dict | None:
    """Send bid request to a single advertiser and return response."""
    try:
        response = await client.post(url, json=bid_data)
        if response.status_code == 200:
            return response.json()
    except httpx.RequestError as e:
        logger.warning(f"⚠️ Failed to reach advertiser {url}: {e}")
    return None


@app.post("/bid/request")
async def receive_bid_request(bid_request: BidRequestIn):
    """Receive and validate a BidRequest from a publisher, forward to advertisers."""
    logger.info(
        f"📥 Received BidRequest: ID={bid_request.id[:8]}... | "
        f"domain={bid_request.domain} | category={bid_request.category} | "
        f"floor={bid_request.bid_floor}$"
    )

    bid_data = bid_request.model_dump()
    timeout_sec = config.max_bid_response_time_ms / 1000.0

    async with httpx.AsyncClient(timeout=timeout_sec) as client:
        tasks = [
            fetch_bid_from_advertiser(client, url, bid_data)
            for url in config.advertiser_urls
        ]
        responses = await asyncio.gather(*tasks)

    valid_bids = [r for r in responses if r is not None and r.get("bid_price", 0) >= bid_request.bid_floor]

    if not valid_bids:
        logger.info(f"📭 No valid bids for request {bid_request.id[:8]}...")
        return {"status": "no_bid", "id": bid_request.id}

    winning_bid = max(valid_bids, key=lambda x: x["bid_price"])
    logger.info(
        f"🏆 Winning bid: advertiser={winning_bid['advertiser_id']} | "
        f"price={winning_bid['bid_price']}$ | ad={winning_bid['ad_id'][:8]}..."
    )

    return {
        "status": "bid_won",
        "id": bid_request.id,
        "winning_bid": winning_bid,
    }


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
