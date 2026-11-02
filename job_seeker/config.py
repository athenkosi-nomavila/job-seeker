"""Loading settings from config.yaml and secrets from .env."""

from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

DEFAULT_CONFIG = Path("config.yaml")


def load_config(path: Path = DEFAULT_CONFIG) -> dict[str, Any]:
    """Read config.yaml and load .env into the environment.

    Raises FileNotFoundError with a hint if config.yaml hasn't been created yet.
    """
    load_dotenv()
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Copy config.example.yaml to {path} and edit it."
        )
    with path.open() as f:
        return yaml.safe_load(f) or {}
