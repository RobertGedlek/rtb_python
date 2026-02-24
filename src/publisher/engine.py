import time
import random
import uuid
import logging
from src.publisher.models import BidRequest
from src.publisher.config import PublisherConfig

class Publisher:
    def __init__(self, config: PublisherConfig):
        """
        Initializes the publisher based on the provided configuration class.
        """
        self.config = config
        # Create a logger named after the specific publisher
        self.logger = logging.getLogger(f"Publisher-{config.name}")

    def generate_single_request(self) -> BidRequest:
        """
        Creates an immutable (frozen) BidRequest object.
        All parameters come from the configuration or generators.
        """
        return BidRequest(
            id=str(uuid.uuid4()),
            domain=self.config.domain,
            category=self.config.category,
            bid_floor=round(random.uniform(self.config.min_floor, self.config.max_floor), 2)
        )

    def run_simulation(self, interval: float = 1.0):
        self.logger.info(f"🚀 Starting traffic simulation for {self.config.domain} (Category: {self.config.category})")

        try:
            while True:
                # 1. Generate auction data
                request = self.generate_single_request()

                # 2. Log event (later: send to SSP/DSP)
                self.logger.info(
                    f"GENERATE | ID: {request.id[:8]}... | Floor: {request.bid_floor:>4}$ | Domain: {request.domain}"
                )

                # 3. Wait for the specified time
                time.sleep(interval)

        except KeyboardInterrupt:
            self.logger.info(f"🛑 Stopped publisher: {self.config.name}")
