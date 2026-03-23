# Modal Cloud GPU Setup

Modal is an alternative cloud GPU provider for the toolkit's AI tools. All cloud GPU tools support both RunPod (`--cloud runpod`) and Modal (`--cloud modal`).

## Why Dual Cloud GPU Support?

We added Modal alongside RunPod after a weekend of RunPod reliability issues (March 2026). Having two providers means:

- **No single point of failure** — if one provider is down, switch to the other with `--cloud modal` or `--cloud runpod`
- **Faster cold starts** — Modal typically spins up containers faster than RunPod serverless
- **Scale to zero** — both providers only charge when actively processing (no idle costs)
- **Same interface** — all tools use `--cloud runpod|modal`, same payloads, same results

RunPod remains the default (`--cloud runpod`) for backward compatibility.

## Cloud GPU Tools

All 7 cloud GPU tools support both providers:

| Tool | Backend | Use Case | Est. Cost (Modal) |
|------|---------|----------|-------------------|
| `qwen3_tts` | Qwen3-TTS | AI speech generation | ~$0.005-0.02 |
| `flux2` | FLUX.2 Klein | AI image generation | ~$0.01-0.03 |
| `image_edit` | Qwen-Image-Edit | AI image editing, style transfer | ~$0.02-0.05 |
| `upscale` | RealESRGAN | AI image upscaling (2x/4x) | ~$0.005-0.02 |
| `music_gen` | ACE-Step 1.5 | AI music generation | ~$0.02-0.10 |
| `sadtalker` | SadTalker | Talking head video | ~$0.05-0.30 |
| `dewatermark` | ProPainter | AI video inpainting | ~$0.05-0.50 |

All Modal apps use A10G GPUs (24GB VRAM) and scale to zero when idle.

## Quick Start

```bash
# 1. Install Modal CLI
pip install modal
python3 -m modal setup    # Authenticates with your Modal account

# 2. Deploy the tools you need
modal deploy docker/modal-qwen3-tts/app.py      # Speech generation
modal deploy docker/modal-flux2/app.py           # Image generation
modal deploy docker/modal-image-edit/app.py      # Image editing
modal deploy docker/modal-upscale/app.py         # Image upscaling
modal deploy docker/modal-music-gen/app.py       # Music generation
modal deploy docker/modal-sadtalker/app.py       # Talking head video
modal deploy docker/modal-propainter/app.py      # Watermark removal

# 3. Save the endpoint URLs to .env (printed after each deploy)
#    Each deploy prints a URL like:
#    https://yourname--video-toolkit-upscale-upscaler-upscale.modal.run
#
#    Add them to .env:
echo "MODAL_QWEN3_TTS_ENDPOINT_URL=https://..." >> .env
echo "MODAL_FLUX2_ENDPOINT_URL=https://..." >> .env
echo "MODAL_IMAGE_EDIT_ENDPOINT_URL=https://..." >> .env
echo "MODAL_UPSCALE_ENDPOINT_URL=https://..." >> .env
echo "MODAL_MUSIC_GEN_ENDPOINT_URL=https://..." >> .env
echo "MODAL_SADTALKER_ENDPOINT_URL=https://..." >> .env
echo "MODAL_DEWATERMARK_ENDPOINT_URL=https://..." >> .env

# 4. Use any tool with --cloud modal
python3 tools/image_edit.py --input photo.jpg --style cyberpunk --cloud modal
python3 tools/upscale.py --input photo.jpg --output photo_4x.png --cloud modal
python3 tools/music_gen.py --preset corporate-bg --duration 30 --output bg.mp3 --cloud modal
```

## Cold Starts

First request after idle will trigger a cold start while Modal loads the model:

| Tool | Cold Start | Warm Request |
|------|-----------|--------------|
| `qwen3_tts` | ~60-90s | ~5-15s |
| `flux2` | ~25-30s | ~1-3s |
| `image_edit` | ~5-8min | ~15-20s |
| `upscale` | ~25-30s | ~3-5s |
| `music_gen` | ~60-90s | ~10-30s |
| `sadtalker` | ~45-60s | ~30-60s |
| `dewatermark` | ~30-45s | varies by video length |

After 60 seconds of no requests, containers scale back to zero. No charges while idle.

## Monitoring & Billing

```bash
# Check what's running (Tasks column should be 0 when idle)
modal app list

# Check today's spend
modal billing report --for today --json

# View container logs
modal app logs video-toolkit-upscale
```

## Architecture

Each tool has its own Modal app (`docker/modal-*/app.py`), deployed independently:

- **One app per tool** — independent scaling, GPU assignment, and lifecycle
- **Web endpoints** — HTTP POST via `@modal.fastapi_endpoint`, no `modal` pip dependency needed on the client
- **Same payload format** — tools send `{"input": {...}}` to both RunPod and Modal
- **R2 file transfer** — large results upload to Cloudflare R2 (if configured), otherwise base64
- **Scale to zero** — `scaledown_window=60` means containers shut down after 1 minute idle

The client-side abstraction lives in `tools/cloud_gpu.py`, which routes `call_cloud_endpoint()` to either `_call_runpod()` (submit + poll) or `_call_modal()` (synchronous POST).

## Differences from RunPod

| Aspect | RunPod | Modal |
|--------|--------|-------|
| Setup | `--setup` flag (automated GraphQL) | `modal deploy` (manual) |
| Invocation | Async submit + poll | Synchronous HTTP POST |
| Cold start | Slower (Docker pull) | Faster (cached layers) |
| GPU selection | Per-endpoint config | Per-app in `app.py` |
| Auth | `RUNPOD_API_KEY` | `MODAL_TOKEN_ID` + `MODAL_TOKEN_SECRET` (optional for web endpoints) |
| Default | Yes (`--cloud runpod`) | Opt-in (`--cloud modal`) |
