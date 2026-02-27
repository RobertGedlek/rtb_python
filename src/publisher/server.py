import asyncio
import os
import random
import uuid
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from src.logging_config import get_logger
from src.publisher.config import get_config
from src.publisher.models import BidRequest

env = os.getenv("RTB_ENV", "dev")
config = get_config(env)

logger = get_logger("Publisher")

is_generating = False
generation_task: asyncio.Task | None = None


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info(f"🚀 Publisher starting | env={env} | id={config.publisher_id}")
    logger.info(f"⚙️  Config: host={config.server.host}, port={config.server.port}, "
                f"domain={config.domain}, floor=[{config.min_floor}, {config.max_floor}]")
    yield
    global is_generating, generation_task
    is_generating = False
    if generation_task:
        generation_task.cancel()
    logger.info("🛑 Publisher shutting down")


app = FastAPI(title="RTB Publisher", version="0.1.0", lifespan=lifespan)


def generate_bid_request() -> BidRequest:
    """Creates a random, valid BidRequest object."""
    return BidRequest(
        id=str(uuid.uuid4()),
        domain=config.domain,
        category=config.category,
        bid_floor=round(random.uniform(config.min_floor, config.max_floor), 2)
    )


async def send_bid_request_to_ssp(client: httpx.AsyncClient, bid_request: BidRequest) -> dict | None:
    """Send bid request to SSP and return response."""
    try:
        response = await client.post(config.ssp_url, json=bid_request.to_dict())
        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"⚠️ SSP returned status {response.status_code}")
    except httpx.RequestError as e:
        logger.warning(f"⚠️ Failed to reach SSP at {config.ssp_url}: {e}")
    return None


async def generate_requests_loop():
    """Background loop that continuously generates and sends bid requests."""
    global is_generating
    async with httpx.AsyncClient(timeout=5.0) as client:
        while is_generating:
            bid_request = generate_bid_request()
            logger.info(
                f"📤 Sending BidRequest: ID={bid_request.id[:8]}... | "
                f"domain={bid_request.domain} | floor={bid_request.bid_floor}$"
            )

            result = await send_bid_request_to_ssp(client, bid_request)
            if result:
                status = result.get("status", "unknown")
                if status == "bid_won":
                    winning_bid = result.get("winning_bid", {})
                    logger.info(
                        f"🏆 Bid won! advertiser={winning_bid.get('advertiser_id')} | "
                        f"price={winning_bid.get('bid_price')}$"
                    )
                else:
                    logger.info(f"📭 No winning bid for request {bid_request.id[:8]}...")

            await asyncio.sleep(config.request_interval_ms / 1000.0)


@app.post("/start")
async def start_generating():
    """Start generating bid requests."""
    global is_generating, generation_task
    if is_generating:
        return {"status": "already_running", "publisher_id": config.publisher_id}

    is_generating = True
    generation_task = asyncio.create_task(generate_requests_loop())
    logger.info("▶️ Started generating bid requests")
    return {"status": "started", "publisher_id": config.publisher_id}


@app.post("/stop")
async def stop_generating():
    """Stop generating bid requests."""
    global is_generating, generation_task
    if not is_generating:
        return {"status": "already_stopped", "publisher_id": config.publisher_id}

    is_generating = False
    if generation_task:
        generation_task.cancel()
        generation_task = None
    logger.info("⏹️ Stopped generating bid requests")
    return {"status": "stopped", "publisher_id": config.publisher_id}


@app.post("/send")
async def send_single_request():
    """Send a single bid request to SSP (manual trigger)."""
    bid_request = generate_bid_request()
    logger.info(
        f"📤 Sending single BidRequest: ID={bid_request.id[:8]}... | "
        f"domain={bid_request.domain} | floor={bid_request.bid_floor}$"
    )

    async with httpx.AsyncClient(timeout=5.0) as client:
        result = await send_bid_request_to_ssp(client, bid_request)

    if result:
        return {"status": "sent", "request_id": bid_request.id, "response": result}
    return {"status": "failed", "request_id": bid_request.id}


@app.get("/status")
async def get_status():
    """Get current publisher status."""
    return {
        "publisher_id": config.publisher_id,
        "is_generating": is_generating,
        "domain": config.domain,
        "category": config.category,
        "floor_range": [config.min_floor, config.max_floor],
        "request_interval_ms": config.request_interval_ms,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "env": env, "publisher_id": config.publisher_id}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.publisher.server:app",
        host=config.server.host,
        port=config.server.port,
        workers=config.server.workers,
        log_level=config.server.log_level,
        reload=config.server.reload,
    )
