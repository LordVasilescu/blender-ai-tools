# © 2026 Mathew. All rights reserved.
"""Quick Sharp-mode test: generate one clip via ComfyUI API and report the file."""
import json, sys, time, urllib.request
from video_studio import workflow, API, STYLES, WAN_NEG

prompt = sys.argv[1]
style = sys.argv[2] if len(sys.argv) > 2 else "Cyberpunk Anime"
add, neg = STYLES[style]
styled = f"{prompt}, {add}"
negative = (WAN_NEG + ", " + neg) if neg else WAN_NEG
wf = workflow(styled, seed=7, w=720, h=720, length=49, sharp=True, negative=negative)
req = urllib.request.Request(f"{API}/prompt", data=json.dumps({"prompt": wf}).encode(),
                             headers={"Content-Type": "application/json"})
pid = json.loads(urllib.request.urlopen(req, timeout=60).read())["prompt_id"]
print(f"queued {pid}, rendering Sharp 720p...", flush=True)
t0 = time.time()
while True:
    time.sleep(3)
    hist = json.loads(urllib.request.urlopen(f"{API}/history/{pid}", timeout=30).read())
    if pid in hist:
        e = hist[pid]
        if e.get("status", {}).get("status_str") == "error":
            print("ERROR:", json.dumps(e.get("status"))[:500]); sys.exit(1)
        for node in e.get("outputs", {}).values():
            for it in node.get("images", []) + node.get("gifs", []) + node.get("videos", []):
                if isinstance(it, dict) and it.get("filename", "").endswith((".mp4", ".webm")):
                    print(f"DONE in {time.time()-t0:.0f}s -> {it['filename']}"); sys.exit(0)
    if time.time() - t0 > 1500:
        print("timeout"); sys.exit(1)
