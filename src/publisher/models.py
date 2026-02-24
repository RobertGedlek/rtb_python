from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class BidRequest:
    id: str
    domain: str
    category: str
    bid_floor: float

    def __post_init__(self):
        if self.bid_floor < 0:
            raise ValueError("Cena nie może być ujemna!")

    def to_dict(self):
        return asdict(self)