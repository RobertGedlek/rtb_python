import tomllib
from dataclasses import dataclass, field
from pathlib import Path

_CONFIGS_DIR = Path(__file__).parent / "configs"



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


def get_config(config_path: Path) -> AdvertiserConfig:
    """Load AdvertiserConfig from a TOML file at the given path."""
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, "rb") as f:
        data = tomllib.load(f)
    server = ServerConfig(**data.get("server", {}))
    return AdvertiserConfig(server=server, **data.get("advertiser", {}))
