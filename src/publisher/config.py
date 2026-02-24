from dataclasses import dataclass

@dataclass(frozen=True)
class PublisherConfig:
    name: str
    domain: str
    category: str
    min_floor: float
    max_floor: float

    def __post_init__(self):
        """Walidacja konfiguracji przy starcie."""
        if self.min_floor > self.max_floor:
            raise ValueError(f"Błędna konfiguracja dla {self.name}: min_floor nie może być większy niż max_floor!")