import time
import threading

import httpx

from src.logging_config import setup_logging, get_logger
from src.ssp.config import get_config as get_ssp_config
from src.advertiser.config import get_config as get_advertiser_config
from src.publisher.config import get_config as get_publisher_config

setup_logging()
logger = get_logger("Simulation")


def start_ssp_server():
    """Start the SSP server in a background thread."""
    import uvicorn
    from src.ssp.server import app

    config = get_ssp_config()
    uvicorn.run(
        app,
        host=config.server.host,
        port=config.server.port,
        log_level=config.server.log_level,
    )


def start_advertiser_server():
    """Start the Advertiser server in a background thread."""
    import uvicorn
    from src.advertiser.server import app

    config = get_advertiser_config()
    uvicorn.run(
        app,
        host=config.server.host,
        port=config.server.port,
        log_level=config.server.log_level,
    )


def start_publisher_server():
    """Start the Publisher server in a background thread."""
    import uvicorn
    from src.publisher.server import app

    config = get_publisher_config()
    uvicorn.run(
        app,
        host=config.server.host,
        port=config.server.port,
        log_level=config.server.log_level,
    )


def wait_for_server(name: str, base_url: str, timeout: float = 10.0, interval: float = 0.3) -> bool:
    """Poll server /health endpoint until it responds or timeout is reached."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            resp = httpx.get(f"{base_url}/health", timeout=1.0)
            if resp.status_code == 200:
                logger.info(f"✅ {name} ready: {resp.json()}")
                return True
        except httpx.ConnectError:
            pass
        time.sleep(interval)

    logger.error(f"❌ {name} failed to start within {timeout}s")
    return False


def start_publisher_traffic(pub_url: str) -> bool:
    """Start generating bid requests on the publisher server."""
    try:
        resp = httpx.post(f"{pub_url}/start", timeout=5.0)
        if resp.status_code == 200:
            logger.info(f"▶️ Publisher started generating traffic: {resp.json()}")
            return True
    except httpx.RequestError as e:
        logger.error(f"❌ Failed to start publisher traffic: {e}")
    return False


if __name__ == "__main__":
    ssp_config = get_ssp_config()
    adv_config = get_advertiser_config()
    pub_config = get_publisher_config()

    ssp_url = f"http://{ssp_config.server.host}:{ssp_config.server.port}"
    adv_url = f"http://{adv_config.server.host}:{adv_config.server.port}"
    pub_url = f"http://{pub_config.server.host}:{pub_config.server.port}"

    # Start all servers in daemon threads
    threading.Thread(target=start_advertiser_server, daemon=True).start()
    threading.Thread(target=start_ssp_server, daemon=True).start()
    threading.Thread(target=start_publisher_server, daemon=True).start()

    # Wait for all servers to be ready
    logger.info("⏳ Waiting for Advertiser server...")
    if not wait_for_server("Advertiser", adv_url):
        logger.error("Aborting — Advertiser server not available")
        raise SystemExit(1)

    logger.info("⏳ Waiting for SSP server...")
    if not wait_for_server("SSP", ssp_url):
        logger.error("Aborting — SSP server not available")
        raise SystemExit(1)

    logger.info("⏳ Waiting for Publisher server...")
    if not wait_for_server("Publisher", pub_url):
        logger.error("Aborting — Publisher server not available")
        raise SystemExit(1)

    # Start generating bid requests
    logger.info("🚀 Starting simulation...")
    if not start_publisher_traffic(pub_url):
        logger.error("Aborting — could not start publisher traffic")
        raise SystemExit(1)

    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 Simulation stopped")