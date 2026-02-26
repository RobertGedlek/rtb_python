from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.logging_config import get_logger

logger = get_logger("SSP-Server")


async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    """Custom handler for request validation errors — returns clear RTB-style error messages."""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"],
        })

    logger.warning(f"🚫 Invalid BidRequest received: {errors}")
    return JSONResponse(
        status_code=422,
        content={
            "status": "rejected",
            "reason": "validation_error",
            "errors": errors,
        },
    )

