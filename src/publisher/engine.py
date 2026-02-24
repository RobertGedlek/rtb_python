import time
import random
import uuid
import logging
from src.publisher.models import BidRequest
from src.publisher.config import PublisherConfig

class Publisher:
    def __init__(self, config: PublisherConfig):
        """
        Inicjalizuje wydawcę na podstawie dostarczonej klasy konfiguracji.
        """
        self.config = config
        # Tworzymy logger nazwany imieniem konkretnego wydawcy
        self.logger = logging.getLogger(f"Publisher-{config.name}")

    def generate_single_request(self) -> BidRequest:
        """
        Tworzy niezmienny (frozen) obiekt BidRequest.
        Wszystkie parametry pochodzą z konfiguracji lub generatorów.
        """
        return BidRequest(
            id=str(uuid.uuid4()),
            domain=self.config.domain,
            category=self.config.category,
            bid_floor=round(random.uniform(self.config.min_floor, self.config.max_floor), 2)
        )

    def run_simulation(self, interval: float = 1.0):
        """
        Główna pętla symulująca działanie serwera wydawcy.
        W przyszłości tutaj dodamy metodę wysyłającą request przez HTTP.
        """
        self.logger.info(f"🚀 Start symulacji ruchu dla {self.config.domain} (Kat: {self.config.category})")

        try:
            while True:
                # 1. Generujemy dane aukcji
                request = self.generate_single_request()

                # 2. Logujemy zdarzenie (później: wysyłka do SSP/DSP)
                self.logger.info(
                    f"GENERATE | ID: {request.id[:8]}... | Floor: {request.bid_floor:>4}$ | Domain: {request.domain}"
                )

                # 3. Odczekujemy zadany czas
                time.sleep(interval)

        except KeyboardInterrupt:
            self.logger.info(f"🛑 Zatrzymano wydawcę: {self.config.name}")