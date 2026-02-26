"""Unit tests for src.publisher.engine.Publisher"""
from unittest.mock import patch
from uuid import UUID

from src.publisher.engine import Publisher

class TestPublisherInit:
    """Tests for Publisher initialization."""

    def test_stores_config(self, valid_publisher_config):
        pub = Publisher(valid_publisher_config)
        assert pub.config is valid_publisher_config

    def test_logger_name_contains_publisher_name(self, valid_publisher_config):
        pub = Publisher(valid_publisher_config)
        assert valid_publisher_config.name in pub.logger.name


class TestGenerateSingleRequest:
    """Tests for Publisher.generate_single_request()."""

    def test_returns_bid_request_instance(self, valid_publisher_config):
        from src.publisher.models import BidRequest

        pub = Publisher(valid_publisher_config)
        result = pub.generate_single_request()
        assert isinstance(result, BidRequest)

    def test_domain_matches_config(self, valid_publisher_config):
        pub = Publisher(valid_publisher_config)
        result = pub.generate_single_request()
        assert result.domain == valid_publisher_config.domain

    def test_category_matches_config(self, valid_publisher_config):
        pub = Publisher(valid_publisher_config)
        result = pub.generate_single_request()
        assert result.category == valid_publisher_config.category

    def test_bid_floor_within_config_range(self, valid_publisher_config):
        pub = Publisher(valid_publisher_config)
        for _ in range(50):  # run multiple times – random values
            result = pub.generate_single_request()
            assert valid_publisher_config.min_floor <= result.bid_floor <= valid_publisher_config.max_floor

    def test_id_is_valid_uuid(self, valid_publisher_config):
        pub = Publisher(valid_publisher_config)
        result = pub.generate_single_request()
        UUID(result.id)  # raises ValueError if not a valid UUID

    @patch("src.publisher.engine.random.uniform", return_value=3.14)
    def test_bid_floor_uses_random_uniform(self, mock_uniform, valid_publisher_config):
        pub = Publisher(valid_publisher_config)
        result = pub.generate_single_request()

        mock_uniform.assert_called_once_with(
            valid_publisher_config.min_floor,
            valid_publisher_config.max_floor,
        )
        assert result.bid_floor == 3.14

    @patch("src.publisher.engine.random.uniform", return_value=3.14159)
    def test_bid_floor_is_rounded_to_two_decimal_places(self, _mock_uniform, valid_publisher_config):
        pub = Publisher(valid_publisher_config)
        result = pub.generate_single_request()
        assert result.bid_floor == round(3.14159, 2)

    def test_each_call_generates_unique_id(self, valid_publisher_config):
        pub = Publisher(valid_publisher_config)
        ids = {pub.generate_single_request().id for _ in range(20)}
        assert len(ids) == 20

