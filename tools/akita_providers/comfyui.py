from __future__ import annotations

import json
import urllib.request
from typing import Any

from .common import ProviderResult


def health(base_url: str = "http://192.168.68.62:1122") -> ProviderResult:
    url = base_url.rstrip("/") + "/system_stats"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
        return ProviderResult("comfyui", "health", "ok", metadata={"base_url": base_url, "system_stats": data})
    except Exception as exc:  # noqa: BLE001 - health command should report any connectivity failure.
        return ProviderResult("comfyui", "health", "error", metadata={"base_url": base_url, "error": str(exc)})


def queue_prompt(workflow: dict[str, Any], base_url: str = "http://192.168.68.62:1122", *, dry_run: bool = False) -> ProviderResult:
    if dry_run:
        return ProviderResult("comfyui", "workflow", "dry_run", metadata={"base_url": base_url, "workflow_node_count": len(workflow)})

    url = base_url.rstrip("/") + "/prompt"
    body = json.dumps({"prompt": workflow}).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))
    return ProviderResult("comfyui", "workflow", "queued", id=data.get("prompt_id"), metadata={"base_url": base_url, "response": data})
