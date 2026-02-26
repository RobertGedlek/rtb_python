"""Unit tests for src.publisher.models.BidRequest"""
import dataclasses

import pytest

from src.publisher.models import BidRequest

class TestBidRequestCreation:
    """Tests for creating valid BidRequest instances."""

    def test_create_valid_bid_request(self):
        br = BidRequest(id="abc-123", domain="example.com", category="tech", bid_floor=1.50)

        assert br.id == "abc-123"
        assert br.domain == "example.com"
        assert br.category == "tech"
        assert br.bid_floor == 1.50

    def test_create_with_zero_floor(self):
        br = BidRequest(id="1", domain="d.com", category="c", bid_floor=0.0)
        assert br.bid_floor == 0.0

    def test_create_with_high_floor(self):
        br = BidRequest(id="1", domain="d.com", category="c", bid_floor=9999.99)
        assert br.bid_floor == 9999.99


class TestBidRequestValidation:
    """Tests for __post_init__ validation."""

    def test_negative_bid_floor_raises_value_error(self):
        with pytest.raises(ValueError, match="Price cannot be negative"):
            BidRequest(id="1", domain="d.com", category="c", bid_floor=-0.01)

    def test_large_negative_bid_floor_raises_value_error(self):
        with pytest.raises(ValueError, match="Price cannot be negative"):
            BidRequest(id="1", domain="d.com", category="c", bid_floor=-100.0)


class TestBidRequestFrozen:
    """Tests that BidRequest is immutable (frozen dataclass)."""

    def test_cannot_modify_id(self):
        br = BidRequest(id="1", domain="d.com", category="c", bid_floor=1.0)
        with pytest.raises(dataclasses.FrozenInstanceError):
            br.id = "changed"

    def test_cannot_modify_bid_floor(self):
        br = BidRequest(id="1", domain="d.com", category="c", bid_floor=1.0)
        with pytest.raises(dataclasses.FrozenInstanceError):
            br.bid_floor = 99.0


class TestBidRequestToDict:
    """Tests for to_dict() serialization."""

    def test_to_dict_returns_all_fields(self):
        br = BidRequest(id="abc", domain="site.com", category="news", bid_floor=2.5)
        result = br.to_dict()

        assert result == {
            "id": "abc",
            "domain": "site.com",
            "category": "news",
            "bid_floor": 2.5,
        }

    def test_to_dict_returns_new_dict_each_call(self):
        br = BidRequest(id="1", domain="d.com", category="c", bid_floor=1.0)
        assert br.to_dict() is not br.to_dict()

