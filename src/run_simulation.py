import time
import threading
from concurrent.futures import ThreadPoolExecutor

import httpx
import requests

from src.logging_config import setup_logging, get_logger
from src.publisher.config import PublisherConfig
from src.publisher.engine import Publisher
from src.ssp.config import get_config

# Initialize central logging configuration
setup_logging()
logger = get_logger("Simulation")


def start_ssp_server():
    """Start the SSP server in a background thread."""
    import uvicorn
    from src.ssp.server import app

    config = get_config()

    uvicorn.run(
        app,
        host=config.server.host,
        port=config.server.port,
        log_level=config.server.log_level,
    )


def wait_for_ssp(base_url: str, timeout: float = 10.0, interval: float = 0.3) -> bool:
    """Poll SSP /health endpoint until it responds or timeout is reached."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            resp = httpx.get(f"{base_url}/health", timeout=1.0)
            if resp.status_code == 200:
                logger.info(f"✅ SSP server ready: {resp.json()}")
                return True
        except httpx.ConnectError:
            pass
        time.sleep(interval)

    logger.error(f"❌ SSP server failed to start within {timeout}s")
    return False


def run_simulation(publisher: Publisher, interval: float = 1.0):
    """Loop sending requests to SSP."""
    publisher.logger.info(f"🚀 Starting traffic: {publisher.config.domain} -> {publisher.config.target_url}")

    try:
        while True:
            request_obj = publisher.generate_single_request()

            try:
                response = requests.post(
                    publisher.config.target_url,
                    json=request_obj.to_dict(),
                    timeout=0.5
                )

                if response.status_code in [200, 204]:
                    publisher.logger.info(f"✅ OK | ID: {request_obj.id[:8]}... | Floor: {request_obj.bid_floor}$")
                else:
                    publisher.logger.warning(f"⚠️ Server returned error: {response.status_code}")

            except requests.exceptions.RequestException as e:
                publisher.logger.error(f"❌ No connection to SSP: {e}")

            time.sleep(interval)
    except KeyboardInterrupt:
        publisher.logger.info(f"🛑 Stopped: {publisher.config.name}")


def start_publishers():
    """Start all publishers in parallel threads."""
    configs = [
        PublisherConfig("TechBlog", "tech-world.com", "technology", 1.5, 4.0),
        PublisherConfig("SportPortal", "fast-sports.pl", "sports", 0.5, 1.2),
        PublisherConfig("NewsSite", "daily-news.com", "news", 0.1, 0.8),
    ]

    with ThreadPoolExecutor(max_workers=len(configs)) as executor:
        for cfg in configs:
            pub = Publisher(cfg)
            executor.submit(run_simulation, pub, 2.0)


if __name__ == "__main__":
    config = get_config()
    base_url = f"http://{config.server.host}:{config.server.port}"

    # Start SSP server in a daemon thread (stops when main process exits)
    server_thread = threading.Thread(target=start_ssp_server, daemon=True)
    server_thread.start()

    # Poll /health
    logger.info("⏳ Waiting for SSP server to become ready...")
    if not wait_for_ssp(base_url):
        logger.error("Aborting simulation — SSP server not available")
        raise SystemExit(1)

    logger.info("🚀 Starting publishers...")
    start_publishers()