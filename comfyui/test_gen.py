# © 2026 Mathew. All rights reserved.
"""Drive ComfyUI via its API: submit a workflow, wait, report output file.
Usage: python test_gen.py flux2 "<prompt>"     (text-to-image)
"""
import json, sys, time, urllib.request

API = "http://127.0.0.1:8188"


def flux2_workflow(prompt, seed=42, steps=20, w=1024, h=1024):
    return {
        "12": {"class_type": "UNETLoader", "inputs": {"unet_name": "flux2_dev_fp8mixed.safetensors", "weight_dtype": "default"}},
        "38": {"class_type": "CLIPLoader", "inputs": {"clip_name": "mistral_3_small_flux2_fp8.safetensors", "type": "flux2", "device": "default"}},
        "10": {"class_type": "VAELoader", "inputs": {"vae_name": "flux2-vae.safetensors"}},
        "6":  {"class_type": "CLIPTextEncode", "inputs": {"clip": ["38", 0], "text": prompt}},
        "26": {"class_type": "FluxGuidance", "inputs": {"conditioning": ["6", 0], "guidance": 4}},
        "47": {"class_type": "EmptyFlux2LatentImage", "inputs": {"width": w, "height": h, "batch_size": 1}},
        "48": {"class_type": "Flux2Scheduler", "inputs": {"steps": steps, "width": w, "height": h}},
        "16": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
        "25": {"class_type": "RandomNoise", "inputs": {"noise_seed": seed}},
        "22": {"class_type": "BasicGuider", "inputs": {"model": ["12", 0], "conditioning": ["26", 0]}},
        "13": {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["25", 0], "guider": ["22", 0], "sampler": ["16", 0], "sigmas": ["48", 0], "latent_image": ["47", 0]}},
        "8":  {"class_type": "VAEDecode", "inputs": {"samples": ["13", 0], "vae": ["10", 0]}},
        "9":  {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": "flux2_test"}},
    }


WAN_NEG = ("low quality, blurry, distorted, static image, watermark, text, "
           "deformed, bad anatomy, extra limbs, jpeg artifacts")


def wan2v_workflow(prompt, seed=42, w=640, h=640, length=81, fps=16):
    return {
        "71": {"class_type": "CLIPLoader", "inputs": {"clip_name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors", "type": "wan", "device": "default"}},
        "73": {"class_type": "VAELoader", "inputs": {"vae_name": "wan_2.1_vae.safetensors"}},
        "75": {"class_type": "UNETLoader", "inputs": {"unet_name": "wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors", "weight_dtype": "default"}},
        "76": {"class_type": "UNETLoader", "inputs": {"unet_name": "wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors", "weight_dtype": "default"}},
        "83": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["75", 0], "lora_name": "wan2.2_t2v_lightx2v_4steps_lora_v1.1_high_noise.safetensors", "strength_model": 1.0}},
        "85": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["76", 0], "lora_name": "wan2.2_t2v_lightx2v_4steps_lora_v1.1_low_noise.safetensors", "strength_model": 1.0}},
        "86": {"class_type": "ModelSamplingSD3", "inputs": {"model": ["83", 0], "shift": 5.0}},
        "82": {"class_type": "ModelSamplingSD3", "inputs": {"model": ["85", 0], "shift": 5.0}},
        "89": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["71", 0], "text": prompt}},
        "72": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["71", 0], "text": WAN_NEG}},
        "74": {"class_type": "EmptyHunyuanLatentVideo", "inputs": {"width": w, "height": h, "length": length, "batch_size": 1}},
        "81": {"class_type": "KSamplerAdvanced", "inputs": {"model": ["86", 0], "add_noise": "enable", "noise_seed": seed, "steps": 4, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "positive": ["89", 0], "negative": ["72", 0], "latent_image": ["74", 0], "start_at_step": 0, "end_at_step": 2, "return_with_leftover_noise": "enable"}},
        "78": {"class_type": "KSamplerAdvanced", "inputs": {"model": ["82", 0], "add_noise": "disable", "noise_seed": 0, "steps": 4, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "positive": ["89", 0], "negative": ["72", 0], "latent_image": ["81", 0], "start_at_step": 2, "end_at_step": 4, "return_with_leftover_noise": "disable"}},
        "87": {"class_type": "VAEDecode", "inputs": {"samples": ["78", 0], "vae": ["73", 0]}},
        "88": {"class_type": "CreateVideo", "inputs": {"images": ["87", 0], "fps": fps}},
        "80": {"class_type": "SaveVideo", "inputs": {"video": ["88", 0], "filename_prefix": "wan_test", "format": "auto", "codec": "auto"}},
    }


def post(path, payload):
    req = urllib.request.Request(f"{API}{path}", data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def get(path):
    with urllib.request.urlopen(f"{API}{path}", timeout=60) as r:
        return json.loads(r.read())


kind, prompt = sys.argv[1], sys.argv[2]
wf = {"flux2": flux2_workflow, "wan": wan2v_workflow}[kind](prompt)
print(f"submitting {kind} workflow...", flush=True)
t0 = time.time()
res = post("/prompt", {"prompt": wf})
if "error" in res:
    print("VALIDATION ERROR:", json.dumps(res, indent=2)[:2000]); sys.exit(1)
pid = res["prompt_id"]
print(f"queued prompt_id={pid}", flush=True)

while True:
    time.sleep(2)
    hist = get(f"/history/{pid}")
    if pid in hist:
        entry = hist[pid]
        status = entry.get("status", {})
        if status.get("status_str") == "error":
            print("EXECUTION ERROR:", json.dumps(status, indent=2)[:2000]); sys.exit(1)
        outs = entry.get("outputs", {})
        # find any produced file (images for flux, video/gifs for wan)
        for node in outs.values():
            for key in ("images", "gifs", "videos", "video"):
                for item in node.get(key, []):
                    if isinstance(item, dict) and item.get("filename"):
                        print(f"DONE in {time.time()-t0:.1f}s -> output/{item.get('subfolder','')}/{item['filename']}")
                        sys.exit(0)
        if status.get("completed"):
            print("completed but no output file?", json.dumps(outs)[:800]); sys.exit(1)
    if time.time() - t0 > 1200:
        print("timeout 1200s"); sys.exit(1)
