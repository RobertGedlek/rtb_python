"""
Integration test configuration and shared fixtures.
"""
import pathlib
import random
import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from src.ssp.server import app as ssp_app
from src.advertiser.server import app as advertiser_app
from src.publisher.config import PublisherConfig
from src.publisher.models import BidRequest


_THIS_DIR = pathlib.Path(__file__).resolve().parent


def pytest_collection_modifyitems(items):
    """Auto-mark only tests in this folder with @pytest.mark.integration."""
    for item in items:
        if _THIS_DIR in pathlib.Path(item.fspath).resolve().parents:
            item.add_marker(pytest.mark.integration)


@pytest_asyncio.fixture
async def async_client():
    """Async HTTP client for testing the SSP FastAPI server."""
    transport = ASGITransport(app=ssp_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def advertiser_client():
    """Async HTTP client for testing the Advertiser FastAPI server."""
    transport = ASGITransport(app=advertiser_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def publisher_config() -> PublisherConfig:
    """A PublisherConfig for integration testing."""
    return PublisherConfig(
        publisher_id="pub-integration",
        name="IntegrationTestPub",
        domain="integration-test.com",
        category="IAB1",
        min_floor=0.50,
        max_floor=10.00,
    )


@pytest.fixture
def publisher_config_high_floor() -> PublisherConfig:
    """A PublisherConfig with high bid floor range."""
    return PublisherConfig(
        publisher_id="pub-high-floor",
        name="HighFloorPub",
        domain="premium-site.com",
        category="IAB2",
        min_floor=50.00,
        max_floor=100.00,
    )


def generate_bid_request(config: PublisherConfig) -> BidRequest:
    """Generate a BidRequest from a PublisherConfig."""
    return BidRequest(
        id=str(uuid.uuid4()),
        domain=config.domain,
        category=config.category,
        bid_floor=round(random.uniform(config.min_floor, config.max_floor), 2)
    )


def generate_bid_request_payload(
    request_id: str | None = None,
    domain: str = "test.com",
    category: str = "IAB1",
    bid_floor: float = 1.0,
) -> dict:
    """Generate a bid request payload dict for advertiser testing."""
    return {
        "id": request_id or str(uuid.uuid4()),
        "domain": domain,
        "category": category,
        "bid_floor": bid_floor,
    }
