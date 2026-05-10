from __future__ import annotations

import json
import urllib.request

from .common import ProviderResult
from .comfyui import health as comfyui_health


def ollama_tags(base_url: str = "http://192.168.68.62:11434") -> ProviderResult:
    url = base_url.rstrip("/") + "/api/tags"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
        return ProviderResult("episteme", "ollama", "ok", metadata={"base_url": base_url, "models": data.get("models", [])})
    except Exception as exc:  # noqa: BLE001
        return ProviderResult("episteme", "ollama", "error", metadata={"base_url": base_url, "error": str(exc)})


def health(ollama_base_url: str = "http://192.168.68.62:11434", comfyui_base_url: str = "http://192.168.68.62:1122") -> dict[str, dict]:
    return {
        "ollama": ollama_tags(ollama_base_url).to_dict(),
        "comfyui": comfyui_health(comfyui_base_url).to_dict(),
    }
