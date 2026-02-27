"""Unit tests for src.publisher.server"""
from unittest.mock import patch, AsyncMock

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from src.publisher.server import app, generate_bid_request, is_generating


@pytest_asyncio.fixture
async def client():
    """Async HTTP client for testing the Publisher FastAPI server."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    async def test_health_returns_ok(self, client: AsyncClient):
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    async def test_health_includes_publisher_id(self, client: AsyncClient):
        response = await client.get("/health")
        data = response.json()
        assert "publisher_id" in data
        assert "env" in data


class TestStatusEndpoint:
    """Tests for the /status endpoint."""

    async def test_status_returns_config_info(self, client: AsyncClient):
        response = await client.get("/status")
        assert response.status_code == 200
        data = response.json()
        assert "publisher_id" in data
        assert "domain" in data
        assert "category" in data
        assert "floor_range" in data
        assert "is_generating" in data


class TestGenerateBidRequest:
    """Tests for the generate_bid_request function."""

    def test_returns_bid_request_with_valid_uuid(self):
        from uuid import UUID
        request = generate_bid_request()
        UUID(request.id)

    def test_uses_config_domain(self):
        request = generate_bid_request()
        assert request.domain is not None
        assert len(request.domain) > 0

    def test_bid_floor_is_positive(self):
        for _ in range(10):
            request = generate_bid_request()
            assert request.bid_floor >= 0


class TestSendEndpoint:
    """Tests for the /send endpoint."""

    async def test_send_returns_request_id(self, client: AsyncClient):
        with patch("src.publisher.server.send_bid_request_to_ssp", new_callable=AsyncMock) as mock:
            mock.return_value = {"status": "received", "id": "test-id"}
            response = await client.post("/send")
            assert response.status_code == 200
            data = response.json()
            assert "request_id" in data

    async def test_send_handles_ssp_failure(self, client: AsyncClient):
        with patch("src.publisher.server.send_bid_request_to_ssp", new_callable=AsyncMock) as mock:
            mock.return_value = None
            response = await client.post("/send")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "failed"


class TestStartStopEndpoints:
    """Tests for /start and /stop endpoints."""

    async def test_start_returns_started_status(self, client: AsyncClient):
        import src.publisher.server as server_module
        server_module.is_generating = False

        with patch("src.publisher.server.asyncio.create_task"):
            response = await client.post("/start")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] in ["started", "already_running"]

        server_module.is_generating = False

    async def test_stop_when_not_running(self, client: AsyncClient):
        import src.publisher.server as server_module
        server_module.is_generating = False
        server_module.generation_task = None

        response = await client.post("/stop")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "already_stopped"
