from pathlib import Path

BASE_DATA_DIR = Path("data")
BASE_CAMPAIGNS_DIR = BASE_DATA_DIR / "campaigns"
LOG_DIR = Path("logs")


def get_campaign_path(campaign_id: str) -> Path:
    if not campaign_id or "/" in campaign_id:
        raise ValueError(f"Invalid campaign_id: {campaign_id!r}")
    return BASE_CAMPAIGNS_DIR / campaign_id


def get_paths(campaign_id: str | None = None) -> dict:
    if campaign_id is None:
        raise ValueError("campaign_id is required to resolve paths")
    base = get_campaign_path(campaign_id)
    memory_dir = base / "inmemory"
    return {
        "campaign_dir": base,
        "memory_dir": memory_dir,
        "log_dir": LOG_DIR,
        "embedding_cache": memory_dir / "embedding_cache.json",
        "vector_index": base / "vector.index",
    }


def ensure_global_directories() -> None:
    BASE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    BASE_CAMPAIGNS_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def ensure_directories() -> None:
    ensure_global_directories()
