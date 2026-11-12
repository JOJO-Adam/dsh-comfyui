# dsh-comfyui · JOJO&Adam

A ComfyUI production pack for DeepSeek Harness: environment doctor, zero-dependency API client, workflow design/upgrade, measured parameter matrices, failure triage, batch consistency — plus video/audio/3D/LoRA/vision pipelines.

Not “how to click around in ComfyUI” — it makes the agent actually generate images, diagnose broken output and run a production line.

## Install

```bash
dsh plugin --profile web add @jojonadam/dsh-comfyui
dsh plugin --profile desktop add @jojonadam/dsh-comfyui
```

Requires a reachable ComfyUI server (default `127.0.0.1:8188`). The client is stdlib-only Python.

## What's inside (20 skills)

- Execution: `comfyui-studio` (entry point + client + example workflow), `comfyui-env`, `comfyui-generation-exec`, `comfyui-mcp-bridge`, `comfyui-model-management`, `comfyui-handoff`, `comfyui-hardware-audit`
- Standards & process: `comfyui-sop`, `comfyui-workflow-design`, `comfyui-workflow-upgrade`, `comfyui-param-tuning`, `comfyui-prompt-structure`, `comfyui-batch-consistency`, `comfyui-failure-tree`, `comfyui-production-sop`
- Pipelines: `comfyui-video-pipeline`, `comfyui-audio-pipeline`, `comfyui-3d-pipeline`, `comfyui-training-lora`, `comfyui-vision-utils`

Every capability is tagged `[measured]` / `[external]` / `[unverified]`; no static VRAM tiers.

## Boundaries

- Does not bundle models or workflows; weights must already exist on your server.
- Parameter matrices come from a measured Apple M5 run — re-calibrate for other hardware.
- Nothing is sent to the cloud; only your configured local endpoint is called.

## Verify

```bash
node test/provider.test.mjs
python3 skills/comfyui-studio/scripts/comfy_client.py doctor
```

## License

MIT · JOJO & Adam · <https://jojo-adam.com>
