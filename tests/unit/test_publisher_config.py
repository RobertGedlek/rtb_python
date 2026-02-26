"""Unit tests for src.publisher.config.PublisherConfig"""
import pytest

from src.publisher.config import PublisherConfig

class TestPublisherConfigCreation:
    """Tests for valid PublisherConfig creation."""

    def test_create_with_defaults(self):
        cfg = PublisherConfig(
            name="Pub1", domain="example.com", category="tech",
            min_floor=1.0, max_floor=5.0,
        )
        assert cfg.name == "Pub1"
        assert cfg.target_url == "http://127.0.0.1:8000/bid/request"

    def test_create_with_custom_target_url(self):
        cfg = PublisherConfig(
            name="Pub1", domain="example.com", category="tech",
            min_floor=1.0, max_floor=5.0,
            target_url="http://custom:9000/bid",
        )
        assert cfg.target_url == "http://custom:9000/bid"

    def test_equal_min_max_floor_is_valid(self):
        cfg = PublisherConfig(
            name="Pub1", domain="d.com", category="c",
            min_floor=3.0, max_floor=3.0,
        )
        assert cfg.min_floor == cfg.max_floor


class TestPublisherConfigValidation:
    """Tests for __post_init__ validation — each branch."""

    def test_empty_name_raises(self):
        with pytest.raises(ValueError, match="'name' cannot be empty"):
            PublisherConfig(name="", domain="d.com", category="c", min_floor=1.0, max_floor=2.0)

    def test_empty_domain_raises(self):
        with pytest.raises(ValueError, match="'domain' cannot be empty"):
            PublisherConfig(name="P", domain="", category="c", min_floor=1.0, max_floor=2.0)

    def test_empty_category_raises(self):
        with pytest.raises(ValueError, match="'category' cannot be empty"):
            PublisherConfig(name="P", domain="d.com", category="", min_floor=1.0, max_floor=2.0)

    def test_min_floor_greater_than_max_floor_raises(self):
        with pytest.raises(ValueError, match="'min_floor' cannot be greater than 'max_floor'"):
            PublisherConfig(name="P", domain="d.com", category="c", min_floor=10.0, max_floor=1.0)

    def test_none_min_floor_raises(self):
        with pytest.raises((ValueError, TypeError)):
            PublisherConfig(name="P", domain="d.com", category="c", min_floor=None, max_floor=2.0)

    def test_none_max_floor_raises(self):
        with pytest.raises((ValueError, TypeError)):
            PublisherConfig(name="P", domain="d.com", category="c", min_floor=1.0, max_floor=None)

