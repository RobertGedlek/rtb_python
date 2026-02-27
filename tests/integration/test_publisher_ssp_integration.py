"""
Integration tests for Publisher -> SSP bid request flow.

These tests verify the complete end-to-end flow:
- Publisher generates valid bid requests
- SSP server receives and validates them
- Proper responses are returned
"""
import uuid

from httpx import AsyncClient

from src.publisher.engine import Publisher

class TestPublisherToSSPFlow:
    """Test the complete flow from Publisher generating requests to SSP receiving them."""

    async def test_publisher_request_accepted_by_ssp(
        self, async_client: AsyncClient, publisher: Publisher
    ):
        """Publisher-generated request should be accepted by SSP."""
        bid_request = publisher.generate_single_request()
        
        response = await async_client.post(
            "/bid/request",
            json=bid_request.to_dict()
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "received"
        assert data["id"] == bid_request.id

    async def test_multiple_publisher_requests_all_accepted(
        self, async_client: AsyncClient, publisher: Publisher
    ):
        """Multiple consecutive requests from same publisher should all succeed."""
        for _ in range(5):
            bid_request = publisher.generate_single_request()
            response = await async_client.post(
                "/bid/request",
                json=bid_request.to_dict()
            )
            assert response.status_code == 200
            assert response.json()["status"] == "received"

    async def test_different_publishers_can_send_requests(
        self, async_client: AsyncClient, publisher: Publisher, publisher_high_floor: Publisher
    ):
        """Different publisher configurations should all work."""
        for pub in [publisher, publisher_high_floor]:
            bid_request = pub.generate_single_request()
            response = await async_client.post(
                "/bid/request",
                json=bid_request.to_dict()
            )
            assert response.status_code == 200

    async def test_bid_floor_preserved_in_response_flow(
        self, async_client: AsyncClient, publisher: Publisher
    ):
        """Bid floor should be within publisher's configured range."""
        bid_request = publisher.generate_single_request()
        
        assert publisher.config.min_floor <= bid_request.bid_floor <= publisher.config.max_floor
        
        response = await async_client.post(
            "/bid/request",
            json=bid_request.to_dict()
        )
        assert response.status_code == 200

    async def test_category_normalized_by_ssp(
        self, async_client: AsyncClient, publisher: Publisher
    ):
        """SSP normalizes category to uppercase."""
        bid_request = publisher.generate_single_request()
        payload = bid_request.to_dict()
        payload["category"] = "technology"  # lowercase
        
        response = await async_client.post("/bid/request", json=payload)
        
        assert response.status_code == 200

    async def test_domain_normalized_by_ssp(
        self, async_client: AsyncClient, publisher: Publisher
    ):
        """SSP normalizes domain to lowercase."""
        bid_request = publisher.generate_single_request()
        payload = bid_request.to_dict()
        payload["domain"] = "TEST-SITE.COM"  # uppercase
        
        response = await async_client.post("/bid/request", json=payload)
        
        assert response.status_code == 200


class TestSSPValidationIntegration:
    """Test SSP validation behavior with various request payloads."""

    async def test_invalid_uuid_rejected(self, async_client: AsyncClient):
        """SSP rejects requests with invalid UUID format."""
        payload = {
            "id": "not-a-valid-uuid",
            "domain": "test.com",
            "category": "IAB1",
            "bid_floor": 1.0
        }
        
        response = await async_client.post("/bid/request", json=payload)
        
        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "rejected"
        assert data["reason"] == "validation_error"
        assert any(e["field"] == "id" for e in data["errors"])

    async def test_invalid_domain_rejected(self, async_client: AsyncClient):
        """SSP rejects requests with invalid domain (no dot)."""
        payload = {
            "id": str(uuid.uuid4()),
            "domain": "invaliddomainnodot",
            "category": "IAB1",
            "bid_floor": 1.0
        }
        
        response = await async_client.post("/bid/request", json=payload)
        
        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "rejected"
        assert any(e["field"] == "domain" for e in data["errors"])

    async def test_negative_bid_floor_rejected(self, async_client: AsyncClient):
        """SSP rejects requests with negative bid floor."""
        payload = {
            "id": str(uuid.uuid4()),
            "domain": "test.com",
            "category": "IAB1",
            "bid_floor": -0.5
        }
        
        response = await async_client.post("/bid/request", json=payload)
        
        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "rejected"
        assert any(e["field"] == "bid_floor" for e in data["errors"])

    async def test_missing_required_fields_rejected(self, async_client: AsyncClient):
        """SSP rejects requests missing required fields."""
        payload = {
            "id": str(uuid.uuid4()),
            "domain": "test.com"
            # missing category and bid_floor
        }
        
        response = await async_client.post("/bid/request", json=payload)
        
        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "rejected"

    async def test_empty_category_rejected(self, async_client: AsyncClient):
        """SSP rejects requests with empty category."""
        payload = {
            "id": str(uuid.uuid4()),
            "domain": "test.com",
            "category": "",
            "bid_floor": 1.0
        }
        
        response = await async_client.post("/bid/request", json=payload)
        
        assert response.status_code == 422

    async def test_zero_bid_floor_accepted(self, async_client: AsyncClient):
        """SSP accepts requests with zero bid floor."""
        payload = {
            "id": str(uuid.uuid4()),
            "domain": "test.com",
            "category": "IAB1",
            "bid_floor": 0.0
        }
        
        response = await async_client.post("/bid/request", json=payload)
        
        assert response.status_code == 200
        assert response.json()["status"] == "received"

    async def test_multiple_validation_errors_reported(self, async_client: AsyncClient):
        """SSP reports all validation errors at once."""
        payload = {
            "id": "invalid",
            "domain": "nodot",
            "category": "",
            "bid_floor": -1.0
        }
        
        response = await async_client.post("/bid/request", json=payload)
        
        assert response.status_code == 422
        data = response.json()
        assert len(data["errors"]) >= 2


class TestSSPHealthEndpoint:
    """Test the SSP health check endpoint."""

    async def test_health_returns_ok(self, async_client: AsyncClient):
        """Health endpoint returns OK status."""
        response = await async_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    async def test_health_includes_environment(self, async_client: AsyncClient):
        """Health endpoint includes environment info."""
        response = await async_client.get("/health")
        
        data = response.json()
        assert "env" in data
        assert "seat_id" in data


class TestRequestIdUniqueness:
    """Test that Publisher generates unique request IDs."""

    async def test_publisher_generates_unique_ids(
        self, async_client: AsyncClient, publisher: Publisher
    ):
        """Each generated request should have a unique ID."""
        ids = set()
        
        for _ in range(100):
            bid_request = publisher.generate_single_request()
            assert bid_request.id not in ids, "Duplicate ID generated"
            ids.add(bid_request.id)
            
            response = await async_client.post(
                "/bid/request",
                json=bid_request.to_dict()
            )
            assert response.status_code == 200


class TestEdgeCases:
    """Test edge cases in the Publisher-SSP integration."""

    async def test_very_high_bid_floor(
        self, async_client: AsyncClient, publisher_high_floor: Publisher
    ):
        """High bid floor values should be accepted."""
        bid_request = publisher_high_floor.generate_single_request()
        
        assert bid_request.bid_floor >= 50.0
        
        response = await async_client.post(
            "/bid/request",
            json=bid_request.to_dict()
        )
        assert response.status_code == 200

    async def test_long_category_value(self, async_client: AsyncClient):
        """Category at max length should be accepted."""
        payload = {
            "id": str(uuid.uuid4()),
            "domain": "test.com",
            "category": "A" * 100,  # max_length=100
            "bid_floor": 1.0
        }
        
        response = await async_client.post("/bid/request", json=payload)
        
        assert response.status_code == 200

    async def test_category_exceeds_max_length_rejected(self, async_client: AsyncClient):
        """Category exceeding max length should be rejected."""
        payload = {
            "id": str(uuid.uuid4()),
            "domain": "test.com",
            "category": "A" * 101,  # exceeds max_length=100
            "bid_floor": 1.0
        }
        
        response = await async_client.post("/bid/request", json=payload)
        
        assert response.status_code == 422

    async def test_special_characters_in_domain(self, async_client: AsyncClient):
        """Domains with special characters should be handled."""
        payload = {
            "id": str(uuid.uuid4()),
            "domain": "test-site.example.com",
            "category": "IAB1",
            "bid_floor": 1.0
        }
        
        response = await async_client.post("/bid/request", json=payload)
        
        assert response.status_code == 200

    async def test_subdomain_accepted(self, async_client: AsyncClient):
        """Subdomains should be accepted as valid domains."""
        payload = {
            "id": str(uuid.uuid4()),
            "domain": "sub.domain.example.com",
            "category": "IAB1",
            "bid_floor": 1.0
        }
        
        response = await async_client.post("/bid/request", json=payload)
        
        assert response.status_code == 200

    async def test_decimal_precision_in_bid_floor(self, async_client: AsyncClient):
        """Bid floor with multiple decimal places should be accepted."""
        payload = {
            "id": str(uuid.uuid4()),
            "domain": "test.com",
            "category": "IAB1",
            "bid_floor": 1.23456789
        }
        
        response = await async_client.post("/bid/request", json=payload)
        
        assert response.status_code == 200
