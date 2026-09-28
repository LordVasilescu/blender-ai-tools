# Blender AI Tools

A collection of tools for AI-assisted 3D and video work:

- a **live Blender bridge** that lets an AI agent run Python inside a running Blender session
- **procedural Blender scene generators**
- a **Tripo3D** text/image-to-3D command-line client
- **ComfyUI** helpers for local image and video generation

## `blender/`

### `bridge/`: live Blender command bridge
| File | What it does |
|---|---|
| `addon/meridian_blender_bridge/__init__.py` | Blender add-on. A `bpy.app.timers` poller watches an `inbox/` folder for `.py` or `.json` jobs, runs each one inside a safe VIEW_3D context override, captures stdout and tracebacks, and writes `outbox/result_<time>_<job>.json`. It writes a heartbeat to `status.json` every 2 s, restarts itself after a file load through a persistent `load_post` handler, and has a sidebar panel with Start and Stop buttons. The timer callback never raises, so a bad job cannot crash Blender |
| `bctl.ps1` | Control script: `status` (checks liveness from the heartbeat age and the process), `up`, `send`, `ping`, `doctor` |
| `start_blender_bridge.ps1` | Launches Blender as an interactive Scheduled Task, so it is not tied to the calling agent's process lifetime |
| `boot_bridge_session.py` | Startup script that frames the viewport and switches to Material Preview |
| `jobs/` | Example jobs from a real character-assembly session: importing Tripo-generated FBX parts, swapping meshes while keeping their placement, laying parts out and reporting mesh sizes |

### `scenes/`: procedural scene and animation scripts
Run these from Blender's Text Editor. Each one builds a complete animated scene in code:
- `blender_wave_ocean.py`: a 20×20 grid of pillars animated as a travelling wave
- `blender_spiral_tower.py`: a helix of rainbow-coloured cubes
- `blender_claude_core.py`, `blender_claude_core_v2.py`: glowing animated "AI core" motion-graphics pieces
- `blender_2d_arcane.py`: a 2D magic-circle animation built from curves and emission shaders
- `blender_vtuber.py`: a procedural chibi anime character, modelled from primitives and keyframed with idle animation
- `blender_tatsumaki_dance.py`: a beat-synced (125 BPM) dance keyframed onto an existing rig, including shape-key expressions
- `blender_vrm0_setup.py`, `blender_set_vrm0.py`: prepare a rig for VRM 0.x export (needs the VRM Add-on for Blender)

## `tripo/`: Tripo3D bridge (`tctl.ps1`)
A PowerShell client for the Tripo3D v2 API:
- `doctor`: checks the API key and account balance
- `text "<prompt>"`: text to 3D model
- `image <file>`: image upload, then image to 3D model, with optional smart low-poly and a face limit
- `merrix`: batch job that turns a set of character-part images into GLB meshes, each with its own polygon budget

It polls each task until it finishes and downloads the model. The API key is read only from the `TRIPO_API_KEY` environment variable.

## `comfyui/`: ComfyUI helpers
Copy these into your ComfyUI folder, or set `COMFY_DIR`.
- `video_studio.py`: **Zarya Video Studio**, a Gradio front-end (`:7861`) for Wan 2.2 14B text-to-video. Starts ComfyUI automatically if it is down. Style presets (Realistic, Anime, Cyberpunk Anime); Fast mode (4-step lightx2v LoRAs) or Sharp mode (20 steps, CFG 3.5); size and length options
- `test_gen.py`: builds FLUX.2 text-to-image and Wan 2.2 text-to-video workflows in API format, submits them and waits for the output
- `run_sharp.py`: command-line render of one Sharp-quality clip
- `download_models.py` / `download_models.ps1`: resumable downloads of FLUX.2-dev and Wan 2.2 14B weights from Comfy-Org's public Hugging Face repos, placed in the right model folders

## Tech stack

Python · Blender `bpy` / `mathutils` · PowerShell · Tripo3D REST API · ComfyUI API · Gradio · Hugging Face Hub

## Setup

- **Blender bridge:** copy `blender/bridge/addon/meridian_blender_bridge` into Blender's `scripts/addons` folder and enable it. Optionally set `MERIDIAN_BL_BRIDGE` to choose the inbox/outbox folder. Then run `.\bctl.ps1 ping`.
- **Tripo:** create an API key at platform.tripo3d.ai, then `setx TRIPO_API_KEY "<your key>"` and `.\tripo\tctl.ps1 doctor`.
- **ComfyUI:** `pip install -r comfyui/requirements.txt`, then `python download_models.py`, then `python video_studio.py`.

Example job scripts and some control scripts still use the author's workstation paths. No keys, models, .blend files or generated media are included.

---

© 2026 Mathew Vasilescu. All rights reserved. See [LICENSE](LICENSE).
