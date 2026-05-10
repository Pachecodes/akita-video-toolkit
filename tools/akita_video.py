#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from akita_providers.common import load_config, write_json
from akita_providers import episteme


def slugify(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-").replace("--", "-")


def command_plan(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    output_root = Path(config.get("default_output_root", "projects"))
    slug = slugify(args.name or f"{args.brand}-{args.template}")
    project_dir = output_root / args.brand / slug
    project_dir.mkdir(parents=True, exist_ok=True)
    for subdir in ["assets", "layers", "recordings", "audio", "renders", "recipes"]:
        (project_dir / subdir).mkdir(exist_ok=True)

    project: dict[str, Any] = {
        "name": slug,
        "brand": args.brand,
        "template": args.template,
        "format": args.format,
        "brief": args.brief,
        "phase": "planning",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "providers": config.get("providers", {}),
        "next_actions": [
            "Write script.md with scene-by-scene narration.",
            "Choose composition engine: hyperframes for reels/motion, remotion for structured demos.",
            "Generate or record required assets into assets/ and recordings/.",
            "Render preview into renders/ and document recipe under recipes/.",
        ],
    }
    write_json(project_dir / "project.json", project)
    (project_dir / "brief.md").write_text(f"# {slug}\n\n{args.brief}\n")
    (project_dir / "script.md").write_text(f"# {slug} Script\n\nTODO: scene-by-scene script.\n")
    (project_dir / "approvals.md").write_text(f"# {slug} Approvals\n\n- Created: {project['created_at']}\n")
    print(json.dumps({"status": "created", "project_dir": str(project_dir), "project": project}, indent=2, ensure_ascii=False))
    return 0


def command_health(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    providers = config.get("providers", {})
    epi = providers.get("episteme", {})
    result = episteme.health(
        epi.get("ollama_base_url", "http://192.168.68.62:11434"),
        epi.get("comfyui_base_url", "http://192.168.68.62:8188"),
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Akita Video Toolkit orchestration CLI")
    parser.add_argument("--config", help="Path to akita.config.json")
    sub = parser.add_subparsers(dest="command", required=True)

    plan = sub.add_parser("plan", help="Create a reproducible video project skeleton")
    plan.add_argument("--brand", required=True)
    plan.add_argument("--template", default="akita-product-demo")
    plan.add_argument("--format", choices=["horizontal", "vertical", "square"], default="horizontal")
    plan.add_argument("--brief", required=True)
    plan.add_argument("--name")
    plan.set_defaults(func=command_plan)

    health = sub.add_parser("health", help="Check Akita LAN creative backends")
    health.set_defaults(func=command_health)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
