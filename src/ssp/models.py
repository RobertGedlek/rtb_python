from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class BidRequestIn(BaseModel):
    """
    Pydantic model for validating incoming BidRequest data from publishers.
    Maps to the publisher's BidRequest dataclass fields.
    """
    id: str = Field(..., min_length=1, description="Unique bid request ID (UUID format)")
    domain: str = Field(..., min_length=1, max_length=255, description="Publisher domain")
    category: str = Field(..., min_length=1, max_length=100, description="Content category (e.g. IAB)")
    bid_floor: float = Field(..., ge=0, description="Minimum bid price in USD")

    @field_validator("id")
    @classmethod
    def validate_uuid_format(cls, v: str) -> str:
        """Ensure the id field is a valid UUID string."""
        try:
            UUID(v)
        except ValueError:
            raise ValueError(f"'{v}' is not a valid UUID")
        return v

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v: str) -> str:
        """Basic domain validation — must contain at least one dot."""
        if "." not in v:
            raise ValueError(f"'{v}' does not look like a valid domain (missing dot)")
        return v.lower().strip()

    @field_validator("category")
    @classmethod
    def normalize_category(cls, v: str) -> str:
        """Normalize category to uppercase (IAB convention)."""
        return v.strip().upper()

