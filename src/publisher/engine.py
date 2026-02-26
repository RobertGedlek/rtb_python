import random
import uuid
from src.logging_config import get_logger
from src.publisher.models import BidRequest
from src.publisher.config import PublisherConfig

class Publisher:
    def __init__(self, config: PublisherConfig):
        self.config = config
        self.logger = get_logger(f"Publisher-{config.name}")

    def generate_single_request(self) -> BidRequest:
        """Creates a random, valid BidRequest object."""
        return BidRequest(
            id=str(uuid.uuid4()),
            domain=self.config.domain,
            category=self.config.category,
            bid_floor=round(random.uniform(self.config.min_floor, self.config.max_floor), 2)
        )

