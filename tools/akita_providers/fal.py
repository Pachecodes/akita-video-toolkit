from __future__ import annotations

import json
import urllib.request
from typing import Any

from .common import ProviderResult, env_required


def submit(model: str, payload: dict[str, Any], *, dry_run: bool = False) -> ProviderResult:
    """Submit a Fal model request.

    This is intentionally thin: different Fal models have different payloads.
    The caller owns the model-specific schema and output handling.
    """
    if dry_run:
        return ProviderResult("fal", payload.get("kind", "asset"), "dry_run", metadata={"model": model, "payload": payload})

    key = env_required("FAL_KEY")
    url = f"https://fal.run/{model.lstrip('/')}"
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Authorization": f"Key {key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        data = json.loads(response.read().decode("utf-8"))
    return ProviderResult("fal", payload.get("kind", "asset"), "submitted", metadata={"model": model, "response": data})
