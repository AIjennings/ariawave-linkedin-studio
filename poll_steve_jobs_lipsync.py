#!/usr/bin/env python3
"""
Poll the submitted FAL lip-sync jobs (OmniHuman v1.5, Kling AI Avatar v2 Pro, Kling AI Avatar v2 Std)
until at least one completes, and download the resulting MP4s to scratch.
"""
import os
import ssl
import time
import json
import base64
import urllib.request

ssl._create_default_https_context = ssl._create_unverified_context
SCRATCH = r"C:\Users\Aria\.gemini\antigravity\scratch"

def get_fal_key():
    py_code = r"""
import json
from pathlib import Path
env = {}
for line in Path(r"C:/Users/Aria/AppData/Local/hermes/.env").read_text(encoding="utf-8", errors="ignore").splitlines():
    s = line.strip()
    if s and not s.startswith("#") and "=" in s:
        k, v = s.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
print(json.dumps({"FAL_KEY": env.get("FAL_KEY")}))
"""
    b64 = base64.b64encode(py_code.encode("utf-8")).decode("ascii")
    cmd = f"python -c \"import base64; exec(base64.b64decode('{b64}').decode('utf-8'))\""
    req = urllib.request.Request(
        "http://100.98.181.38:7777/api/gemini",
        data=json.dumps({"action": "shell", "command": cmd}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        out = json.loads(resp.read().decode("utf-8")).get("output", "").strip()
        return json.loads(out.splitlines()[-1])["FAL_KEY"]

fal_key = get_fal_key()
with open(os.path.join(SCRATCH, "steve_jobs_fal_jobs.json"), "r", encoding="utf-8") as f:
    manifest = json.load(f)

jobs = {
    "omnihuman": manifest["omnihuman"],
    "kling_pro": manifest["kling_pro"],
    "kling_std": manifest["kling_std"]
}

completed = {}
start = time.time()

while time.time() - start < 600:
    all_status = {}
    for name, job in jobs.items():
        if name in completed:
            all_status[name] = "DOWNLOADED"
            continue
        status_url = job.get("status_url")
        resp_url = job.get("response_url")
        if not status_url:
            continue
        try:
            req = urllib.request.Request(
                status_url,
                headers={"Authorization": f"Key {fal_key}", "User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=20) as r:
                st = json.loads(r.read().decode("utf-8"))
            state = st.get("status", "UNKNOWN")
            all_status[name] = state
            if state == "COMPLETED":
                rreq = urllib.request.Request(
                    resp_url,
                    headers={"Authorization": f"Key {fal_key}", "User-Agent": "Mozilla/5.0"}
                )
                with urllib.request.urlopen(rreq, timeout=30) as rr:
                    res = json.loads(rr.read().decode("utf-8"))
                vid_url = res.get("video", {}).get("url")
                if vid_url:
                    out_mp4 = os.path.join(SCRATCH, f"steve_jobs_lipsync_{name}.mp4")
                    with urllib.request.urlopen(urllib.request.Request(vid_url, headers={"User-Agent": "Mozilla/5.0"}), timeout=90) as vr:
                        with open(out_mp4, "wb") as vf:
                            vf.write(vr.read())
                    print(f"[COMPLETED] {name} -> {out_mp4} ({os.path.getsize(out_mp4)} bytes)")
                    completed[name] = out_mp4
        except Exception as e:
            all_status[name] = f"ERR: {e}"
    print(f"[{int(time.time() - start)}s] Status:", json.dumps(all_status))
    # Once we have at least omnihuman or kling_pro (or 2 models), or if all finished, break if omnihuman or kling_pro is ready
    if "omnihuman" in completed or "kling_pro" in completed or len(completed) >= 2:
        # Wait just 10 more seconds in case another one finishes right alongside it
        break
    time.sleep(8)

print("Done polling! Completed videos:", json.dumps(completed, indent=2))
