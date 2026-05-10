from __future__ import annotations

import json
import subprocess
from typing import Any

from .common import ProviderResult


def generate(model: str, prompt: str, *, args: list[str] | None = None, dry_run: bool = False) -> ProviderResult:
    cmd = ["higgsfield", "generate", "create", model, "--prompt", prompt, "--wait", "--json"]
    if args:
        cmd.extend(args)
    if dry_run:
        return ProviderResult("higgsfield", "asset", "dry_run", metadata={"cmd": cmd})

    completed = subprocess.run(cmd, check=True, text=True, capture_output=True)
    try:
        payload: Any = json.loads(completed.stdout)
    except json.JSONDecodeError:
        payload = {"stdout": completed.stdout}
    return ProviderResult("higgsfield", "asset", "complete", metadata={"cmd": cmd, "response": payload})
