from fastapi import FastAPI, Request
from src.logging_config import get_logger

logger = get_logger("SSP-Server")

app = FastAPI(title="RTB SSP Receiver")

@app.post("/bid/request")
async def receive_bid_request(request: Request):
    # Receive raw JSON
    data = await request.json()

    # For now, just log the fact that we received it
    logger.info(f"📥 Received BidRequest: ID={data.get('id')[:8]}... from domain {data.get('domain')}")

    # Return empty status 204 (No Content) - typical in RTB when we're not bidding yet
    return {"status": "received"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)