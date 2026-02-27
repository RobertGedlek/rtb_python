"""
Integration tests for SSP -> Advertiser bid flow.

These tests verify the complete end-to-end flow:
- SSP forwards bid requests to Advertiser
- Advertiser processes and returns bid responses
- Proper validation and responses are returned
"""
import uuid

from httpx import AsyncClient

from tests.integration.conftest import generate_bid_request_payload


class TestAdvertiserBidFlow:
    """Test the complete flow from SSP sending requests to Advertiser responding."""

    async def test_advertiser_accepts_valid_bid_request(
        self, advertiser_client: AsyncClient
    ):
        """Advertiser should accept a valid bid request."""
        payload = generate_bid_request_payload()

        response = await advertiser_client.post("/bid", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["request_id"] == payload["id"]
        assert "advertiser_id" in data
        assert "bid_price" in data
        assert "ad_id" in data

    async def test_advertiser_returns_positive_bid_price(
        self, advertiser_client: AsyncClient
    ):
        """Advertiser should return a positive bid price."""
        payload = generate_bid_request_payload()

        response = await advertiser_client.post("/bid", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["bid_price"] >= 0

    async def test_advertiser_returns_valid_ad_id(
        self, advertiser_client: AsyncClient
    ):
        """Advertiser should return a valid UUID as ad_id."""
        payload = generate_bid_request_payload()

        response = await advertiser_client.post("/bid", json=payload)

        assert response.status_code == 200
        data = response.json()
        uuid.UUID(data["ad_id"])

    async def test_multiple_requests_return_unique_ad_ids(
        self, advertiser_client: AsyncClient
    ):
        """Each bid response should have a unique ad_id."""
        ad_ids = set()

        for _ in range(20):
            payload = generate_bid_request_payload()
            response = await advertiser_client.post("/bid", json=payload)
            assert response.status_code == 200
            ad_id = response.json()["ad_id"]
            assert ad_id not in ad_ids, "Duplicate ad_id generated"
            ad_ids.add(ad_id)

    async def test_request_id_preserved_in_response(
        self, advertiser_client: AsyncClient
    ):
        """The original request_id should be preserved in the response."""
        request_id = str(uuid.uuid4())
        payload = generate_bid_request_payload(request_id=request_id)

        response = await advertiser_client.post("/bid", json=payload)

        assert response.status_code == 200
        assert response.json()["request_id"] == request_id


class TestAdvertiserValidation:
    """Test Advertiser validation behavior with various request payloads."""

    async def test_invalid_uuid_rejected(self, advertiser_client: AsyncClient):
        """Advertiser rejects requests with invalid UUID format."""
        payload = {
            "id": "not-a-valid-uuid",
            "domain": "test.com",
            "category": "IAB1",
            "bid_floor": 1.0
        }

        response = await advertiser_client.post("/bid", json=payload)

        assert response.status_code == 422

    async def test_invalid_domain_rejected(self, advertiser_client: AsyncClient):
        """Advertiser rejects requests with invalid domain (no dot)."""
        payload = {
            "id": str(uuid.uuid4()),
            "domain": "invaliddomainnodot",
            "category": "IAB1",
            "bid_floor": 1.0
        }

        response = await advertiser_client.post("/bid", json=payload)

        assert response.status_code == 422

    async def test_negative_bid_floor_rejected(self, advertiser_client: AsyncClient):
        """Advertiser rejects requests with negative bid floor."""
        payload = {
            "id": str(uuid.uuid4()),
            "domain": "test.com",
            "category": "IAB1",
            "bid_floor": -0.5
        }

        response = await advertiser_client.post("/bid", json=payload)

        assert response.status_code == 422

    async def test_missing_required_fields_rejected(self, advertiser_client: AsyncClient):
        """Advertiser rejects requests missing required fields."""
        payload = {
            "id": str(uuid.uuid4()),
            "domain": "test.com"
        }

        response = await advertiser_client.post("/bid", json=payload)

        assert response.status_code == 422

    async def test_empty_category_rejected(self, advertiser_client: AsyncClient):
        """Advertiser rejects requests with empty category."""
        payload = {
            "id": str(uuid.uuid4()),
            "domain": "test.com",
            "category": "",
            "bid_floor": 1.0
        }

        response = await advertiser_client.post("/bid", json=payload)

        assert response.status_code == 422

    async def test_zero_bid_floor_accepted(self, advertiser_client: AsyncClient):
        """Advertiser accepts requests with zero bid floor."""
        payload = generate_bid_request_payload(bid_floor=0.0)

        response = await advertiser_client.post("/bid", json=payload)

        assert response.status_code == 200


class TestAdvertiserHealthEndpoint:
    """Test the Advertiser health check endpoint."""

    async def test_health_returns_ok(self, advertiser_client: AsyncClient):
        """Health endpoint returns OK status."""
        response = await advertiser_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    async def test_health_includes_advertiser_id(self, advertiser_client: AsyncClient):
        """Health endpoint includes advertiser_id info."""
        response = await advertiser_client.get("/health")

        data = response.json()
        assert "env" in data
        assert "advertiser_id" in data


class TestAdvertiserEdgeCases:
    """Test edge cases in the SSP-Advertiser integration."""

    async def test_very_high_bid_floor(self, advertiser_client: AsyncClient):
        """High bid floor values should be accepted."""
        payload = generate_bid_request_payload(bid_floor=1000.0)

        response = await advertiser_client.post("/bid", json=payload)

        assert response.status_code == 200

    async def test_long_category_value(self, advertiser_client: AsyncClient):
        """Category at max length should be accepted."""
        payload = {
            "id": str(uuid.uuid4()),
            "domain": "test.com",
            "category": "A" * 100,
            "bid_floor": 1.0
        }

        response = await advertiser_client.post("/bid", json=payload)

        assert response.status_code == 200

    async def test_category_exceeds_max_length_rejected(self, advertiser_client: AsyncClient):
        """Category exceeding max length should be rejected."""
        payload = {
            "id": str(uuid.uuid4()),
            "domain": "test.com",
            "category": "A" * 101,
            "bid_floor": 1.0
        }

        response = await advertiser_client.post("/bid", json=payload)

        assert response.status_code == 422

    async def test_special_characters_in_domain(self, advertiser_client: AsyncClient):
        """Domains with special characters should be handled."""
        payload = generate_bid_request_payload(domain="test-site.example.com")

        response = await advertiser_client.post("/bid", json=payload)

        assert response.status_code == 200

    async def test_subdomain_accepted(self, advertiser_client: AsyncClient):
        """Subdomains should be accepted as valid domains."""
        payload = generate_bid_request_payload(domain="sub.domain.example.com")

        response = await advertiser_client.post("/bid", json=payload)

        assert response.status_code == 200

    async def test_decimal_precision_in_bid_floor(self, advertiser_client: AsyncClient):
        """Bid floor with multiple decimal places should be accepted."""
        payload = generate_bid_request_payload(bid_floor=1.23456789)

        response = await advertiser_client.post("/bid", json=payload)

        assert response.status_code == 200


class TestAdvertiserResponseFormat:
    """Test the format and structure of Advertiser responses."""

    async def test_response_contains_all_required_fields(
        self, advertiser_client: AsyncClient
    ):
        """Bid response should contain all required fields."""
        payload = generate_bid_request_payload()

        response = await advertiser_client.post("/bid", json=payload)

        assert response.status_code == 200
        data = response.json()
        required_fields = {"request_id", "advertiser_id", "bid_price", "ad_id"}
        assert required_fields.issubset(data.keys())

    async def test_advertiser_id_is_consistent(self, advertiser_client: AsyncClient):
        """Advertiser ID should be consistent across requests."""
        advertiser_ids = set()

        for _ in range(5):
            payload = generate_bid_request_payload()
            response = await advertiser_client.post("/bid", json=payload)
            assert response.status_code == 200
            advertiser_ids.add(response.json()["advertiser_id"])

        assert len(advertiser_ids) == 1, "Advertiser ID should be consistent"

    async def test_bid_price_is_numeric(self, advertiser_client: AsyncClient):
        """Bid price should be a numeric value."""
        payload = generate_bid_request_payload()

        response = await advertiser_client.post("/bid", json=payload)

        assert response.status_code == 200
        bid_price = response.json()["bid_price"]
        assert isinstance(bid_price, (int, float))
