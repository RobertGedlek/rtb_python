"""
Integration test configuration and shared fixtures.
"""
import pathlib
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from src.ssp.server import app
from src.publisher.config import PublisherConfig
from src.publisher.engine import Publisher


_THIS_DIR = pathlib.Path(__file__).resolve().parent

def pytest_collection_modifyitems(items):
    """Auto-mark only tests in this folder with @pytest.mark.integration."""
    for item in items:
        if _THIS_DIR in pathlib.Path(item.fspath).resolve().parents:
            item.add_marker(pytest.mark.integration)


@pytest_asyncio.fixture
async def async_client():
    """Async HTTP client for testing the SSP FastAPI server."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def publisher() -> Publisher:
    """A Publisher instance configured for integration testing."""
    config = PublisherConfig(
        name="IntegrationTestPub",
        domain="integration-test.com",
        category="IAB1",
        min_floor=0.50,
        max_floor=10.00,
    )
    return Publisher(config)


@pytest.fixture
def publisher_high_floor() -> Publisher:
    """A Publisher with high bid floor range for specific tests."""
    config = PublisherConfig(
        name="HighFloorPub",
        domain="premium-site.com",
        category="IAB2",
        min_floor=50.00,
        max_floor=100.00,
    )
    return Publisher(config)
