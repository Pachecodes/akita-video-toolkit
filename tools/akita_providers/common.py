from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
import json
import os


@dataclass
class ProviderResult:
    provider: str
    kind: str
    status: str
    output: str | None = None
    id: str | None = None
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_config(path: str | None = None) -> dict[str, Any]:
    config_path = Path(path) if path else repo_root() / "akita.config.json"
    if not config_path.exists():
        config_path = repo_root() / "akita.config.example.json"
    return json.loads(config_path.read_text())


def env_required(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
