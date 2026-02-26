"""Unit tests for src.ssp.models.BidRequestIn"""
import uuid

import pytest
from pydantic import ValidationError

from src.ssp.models import BidRequestIn

# ── Helper ───────────────────────────────────────────────────────

def _valid_payload(**overrides) -> dict:
    """Return a valid payload dict, with optional field overrides."""
    base = {
        "id": str(uuid.uuid4()),
        "domain": "example.com",
        "category": "iab1",
        "bid_floor": 1.50,
    }
    base.update(overrides)
    return base


# ── Happy-path ───────────────────────────────────────────────────

class TestBidRequestInCreation:

    def test_valid_payload(self):
        model = BidRequestIn(**_valid_payload())
        assert model.bid_floor == 1.50

    def test_domain_is_lowercased_and_stripped(self):
        model = BidRequestIn(**_valid_payload(domain="  Example.COM  "))
        assert model.domain == "example.com"

    def test_category_is_uppercased_and_stripped(self):
        model = BidRequestIn(**_valid_payload(category="  iab5  "))
        assert model.category == "IAB5"

    def test_zero_bid_floor_is_valid(self):
        model = BidRequestIn(**_valid_payload(bid_floor=0.0))
        assert model.bid_floor == 0.0


# ── UUID validator ───────────────────────────────────────────────

class TestUUIDValidator:

    def test_valid_uuid_accepted(self):
        valid_id = str(uuid.uuid4())
        model = BidRequestIn(**_valid_payload(id=valid_id))
        assert model.id == valid_id

    def test_invalid_uuid_rejected(self):
        with pytest.raises(ValidationError, match="not a valid UUID"):
            BidRequestIn(**_valid_payload(id="not-a-uuid"))

    def test_empty_id_rejected(self):
        with pytest.raises(ValidationError):
            BidRequestIn(**_valid_payload(id=""))


# ── Domain validator ─────────────────────────────────────────────

class TestDomainValidator:

    def test_domain_with_dot_accepted(self):
        model = BidRequestIn(**_valid_payload(domain="site.com"))
        assert model.domain == "site.com"

    def test_domain_without_dot_rejected(self):
        with pytest.raises(ValidationError, match="missing dot"):
            BidRequestIn(**_valid_payload(domain="localhost"))

    def test_empty_domain_rejected(self):
        with pytest.raises(ValidationError):
            BidRequestIn(**_valid_payload(domain=""))


# ── Category validator ───────────────────────────────────────────

class TestCategoryValidator:

    def test_category_normalized_to_upper(self):
        model = BidRequestIn(**_valid_payload(category="sports"))
        assert model.category == "SPORTS"

    def test_empty_category_rejected(self):
        with pytest.raises(ValidationError):
            BidRequestIn(**_valid_payload(category=""))


# ── bid_floor field constraint ───────────────────────────────────

class TestBidFloorConstraint:

    def test_negative_bid_floor_rejected(self):
        with pytest.raises(ValidationError):
            BidRequestIn(**_valid_payload(bid_floor=-0.01))

    def test_bid_floor_coerced_from_int(self):
        model = BidRequestIn(**_valid_payload(bid_floor=2))
        assert model.bid_floor == 2.0
        assert isinstance(model.bid_floor, float)

    def test_bid_floor_as_string_number_is_coerced(self):
        model = BidRequestIn(**_valid_payload(bid_floor="1.5"))
        assert model.bid_floor == 1.5

    def test_bid_floor_as_non_numeric_string_rejected(self):
        with pytest.raises(ValidationError):
            BidRequestIn(**_valid_payload(bid_floor="free"))


# ── max_length constraints ───────────────────────────────────────

class TestMaxLengthConstraints:

    def test_domain_at_max_length_accepted(self):
        long_domain = "a" * 251 + ".com"  # 255 chars
        model = BidRequestIn(**_valid_payload(domain=long_domain))
        assert len(model.domain) == 255

    def test_domain_exceeding_max_length_rejected(self):
        too_long = "a" * 252 + ".com"  # 256 chars
        with pytest.raises(ValidationError):
            BidRequestIn(**_valid_payload(domain=too_long))

    def test_category_at_max_length_accepted(self):
        long_cat = "a" * 100
        model = BidRequestIn(**_valid_payload(category=long_cat))
        assert len(model.category) == 100

    def test_category_exceeding_max_length_rejected(self):
        with pytest.raises(ValidationError):
            BidRequestIn(**_valid_payload(category="a" * 101))


# ── Missing required fields ──────────────────────────────────────

class TestMissingRequiredFields:

    def test_missing_id_raises(self):
        payload = _valid_payload()
        del payload["id"]
        with pytest.raises(ValidationError):
            BidRequestIn(**payload)

    def test_missing_domain_raises(self):
        payload = _valid_payload()
        del payload["domain"]
        with pytest.raises(ValidationError):
            BidRequestIn(**payload)

    def test_missing_category_raises(self):
        payload = _valid_payload()
        del payload["category"]
        with pytest.raises(ValidationError):
            BidRequestIn(**payload)

    def test_missing_bid_floor_raises(self):
        payload = _valid_payload()
        del payload["bid_floor"]
        with pytest.raises(ValidationError):
            BidRequestIn(**payload)

