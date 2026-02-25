import time
import random
import uuid
import logging
import requests
from src.publisher.models import BidRequest
from src.publisher.config import PublisherConfig

class Publisher:
    def __init__(self, config: PublisherConfig, target_url: str = "http://127.0.0.1:8000/bid/request"):
        self.config = config
        self.target_url = target_url
        self.logger = logging.getLogger(f"Publisher-{config.name}")

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
        self.logger.info(f"🚀 Starting traffic: {self.config.domain} -> {self.target_url}")

        try:
            while True:
                request_obj = self.generate_single_request()

                try:
                    response = requests.post(
                        self.target_url,
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
