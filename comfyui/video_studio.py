# © 2026 Mathew. All rights reserved.
"""Zarya Video Studio — dead-simple front-end for local Wan 2.2 video.
Type a prompt, pick size/length, hit Generate, get an mp4. No nodes.

It drives the local ComfyUI API (starts ComfyUI automatically if it's not
already running). Everything stays on this machine.
"""
import json
import os
import subprocess
import time
import urllib.request
import gradio as gr

API = "http://127.0.0.1:8188"
COMFY_DIR = os.environ.get("COMFY_DIR", r"D:\ComfyUI")
COMFY_PY = os.environ.get("COMFY_PY", os.path.join(COMFY_DIR, "venv", "Scripts", "python.exe"))
OUT_DIR = os.path.join(COMFY_DIR, "output")
WAN_NEG = ("low quality, blurry, distorted, static image, watermark, text, "
           "deformed, bad anatomy, extra limbs, jpeg artifacts")


def comfy_up():
    try:
        urllib.request.urlopen(f"{API}/system_stats", timeout=2)
        return True
    except Exception:
        return False


def ensure_comfy():
    if comfy_up():
        return
    print("Starting ComfyUI engine in the background...")
    subprocess.Popen([COMFY_PY, "main.py"], cwd=COMFY_DIR,
                     creationflags=subprocess.CREATE_NEW_CONSOLE)
    for _ in range(120):
        if comfy_up():
            print("ComfyUI ready.")
            return
        time.sleep(2)
    raise RuntimeError("ComfyUI did not start in time")


# Style presets: (text added to the prompt, extra negative terms).
STYLES = {
    "Realistic": ("cinematic, photorealistic, highly detailed", ""),
    "Anime": ("anime style, cel shaded, clean line art, vibrant colors, expressive, "
              "studio-quality 2D animation, sharp detailed anime",
              "photorealistic, 3d render, realistic photo, live action"),
    "Cyberpunk Anime": ("cyberpunk anime style, neon-soaked, cel shaded, cinematic 2D animation, "
                        "glowing neon colors, dramatic rim lighting, detailed anime like a modern "
                        "anime series, futuristic city, atmospheric",
                        "photorealistic, 3d render, realistic photo, live action, dull colors"),
}


def workflow(prompt, seed, w, h, length, sharp=False, negative=WAN_NEG, fps=16):
    # Fast = 4-step lightx2v speed LoRAs, cfg 1 (quick previews).
    # Sharp = no speed LoRA, 20 refinement steps, cfg 3.5 (much cleaner).
    if sharp:
        steps, cfg, boundary = 20, 3.5, 10
        high_model = ["75", 0]   # UNETLoader high direct -> ModelSamplingSD3
        low_model = ["76", 0]
    else:
        steps, cfg, boundary = 4, 1.0, 2
        high_model = ["83", 0]   # via lightx2v LoRA
        low_model = ["85", 0]
    wf = {
        "71": {"class_type": "CLIPLoader", "inputs": {"clip_name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors", "type": "wan", "device": "default"}},
        "73": {"class_type": "VAELoader", "inputs": {"vae_name": "wan_2.1_vae.safetensors"}},
        "75": {"class_type": "UNETLoader", "inputs": {"unet_name": "wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors", "weight_dtype": "default"}},
        "76": {"class_type": "UNETLoader", "inputs": {"unet_name": "wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors", "weight_dtype": "default"}},
        "83": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["75", 0], "lora_name": "wan2.2_t2v_lightx2v_4steps_lora_v1.1_high_noise.safetensors", "strength_model": 1.0}},
        "85": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["76", 0], "lora_name": "wan2.2_t2v_lightx2v_4steps_lora_v1.1_low_noise.safetensors", "strength_model": 1.0}},
        "86": {"class_type": "ModelSamplingSD3", "inputs": {"model": high_model, "shift": 5.0}},
        "82": {"class_type": "ModelSamplingSD3", "inputs": {"model": low_model, "shift": 5.0}},
        "89": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["71", 0], "text": prompt}},
        "72": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["71", 0], "text": negative}},
        "74": {"class_type": "EmptyHunyuanLatentVideo", "inputs": {"width": w, "height": h, "length": length, "batch_size": 1}},
        "81": {"class_type": "KSamplerAdvanced", "inputs": {"model": ["86", 0], "add_noise": "enable", "noise_seed": seed, "steps": steps, "cfg": cfg, "sampler_name": "euler", "scheduler": "simple", "positive": ["89", 0], "negative": ["72", 0], "latent_image": ["74", 0], "start_at_step": 0, "end_at_step": boundary, "return_with_leftover_noise": "enable"}},
        "78": {"class_type": "KSamplerAdvanced", "inputs": {"model": ["82", 0], "add_noise": "disable", "noise_seed": 0, "steps": steps, "cfg": cfg, "sampler_name": "euler", "scheduler": "simple", "positive": ["89", 0], "negative": ["72", 0], "latent_image": ["81", 0], "start_at_step": boundary, "end_at_step": steps, "return_with_leftover_noise": "disable"}},
        "87": {"class_type": "VAEDecode", "inputs": {"samples": ["78", 0], "vae": ["73", 0]}},
        "88": {"class_type": "CreateVideo", "inputs": {"images": ["87", 0], "fps": fps}},
        "80": {"class_type": "SaveVideo", "inputs": {"video": ["88", 0], "filename_prefix": "zarya_vid", "format": "auto", "codec": "auto"}},
    }
    return wf


SIZES = {"Square 640": (640, 640), "Sharp square 720": (720, 720),
         "Widescreen 832x480": (832, 480), "Widescreen HD 1280x720": (1280, 720),
         "Tall / phone 480x832": (480, 832), "Fast small 480": (480, 480)}
LENGTHS = {"3 seconds (faster)": 49, "5 seconds": 81}
QUALITY = {"Fast (quick preview)": False, "Sharp (slower, much cleaner)": True}


def generate(prompt, size, length_label, quality_label, style_label, seed_text, progress=gr.Progress()):
    if not prompt.strip():
        return None, "Type what you want to see first, choom."
    progress(0, desc="Warming up the engine...")
    ensure_comfy()
    w, h = SIZES[size]
    length = LENGTHS[length_label]
    sharp = QUALITY[quality_label]
    style_add, style_neg = STYLES[style_label]
    styled_prompt = f"{prompt.strip()}, {style_add}"
    negative = (WAN_NEG + ", " + style_neg) if style_neg else WAN_NEG
    seed = int(seed_text) if seed_text.strip().isdigit() else int(time.time()) % 1_000_000
    wf = workflow(styled_prompt, seed, w, h, length, sharp=sharp, negative=negative)
    req = urllib.request.Request(f"{API}/prompt", data=json.dumps({"prompt": wf}).encode(),
                                 headers={"Content-Type": "application/json"})
    res = json.loads(urllib.request.urlopen(req, timeout=60).read())
    pid = res["prompt_id"]
    t0 = time.time()
    progress(0.1, desc="Painting your video frame by frame...")
    while True:
        time.sleep(2)
        hist = json.loads(urllib.request.urlopen(f"{API}/history/{pid}", timeout=30).read())
        if pid in hist:
            entry = hist[pid]
            if entry.get("status", {}).get("status_str") == "error":
                return None, "Generation hit an error. Try again or tell Zarya."
            for node in entry.get("outputs", {}).values():
                for key in ("images", "gifs", "videos"):
                    for item in node.get(key, []):
                        if isinstance(item, dict) and item.get("filename", "").endswith((".mp4", ".webm")):
                            path = os.path.join(OUT_DIR, item.get("subfolder", ""), item["filename"])
                            return path, f"Done in {time.time()-t0:.0f}s — saved to {path}"
        elapsed = time.time() - t0
        progress(min(0.95, 0.1 + elapsed / 360), desc=f"Rendering... {elapsed:.0f}s")
        if elapsed > 1800:
            return None, "Timed out. Sharp mode at high resolution is slow; try a smaller size."


with gr.Blocks(title="Zarya Video Studio") as demo:
    gr.Markdown("# Zarya Video Studio\nLocal AI video on your RTX 5090. Free, private, unlimited. "
                "First clip after opening is slow (loads the models); after that it's faster.")
    with gr.Row():
        with gr.Column():
            prompt = gr.Textbox(label="What should the video show?", lines=3,
                                placeholder="a neon cyberpunk city at night, rain falling, camera slowly flying forward")
            style = gr.Radio(list(STYLES.keys()), value="Realistic", label="Style")
            quality = gr.Radio(list(QUALITY.keys()), value="Fast (quick preview)", label="Quality — Fast to test, Sharp for the real thing")
            size = gr.Radio(list(SIZES.keys()), value="Square 640", label="Size (bigger = sharper but slower)")
            length = gr.Radio(list(LENGTHS.keys()), value="3 seconds (faster)", label="Length")
            seed = gr.Textbox(label="Seed (leave blank for random; reuse a number to repeat a look)")
            go = gr.Button("Generate Video", variant="primary")
        with gr.Column():
            video = gr.Video(label="Your video")
            status = gr.Markdown()
    go.click(generate, [prompt, size, length, quality, style, seed], [video, status])

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7861, inbrowser=True)
