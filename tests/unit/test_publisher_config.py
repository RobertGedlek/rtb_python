"""Unit tests for src.publisher.config"""
import pytest

from src.publisher.config import PublisherConfig, ServerConfig, get_config, ENVIRONMENTS


class TestServerConfig:
    """Tests for ServerConfig dataclass."""

    def test_default_values(self):
        cfg = ServerConfig()
        assert cfg.host == "127.0.0.1"
        assert cfg.port == 8002
        assert cfg.workers == 1
        assert cfg.log_level == "info"
        assert cfg.reload is False

    def test_custom_values(self):
        cfg = ServerConfig(host="0.0.0.0", port=9000, workers=4)
        assert cfg.host == "0.0.0.0"
        assert cfg.port == 9000
        assert cfg.workers == 4


class TestPublisherConfigCreation:
    """Tests for valid PublisherConfig creation."""

    def test_create_with_defaults(self):
        cfg = PublisherConfig()
        assert cfg.publisher_id == "pub-001"
        assert cfg.name == "Default Publisher"
        assert cfg.domain == "example.com"
        assert cfg.category == "news"
        assert cfg.ssp_url == "http://127.0.0.1:8000/bid/request"

    def test_create_with_custom_values(self):
        cfg = PublisherConfig(
            publisher_id="pub-custom",
            name="CustomPub",
            domain="custom.com",
            category="tech",
            min_floor=1.0,
            max_floor=5.0,
            ssp_url="http://custom:9000/bid",
        )
        assert cfg.publisher_id == "pub-custom"
        assert cfg.name == "CustomPub"
        assert cfg.ssp_url == "http://custom:9000/bid"

    def test_equal_min_max_floor_is_valid(self):
        cfg = PublisherConfig(min_floor=3.0, max_floor=3.0)
        assert cfg.min_floor == cfg.max_floor

    def test_server_config_nested(self):
        server = ServerConfig(port=9999)
        cfg = PublisherConfig(server=server)
        assert cfg.server.port == 9999


class TestGetConfig:
    """Tests for get_config function."""

    def test_dev_environment(self):
        cfg = get_config("dev")
        assert cfg.server.reload is True
        assert cfg.server.log_level == "debug"

    def test_staging_environment(self):
        cfg = get_config("staging")
        assert cfg.server.reload is False
        assert cfg.server.workers == 2

    def test_prod_environment(self):
        cfg = get_config("prod")
        assert cfg.server.reload is False
        assert cfg.server.workers == 3

    def test_unknown_environment_raises(self):
        with pytest.raises(ValueError, match="Unknown environment"):
            get_config("unknown")

    def test_all_environments_exist(self):
        for env in ["dev", "staging", "prod"]:
            assert env in ENVIRONMENTS
