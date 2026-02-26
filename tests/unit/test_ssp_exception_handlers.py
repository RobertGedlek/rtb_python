"""Unit tests for src.ssp.exception_handlers.validation_exception_handler"""
import json
from unittest.mock import MagicMock

import pytest
from fastapi.exceptions import RequestValidationError

from src.ssp.exception_handlers import validation_exception_handler

pytestmark = [pytest.mark.asyncio]


def _make_validation_error(errors: list[dict]) -> RequestValidationError:
    """Create a RequestValidationError with the given raw error list."""
    exc = RequestValidationError(errors=errors)
    return exc


class TestValidationExceptionHandler:

    async def test_returns_422_status(self):
        exc = _make_validation_error([
            {"loc": ("body", "bid_floor"), "msg": "bad value", "type": "value_error"},
        ])
        response = await validation_exception_handler(MagicMock(), exc)
        assert response.status_code == 422

    async def test_response_contains_rejected_status(self):
        exc = _make_validation_error([
            {"loc": ("body", "domain"), "msg": "missing dot", "type": "value_error"},
        ])
        response = await validation_exception_handler(MagicMock(), exc)
        body = json.loads(response.body)
        assert body["status"] == "rejected"
        assert body["reason"] == "validation_error"

    async def test_errors_list_structure(self):
        exc = _make_validation_error([
            {"loc": ("body", "id"), "msg": "not a valid UUID", "type": "value_error"},
            {"loc": ("body", "bid_floor"), "msg": "value too low", "type": "value_error.number.not_ge"},
        ])
        response = await validation_exception_handler(MagicMock(), exc)
        body = json.loads(response.body)

        assert len(body["errors"]) == 2
        assert body["errors"][0]["field"] == "id"
        assert body["errors"][0]["message"] == "not a valid UUID"
        assert body["errors"][1]["field"] == "bid_floor"

    async def test_body_loc_is_stripped_from_field(self):
        exc = _make_validation_error([
            {"loc": ("body", "category"), "msg": "too short", "type": "value_error"},
        ])
        response = await validation_exception_handler(MagicMock(), exc)
        body = json.loads(response.body)

        assert body["errors"][0]["field"] == "category"  # "body" stripped

