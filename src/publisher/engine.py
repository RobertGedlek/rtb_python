import time
import random
import uuid
import requests
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

    def run_simulation(self, interval: float = 1.0):
        """Loop sending requests to SSP."""
        self.logger.info(f"🚀 Starting traffic: {self.config.domain} -> {self.config.target_url}")

        try:
            while True:
                request_obj = self.generate_single_request()

                try:
                    response = requests.post(
                        self.config.target_url,
                        json=request_obj.to_dict(),
                        timeout=0.5
                    )

                    if response.status_code in [200, 204]:
                        self.logger.info(f"✅ OK | ID: {request_obj.id[:8]}... | Floor: {request_obj.bid_floor}$")
                    else:
                        self.logger.warning(f"⚠️ Server returned error: {response.status_code}")

                except requests.exceptions.RequestException as e:
                    self.logger.error(f"❌ No connection to SSP: {e}")

                time.sleep(interval)
        except KeyboardInterrupt:
            self.logger.info(f"🛑 Stopped: {self.config.name}")
