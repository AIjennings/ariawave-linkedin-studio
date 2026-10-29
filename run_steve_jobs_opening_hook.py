#!/usr/bin/env python3
r"""
Generate the Opening Hook (1.10s .. 14.20s, duration 13.10s) Steve Jobs Character & Voice Swap!
- At t=0.00s..1.10s: Andrew starts: "Before you ask —"
- At t=1.10s..14.20s: Holographic RGB morph into STEVE JOBS right on "yes, that's an alien gunship firing plasma outside my window next to my Mustang... and yes, our AI agents built my studio background too. What's happening behind me is nothing compared to what we just deployed at Aria Technology Group."
- Combined with the 22.50s..36.60s Steve Jobs segment we ALREADY rendered (kling_pro), this gives a massive 2-part Steve Jobs takeover (Opening Hook + Generative UI Core)!
"""
import os
import ssl
import time
import json
import base64
import subprocess
import urllib.request

ssl._create_default_https_context = ssl._create_unverified_context
SCRATCH = r"C:\Users\Aria\.gemini\antigravity\scratch"

def get_devbox_keys():
    py_code = r"""
import json
from pathlib import Path
env = {}
for line in Path(r"C:/Users/Aria/AppData/Local/hermes/.env").read_text(encoding="utf-8", errors="ignore").splitlines():
    s = line.strip()
    if s and not s.startswith("#") and "=" in s:
        k, v = s.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
print(json.dumps({"FAL_KEY": env.get("FAL_KEY"), "ELEVENLABS_API_KEY": env.get("ELEVENLABS_API_KEY")}))
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
        return json.loads(out.splitlines()[-1])

keys = get_devbox_keys()
fal_key = keys["FAL_KEY"]
xi_key = keys["ELEVENLABS_API_KEY"]

# 1. Extract 1.10s .. 14.20s (13.10s duration) from single_mic_dry.aac
hook_mp3 = os.path.join(SCRATCH, "andrew_hook_1_1_to_14_2.mp3")
subprocess.run([
    "ffmpeg", "-y",
    "-ss", "1.10", "-to", "14.20",
    "-i", os.path.join(SCRATCH, "single_mic_dry.aac"),
    "-c:a", "libmp3lame", "-q:a", "2",
    hook_mp3
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("1. Extracted Andrew opening hook audio:", os.path.getsize(hook_mp3))

# 2. Run ElevenLabs Speech-to-Speech (Steve Jobs voice r7xva0mJjcdjj1WdpFIG) on hook_mp3
boundary = "----AriaBoundaryHook7MA4YWxk"
body = bytearray()
def add_field(name, val):
    body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{val}\r\n".encode("utf-8"))

add_field("model_id", "eleven_multilingual_sts_v2")
add_field("voice_settings", json.dumps({"stability": 0.42, "similarity_boost": 0.95, "style": 0.50, "use_speaker_boost": True}))
body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"audio\"; filename=\"hook.mp3\"\r\nContent-Type: audio/mpeg\r\n\r\n".encode("utf-8"))
with open(hook_mp3, "rb") as f:
    body.extend(f.read())
body.extend(f"\r\n--{boundary}--\r\n".encode("utf-8"))

sts_req = urllib.request.Request(
    "https://api.elevenlabs.io/v1/speech-to-speech/r7xva0mJjcdjj1WdpFIG",
    data=bytes(body),
    headers={
        "xi-api-key": xi_key,
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Accept": "audio/mpeg"
    },
    method="POST"
)
sts_hook_out = os.path.join(SCRATCH, "steve_jobs_sts_hook.mp3")
with urllib.request.urlopen(sts_req, timeout=60) as r:
    with open(sts_hook_out, "wb") as f:
        f.write(r.read())
print("2. Generated Steve Jobs STS Opening Hook audio:", os.path.getsize(sts_hook_out))

# 3. Upload STS hook audio to FAL and reuse the iconic steve_jobs_studio_frame.jpg
def upload_to_fal(file_path: str, content_type: str) -> str:
    fn = os.path.basename(file_path)
    req = urllib.request.Request(
        "https://rest.alpha.fal.ai/storage/upload/initiate?storage_type=fal-cdn-v3",
        data=json.dumps({"file_name": fn, "content_type": content_type}).encode("utf-8"),
        headers={"Authorization": f"Key {fal_key}", "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        init_data = json.loads(r.read().decode("utf-8"))
    with open(file_path, "rb") as f:
        data = f.read()
    put_req = urllib.request.Request(
        init_data["upload_url"],
        data=data,
        headers={"Content-Type": content_type, "User-Agent": "Mozilla/5.0"},
        method="PUT"
    )
    with urllib.request.urlopen(put_req, timeout=60) as r:
        pass
    return init_data["file_url"]

with open(os.path.join(SCRATCH, "steve_jobs_fal_jobs.json"), "r", encoding="utf-8") as f:
    prev_manifest = json.load(f)

steve_img_url = prev_manifest["steve_img_url"]
sts_hook_url = upload_to_fal(sts_hook_out, "audio/mpeg")
print("3. Uploaded STS hook audio to FAL:", sts_hook_url)

def submit_fal(endpoint: str, payload: dict) -> dict:
    url = f"https://queue.fal.run/{endpoint}"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Key {fal_key}", "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

motion_prompt = "Steve Jobs in his iconic black mock turtleneck and round rimless glasses smiling and speaking charisma-filled with expressive hand gestures and natural head nod inside a cyberpunk penthouse studio with a Mustang and alien gunship outside the window"

kling_pro = submit_fal("fal-ai/kling-video/ai-avatar/v2/pro", {
    "image_url": steve_img_url,
    "audio_url": sts_hook_url,
    "prompt": motion_prompt
})
kling_std = submit_fal("fal-ai/kling-video/ai-avatar/v2/standard", {
    "image_url": steve_img_url,
    "audio_url": sts_hook_url,
    "prompt": motion_prompt
})

jobs = {"kling_pro": kling_pro, "kling_std": kling_std}
with open(os.path.join(SCRATCH, "steve_jobs_hook_jobs.json"), "w", encoding="utf-8") as f:
    json.dump(jobs, f, indent=2)
print("4. Submitted Opening Hook lip-sync jobs! Polling until completion...")

completed = {}
start = time.time()
while time.time() - start < 600:
    st_summary = {}
    for name, job in jobs.items():
        if name in completed:
            st_summary[name] = "DOWNLOADED"
            continue
        req = urllib.request.Request(
            job["status_url"],
            headers={"Authorization": f"Key {fal_key}", "User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=20) as r:
            st = json.loads(r.read().decode("utf-8"))
        state = st.get("status", "UNKNOWN")
        st_summary[name] = state
        if state == "COMPLETED":
            rreq = urllib.request.Request(
                job["response_url"],
                headers={"Authorization": f"Key {fal_key}", "User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(rreq, timeout=30) as rr:
                res = json.loads(rr.read().decode("utf-8"))
            vid_url = res.get("video", {}).get("url")
            if vid_url:
                out_mp4 = os.path.join(SCRATCH, f"steve_jobs_hook_{name}.mp4")
                with urllib.request.urlopen(urllib.request.Request(vid_url, headers={"User-Agent": "Mozilla/5.0"}), timeout=90) as vr:
                    with open(out_mp4, "wb") as vf:
                        vf.write(vr.read())
                print(f"[COMPLETED] {name} -> {out_mp4} ({os.path.getsize(out_mp4)} bytes)")
                completed[name] = out_mp4
    print(f"[{int(time.time() - start)}s] Hook Lip-Sync Status:", json.dumps(st_summary))
    if "kling_pro" in completed or len(completed) == 2:
        break
    time.sleep(8)

print("Done! Opening Hook lip-sync videos:", json.dumps(completed, indent=2))
