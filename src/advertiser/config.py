from dataclasses import dataclass, field


@dataclass(frozen=True)
class ServerConfig:
    """Configuration for a single Advertiser server instance."""
    host: str = "127.0.0.1"
    port: int = 8001
    workers: int = 1
    log_level: str = "info"
    reload: bool = False


@dataclass(frozen=True)
class AdvertiserConfig:
    """Main Advertiser (DSP) configuration."""
    server: ServerConfig = field(default_factory=ServerConfig)
    advertiser_id: str = "adv-001"
    response_delay_ms: int = 50
    min_bid: float = 0.5
    max_bid: float = 5.0


DEVELOPMENT = AdvertiserConfig(
    server=ServerConfig(
        host="127.0.0.1",
        port=8001,
        workers=1,
        log_level="debug",
        reload=True,
    ),
    response_delay_ms=30,
)

STAGING = AdvertiserConfig(
    server=ServerConfig(
        host="0.0.0.0",
        port=8001,
        workers=2,
        log_level="info",
        reload=False,
    ),
    response_delay_ms=50,
)

PRODUCTION = AdvertiserConfig(
    server=ServerConfig(
        host="0.0.0.0",
        port=8001,
        workers=3,
        log_level="warning",
        reload=False,
    ),
    response_delay_ms=50,
)

ENVIRONMENTS = {
    "dev": DEVELOPMENT,
    "staging": STAGING,
    "prod": PRODUCTION,
}


def get_config(env: str = "dev") -> AdvertiserConfig:
    """Get Advertiser config for a given environment."""
    if env not in ENVIRONMENTS:
        raise ValueError(f"Unknown environment: '{env}'. Available: {list(ENVIRONMENTS.keys())}")
    return ENVIRONMENTS[env]
