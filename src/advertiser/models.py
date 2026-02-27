from pydantic import BaseModel, Field


class BidResponse(BaseModel):
    """Response from advertiser with bid information."""
    request_id: str = Field(..., description="Original bid request ID")
    advertiser_id: str = Field(..., description="Advertiser identifier")
    bid_price: float = Field(..., ge=0, description="Bid price in USD")
    ad_id: str = Field(..., description="ID of the ad to display")
