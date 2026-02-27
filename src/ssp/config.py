from dataclasses import dataclass, field


@dataclass(frozen=True)
class ServerConfig:
    """Configuration for a single SSP server instance."""
    host: str = "127.0.0.1"
    port: int = 8000
    workers: int = 1
    log_level: str = "info"
    reload: bool = False  # True only for development


@dataclass(frozen=True)
class SSPConfig:
    """Main SSP configuration."""
    server: ServerConfig = field(default_factory=ServerConfig)
    max_bid_response_time_ms: int = 100  # RTB timeout for bid response
    currency: str = "USD"
    seat_id: str = "ssp-001"
    advertiser_urls: tuple[str, ...] = field(default_factory=lambda: ("http://127.0.0.1:8001/bid",))


# --- Environment presets ---

DEVELOPMENT = SSPConfig(
    server=ServerConfig(
        host="127.0.0.1",
        port=8000,
        workers=1,
        log_level="debug",
        reload=True,
    ),
    max_bid_response_time_ms=500,  # more lenient in dev
)

STAGING = SSPConfig(
    server=ServerConfig(
        host="0.0.0.0",
        port=8000,
        workers=2,
        log_level="info",
        reload=False,
    ),
    max_bid_response_time_ms=150,
)

PRODUCTION = SSPConfig(
    server=ServerConfig(
        host="0.0.0.0",
        port=8000,
        workers=3,
        log_level="warning",
        reload=False,
    ),
    max_bid_response_time_ms=100,
)

ENVIRONMENTS = {
    "dev": DEVELOPMENT,
    "staging": STAGING,
    "prod": PRODUCTION,
}


def get_config(env: str = "dev") -> SSPConfig:
    """Get SSP config for a given environment."""
    if env not in ENVIRONMENTS:
        raise ValueError(f"Unknown environment: '{env}'. Available: {list(ENVIRONMENTS.keys())}")
    return ENVIRONMENTS[env]

