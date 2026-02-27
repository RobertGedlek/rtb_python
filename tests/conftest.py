"""
Global test configuration and shared fixtures.
"""
import pytest

from src.publisher.config import PublisherConfig


@pytest.fixture
def valid_publisher_config() -> PublisherConfig:
    """A reusable, valid PublisherConfig for tests that need one."""
    return PublisherConfig(
        publisher_id="pub-test",
        name="TestPub",
        domain="test-site.com",
        category="technology",
        min_floor=1.0,
        max_floor=5.0,
    )

