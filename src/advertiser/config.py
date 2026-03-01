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


# --- Advertiser 1 (adv-001, port 8001) ---

DEVELOPMENT_1 = AdvertiserConfig(
    server=ServerConfig(
        host="127.0.0.1",
        port=8001,
        workers=1,
        log_level="debug",
        reload=True,
    ),
    advertiser_id="adv-001",
    response_delay_ms=30,
)

STAGING_1 = AdvertiserConfig(
    server=ServerConfig(
        host="0.0.0.0",
        port=8001,
        workers=2,
        log_level="info",
        reload=False,
    ),
    advertiser_id="adv-001",
    response_delay_ms=50,
)

PRODUCTION_1 = AdvertiserConfig(
    server=ServerConfig(
        host="0.0.0.0",
        port=8001,
        workers=3,
        log_level="warning",
        reload=False,
    ),
    advertiser_id="adv-001",
    response_delay_ms=50,
)

# --- Advertiser 2 (adv-002, port 8002) ---

DEVELOPMENT_2 = AdvertiserConfig(
    server=ServerConfig(
        host="127.0.0.1",
        port=8002,
        workers=1,
        log_level="debug",
        reload=True,
    ),
    advertiser_id="adv-002",
    response_delay_ms=40,
    min_bid=1.0,
    max_bid=8.0,
)

STAGING_2 = AdvertiserConfig(
    server=ServerConfig(
        host="0.0.0.0",
        port=8002,
        workers=2,
        log_level="info",
        reload=False,
    ),
    advertiser_id="adv-002",
    response_delay_ms=50,
    min_bid=1.0,
    max_bid=8.0,
)

PRODUCTION_2 = AdvertiserConfig(
    server=ServerConfig(
        host="0.0.0.0",
        port=8002,
        workers=3,
        log_level="warning",
        reload=False,
    ),
    advertiser_id="adv-002",
    response_delay_ms=50,
    min_bid=1.0,
    max_bid=8.0,
)

ENVIRONMENTS = {
    "dev": DEVELOPMENT_1,
    "staging": STAGING_1,
    "prod": PRODUCTION_1,
}

ENVIRONMENTS_2 = {
    "dev": DEVELOPMENT_2,
    "staging": STAGING_2,
    "prod": PRODUCTION_2,
}


def get_config(env: str = "dev") -> AdvertiserConfig:
    """Get Advertiser 1 (adv-001) config for a given environment."""
    if env not in ENVIRONMENTS:
        raise ValueError(f"Unknown environment: '{env}'. Available: {list(ENVIRONMENTS.keys())}")
    return ENVIRONMENTS[env]


def get_config_2(env: str = "dev") -> AdvertiserConfig:
    """Get Advertiser 2 (adv-002) config for a given environment."""
    if env not in ENVIRONMENTS_2:
        raise ValueError(f"Unknown environment: '{env}'. Available: {list(ENVIRONMENTS_2.keys())}")
    return ENVIRONMENTS_2[env]

