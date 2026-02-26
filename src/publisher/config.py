from dataclasses import dataclass

@dataclass(frozen=True)
class PublisherConfig:
    name: str
    domain: str
    category: str
    min_floor: float
    max_floor: float
    target_url: str = "http://127.0.0.1:8000/bid/request"

    def __post_init__(self):
        if not self.name:
            raise ValueError("Field 'name' cannot be empty!")
        if not self.domain:
            raise ValueError("Field 'domain' cannot be empty!")
        if not self.category:
            raise ValueError("Field 'category' cannot be empty!")
        if self.min_floor is None:
            raise ValueError("Field 'min_floor' cannot be None!")
        if self.max_floor is None:
            raise ValueError("Field 'max_floor' cannot be None!")
        if self.min_floor > self.max_floor:
            raise ValueError("'min_floor' cannot be greater than 'max_floor'!")
