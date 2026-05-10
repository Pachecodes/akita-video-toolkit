# Akita Video Toolkit Direction

This fork turns `digitalsamba/claude-code-video-toolkit` into Akita's internal video factory: a reproducible pipeline for product demos, sprint reviews, social reels, client explainers, and generated ad assets.

## Product Goal

Akita should be able to ask for a video in product language:

```bash
python3 tools/akita_video.py plan \
  --brand smartransit \
  --template akita-product-demo \
  --format horizontal \
  --brief "Show the live bus map, driver simulator, and operations dashboard."
```

The toolkit should then orchestrate asset generation, screen recording, composition, render, and durable project storage.

## Core Architecture

### 1. Asset generation layer

Creates raw media assets. Provider wrappers live under `tools/akita_providers/` and expose a small common interface.

- **Higgsfield**: UGC ads, avatars, product videos, image/video generation, Marketing Studio.
- **Fal**: fast API-backed images, clips, edits, backgrounds, and model-specific experiments.
- **Episteme / ComfyUI**: local private generation on the RTX 4090 24GB box for Flux/SDXL/video/upscale/inpaint/ControlNet workflows.
- **Playwright**: real app demo capture.
- **Existing toolkit tools**: Qwen3 TTS, ACE-Step music, SFX, FFmpeg/MoviePy utilities.

### 2. Composition layer

Turns assets into finished video.

- **HyperFrames**: HTML/CSS/GSAP motion graphics, vertical reels, captions, title cards, social pieces.
- **Remotion**: React-based structured demos, sprint reviews, data-rich walkthroughs.
- **FFmpeg/MoviePy**: final muxing, transcoding, trims, overlays, and delivery formats.

### 3. Project orchestration layer

Each video project should preserve intent, generated media, layers, recipes, approvals, and final renders.

Recommended project layout:

```txt
projects/<client>/<video-slug>/
├── brief.md
├── script.md
├── project.json
├── assets/
├── layers/
├── recordings/
├── audio/
├── renders/
├── recipes/
└── approvals.md
```

No reusable creative work should live only in `/tmp`.

## Provider Defaults

- Local config file: `akita.config.json` (copy from `akita.config.example.json`).
- Secrets stay in `.env`, shell env, or provider-native auth stores. Never commit API keys.
- Episteme defaults to LAN host `192.168.68.62` with Ollama on `:11434` and ComfyUI expected on `:8188` when enabled.

## First Internal Templates

1. `akita-product-demo`: horizontal 16:9 product walkthrough.
2. `akita-social-reel`: 9:16 HyperFrames reel with kinetic captions.
3. `akita-sprint-review`: sprint/client update with demos and summary slides.
4. `akita-ugc-ad`: Higgsfield/asset-generated ad assembled into final branded deliverables.

## First Real Use Cases

- **Smartransit demo**: live map, bus simulator, operations dashboard, municipal CTA.
- **SALO communication inbox**: patient SMS/callback/escalation story.
- **Pachebot demo**: client email/WhatsApp workflow and Pachebot handoff.

## Near-Term Implementation Slices

1. Fork baseline and preserve upstream remote.
2. Add Akita config, provider wrappers, and this direction doc.
3. Create a minimal `akita_video.py plan` command that emits a project plan skeleton.
4. Add one Akita product-demo template using existing Remotion or HyperFrames building blocks.
5. Wire one provider end-to-end, preferably Fal for fast assets or ComfyUI for Episteme-local smoke tests.
6. Produce the first Smartransit or SALO demo render.
