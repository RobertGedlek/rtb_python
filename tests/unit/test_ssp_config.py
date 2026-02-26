"""Unit tests for src.ssp.config (ServerConfig, SSPConfig, get_config)."""
import pytest

from src.ssp.config import ServerConfig, SSPConfig, get_config, ENVIRONMENTS

class TestServerConfigDefaults:

    def test_default_host(self):
        cfg = ServerConfig()
        assert cfg.host == "127.0.0.1"

    def test_default_port(self):
        cfg = ServerConfig()
        assert cfg.port == 8000

    def test_default_workers(self):
        cfg = ServerConfig()
        assert cfg.workers == 1

    def test_default_reload_is_false(self):
        cfg = ServerConfig()
        assert cfg.reload is False


class TestSSPConfigDefaults:

    def test_default_currency(self):
        cfg = SSPConfig()
        assert cfg.currency == "USD"

    def test_default_seat_id(self):
        cfg = SSPConfig()
        assert cfg.seat_id == "ssp-001"

    def test_default_max_bid_response_time(self):
        cfg = SSPConfig()
        assert cfg.max_bid_response_time_ms == 100

    def test_server_is_server_config_instance(self):
        cfg = SSPConfig()
        assert isinstance(cfg.server, ServerConfig)


class TestGetConfig:

    @pytest.mark.parametrize("env_name", ["dev", "staging", "prod"])
    def test_valid_environment_returns_config(self, env_name):
        cfg = get_config(env_name)
        assert isinstance(cfg, SSPConfig)
        assert cfg is ENVIRONMENTS[env_name]

    def test_unknown_environment_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown environment"):
            get_config("unknown")

    def test_default_is_dev(self):
        assert get_config() is get_config("dev")

    # ── Spot-check environment presets ──

    def test_dev_has_reload_enabled(self):
        cfg = get_config("dev")
        assert cfg.server.reload is True

    def test_prod_has_reload_disabled(self):
        cfg = get_config("prod")
        assert cfg.server.reload is False

    def test_prod_has_stricter_timeout_than_dev(self):
        dev = get_config("dev")
        prod = get_config("prod")
        assert prod.max_bid_response_time_ms < dev.max_bid_response_time_ms

    def test_prod_has_more_workers_than_dev(self):
        dev = get_config("dev")
        prod = get_config("prod")
        assert prod.server.workers > dev.server.workers

