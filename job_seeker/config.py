"""Settings from config.yaml and secrets from .env.

This is the single place that knows where files live. Everything else asks
`Settings` for a path instead of hard-coding one.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

CONFIG_FILE = Path("config.yaml")


@dataclass(frozen=True)
class Settings:
    data_dir: Path = Path("data")
    raw: dict[str, Any] = field(default_factory=dict)  # the full config.yaml contents

    @property
    def profile_path(self) -> Path:
        return self.data_dir / "profile.yaml"

    @property
    def db_path(self) -> Path:
        return self.data_dir / "job_seeker.db"


def load_settings(path: Path = CONFIG_FILE) -> Settings:
    """Load .env into the environment and read config.yaml.

    config.yaml is optional: without it, the defaults above are used.
    """
    load_dotenv()
    if not path.exists():
        return Settings()
    with path.open() as f:
        raw = yaml.safe_load(f) or {}
    data_dir = raw.get("paths", {}).get("data_dir", "data")
    return Settings(data_dir=Path(data_dir), raw=raw)
