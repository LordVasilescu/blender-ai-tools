# © 2026 Mathew. All rights reserved.
# Download FLUX.2 + Wan 2.2 14B into ComfyUI via curl (fast, resumable, no hf-xet).
$ErrorActionPreference = "Continue"
$ROOT = if ($env:COMFY_MODELS_DIR) { $env:COMFY_MODELS_DIR } else { "D:\ComfyUI\models" }
$FLUX = "https://huggingface.co/Comfy-Org/flux2-dev/resolve/main/split_files"
$WAN  = "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files"

$jobs = @(
  @{ url = "$FLUX/diffusion_models/flux2_dev_fp8mixed.safetensors";              sub = "diffusion_models" },
  @{ url = "$FLUX/text_encoders/mistral_3_small_flux2_fp8.safetensors";          sub = "text_encoders" },
  @{ url = "$FLUX/vae/flux2-vae.safetensors";                                    sub = "vae" },
  @{ url = "$WAN/diffusion_models/wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors"; sub = "diffusion_models" },
  @{ url = "$WAN/diffusion_models/wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors";  sub = "diffusion_models" },
  @{ url = "$WAN/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors";          sub = "text_encoders" },
  @{ url = "$WAN/vae/wan_2.1_vae.safetensors";                                   sub = "vae" }
)

$i = 0
foreach ($j in $jobs) {
  $i++
  $name = Split-Path $j.url -Leaf
  $dir  = Join-Path $ROOT $j.sub
  New-Item -ItemType Directory -Force $dir | Out-Null
  $dest = Join-Path $dir $name
  Write-Host "[$i/$($jobs.Count)] $name -> $($j.sub)"
  # -C - resumes a partial file; --retry rides out blips.
  curl.exe -L -C - -o $dest $j.url --retry 5 --retry-delay 5 --connect-timeout 30
  $mb = [int]((Get-Item $dest -ErrorAction SilentlyContinue).Length / 1MB)
  Write-Host "[$i/$($jobs.Count)] done $name ($mb MB)"
}
Write-Host "ALL MODELS DOWNLOADED"
