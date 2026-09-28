# © 2026 Mathew. All rights reserved.
"""Download FLUX.2 (images) + Wan 2.2 14B (video) into ComfyUI, no token needed.
All from Comfy-Org public repackaged repos. Resumable.

Downloads straight into the model folders via local_dir (no separate cache copy),
and disables hf-xet (its backend hangs on Windows for these repos -> plain HTTPS)."""
import os
os.environ["HF_HUB_DISABLE_XET"] = "1"          # xet backend hangs on Windows
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
from huggingface_hub import hf_hub_download

ROOT = os.environ.get("COMFY_MODELS_DIR", r"D:\ComfyUI\models")
JOBS = [
    # (repo, path-in-repo, target subfolder)
    ("Comfy-Org/flux2-dev", "split_files/diffusion_models/flux2_dev_fp8mixed.safetensors", "diffusion_models"),
    ("Comfy-Org/flux2-dev", "split_files/text_encoders/mistral_3_small_flux2_fp8.safetensors", "text_encoders"),
    ("Comfy-Org/flux2-dev", "split_files/vae/flux2-vae.safetensors", "vae"),
    ("Comfy-Org/Wan_2.2_ComfyUI_Repackaged", "split_files/diffusion_models/wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors", "diffusion_models"),
    ("Comfy-Org/Wan_2.2_ComfyUI_Repackaged", "split_files/diffusion_models/wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors", "diffusion_models"),
    ("Comfy-Org/Wan_2.2_ComfyUI_Repackaged", "split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors", "text_encoders"),
    ("Comfy-Org/Wan_2.2_ComfyUI_Repackaged", "split_files/vae/wan_2.1_vae.safetensors", "vae"),
]

for i, (repo, rpath, sub) in enumerate(JOBS, 1):
    name = os.path.basename(rpath)
    dest_dir = os.path.join(ROOT, sub)
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, name)
    if os.path.exists(dest) and os.path.getsize(dest) > 1_000_000:
        print(f"[{i}/{len(JOBS)}] already have {name}", flush=True)
        continue
    print(f"[{i}/{len(JOBS)}] downloading {name} ...", flush=True)
    # local_dir keeps the file's repo subpath; pull it up to dest_dir/<name>.
    got = hf_hub_download(repo_id=repo, filename=rpath, local_dir=dest_dir)
    if os.path.abspath(got) != os.path.abspath(dest):
        os.replace(got, dest)
    print(f"[{i}/{len(JOBS)}] placed -> {dest}  ({os.path.getsize(dest)/1e9:.1f} GB)", flush=True)

# tidy the empty split_files/ subdirs local_dir leaves behind
for sub in ("diffusion_models", "text_encoders", "vae"):
    leftover = os.path.join(ROOT, sub, "split_files")
    if os.path.isdir(leftover):
        import shutil
        shutil.rmtree(leftover, ignore_errors=True)

print("ALL MODELS DOWNLOADED")
