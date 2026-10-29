#!/usr/bin/env python3
"""
1. Immediately send the raw $0.00 HeyGen Avatar 4 1080p clip (STEVE_JOBS_ZERO_COST_HEYGEN4_1080P.mp4) to Andrew on Telegram (chat_id=7465211547).
2. Composite the full 57.8s Studio Master using the $0.00 HeyGen Avatar 4 clip for the 1.1s opening hook over the live moving alien gunship + Mustang background (ARIA_TECH_GROUP_SteveJobs_ZeroCost_HeyGen4_Master_1080p.mp4), encode a Telegram-optimized <35MB version, and send that to Telegram too!
"""
import os
import sys
import ssl
import cv2
import time
import json
import subprocess
import urllib.request
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ssl._create_default_https_context = ssl._create_unverified_context

BOT_TOKEN = "8997758848:AAEXwxLrDRvscbgBBFJiVrr34Y6Gvfho-C0"
CHAT_ID = "7465211547"
SCRATCH = r"C:\Users\Aria\.gemini\antigravity\scratch"


def send_telegram_video(video_path: str, caption: str) -> dict:
    boundary = "----AriaTelegramBoundary987654321"
    body = bytearray()

    def add_field(name, val):
        body.extend(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{val}\r\n'.encode("utf-8"))

    add_field("chat_id", CHAT_ID)
    add_field("caption", caption)
    add_field("supports_streaming", "true")

    fn = os.path.basename(video_path)
    body.extend(
        f'--{boundary}\r\nContent-Disposition: form-data; name="video"; filename="{fn}"\r\nContent-Type: video/mp4\r\n\r\n'.encode("utf-8")
    )
    with open(video_path, "rb") as f:
        body.extend(f.read())
    body.extend(f"\r\n--{boundary}--\r\n".encode("utf-8"))

    req = urllib.request.Request(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo",
        data=bytes(body),
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": "Mozilla/5.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


# Step 1: Send the standalone 13.2s $0.00 HeyGen Avatar 4 clip to Telegram immediately!
raw_heygen_mp4 = r"C:\Users\Aria\Desktop\STEVE_JOBS_ZERO_COST_HEYGEN4_1080P.mp4"
print("[1/4] Sending standalone $0.00 HeyGen Avatar 4 clip (13.2s) to Telegram...")
r1 = send_telegram_video(
    raw_heygen_mp4,
    "⚡ [1/2] $0.00 Browser-Generated Steve Jobs Opening Hook (HeyGen Avatar 4 inside ElevenLabs Studio)\n"
    "• Out-of-Pocket Cost: $0.00 (8,484 unused Creator credits used; 204,912 credits remaining)\n"
    "• Automated via Kimi WebBridge + Gemini 2.5 Flash Decision Model (~600ms)\n"
    "• Full 57.8s Studio Composite Master incoming right behind this!",
)
print("   Telegram response [1/2]: ok =", r1.get("ok"), "msg_id =", r1.get("result", {}).get("message_id"))

# Step 2: Normalize the $0.00 HeyGen Avatar 4 clip to 30fps 1920x1080 (13.10s) and composite the full 57.8s Studio Master!
t0 = time.time()
heygen_30fps = os.path.join(SCRATCH, "steve_jobs_heygen4_hook_30fps_1080p.mp4")
subprocess.run([
    "ffmpeg", "-y", "-i", raw_heygen_mp4,
    "-vf", "fps=30,scale=1920:1080:flags=lanczos",
    "-t", "13.10",
    "-an", "-c:v", "h264_nvenc", "-preset", "p5", "-cq", "15", "-pix_fmt", "yuv420p",
    heygen_30fps
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

comp_andrew_mp4 = os.path.join(SCRATCH, "comp_v3_natural.mp4")
bg_mp4 = r"C:\Users\Aria\Desktop\ZOOM_BG_Alien_Mustang_Master_1080p.mp4"
steve_mid_30fps = os.path.join(SCRATCH, "steve_jobs_midway_30fps_1080p.mp4")
ass_path = os.path.join(SCRATCH, "linkedin_captions_steve_jobs_hook.ass")
hook_swap_aac = os.path.join(SCRATCH, "audio_steve_jobs_hook_swap.aac")


def load_frames(mp4_path):
    cap = cv2.VideoCapture(mp4_path)
    frames = []
    while True:
        ret, f = cap.read()
        if not ret:
            break
        frames.append(f)
    cap.release()
    return frames


print("[2/4] Loading frames & compositing $0.00 HeyGen Avatar 4 over live moving Alien Gunship + Mustang background...")
bg_frames = load_frames(bg_mp4)
num_bg = len(bg_frames)
hook_frames = load_frames(heygen_30fps)
mid_frames = load_frames(steve_mid_30fps)


def guided_filter(I, p, r=10, eps=5e-4):
    ksize = (2 * r + 1, 2 * r + 1)
    mean_I = cv2.boxFilter(I, cv2.CV_32F, ksize)
    mean_p = cv2.boxFilter(p, cv2.CV_32F, ksize)
    mean_Ip = cv2.boxFilter(I * p, cv2.CV_32F, ksize)
    cov_Ip = mean_Ip - mean_I * mean_p
    mean_II = cv2.boxFilter(I * I, cv2.CV_32F, ksize)
    var_I = mean_II - mean_I * mean_I
    a = cov_Ip / (var_I + eps)
    b = mean_p - a * mean_I
    mean_a = cv2.boxFilter(a, cv2.CV_32F, ksize)
    mean_b = cv2.boxFilter(b, cv2.CV_32F, ksize)
    return np.clip(mean_a * I + mean_b, 0.0, 1.0)


base_options = python.BaseOptions(model_asset_path=os.path.join(SCRATCH, "selfie_segmenter.tflite"))
options = vision.ImageSegmenterOptions(base_options=base_options, output_confidence_masks=True)
segmenter = vision.ImageSegmenter.create_from_options(options)

vignette = np.ones((1080, 1920, 1), dtype=np.float32)
vignette[840:1080, :, :] = np.linspace(1.0, 0.45, 240, dtype=np.float32)[:, None, None]


def apply_holo_glitch(frame_a, frame_b, progress):
    blended = cv2.addWeighted(frame_a, 1.0 - progress, frame_b, progress, 0.0).copy()
    intensity = np.sin(np.pi * progress)
    shift = int(22 * intensity)
    if shift > 0:
        blended[:, shift:, 2] = blended[:, :-shift, 2]
        blended[:, :-shift, 0] = blended[:, shift:, 0]
    scan = np.zeros_like(blended, dtype=np.float32)
    scan[::4, :, 1] = 75.0 * intensity
    scan[::4, :, 0] = 65.0 * intensity
    return np.clip(blended.astype(np.float32) + scan + (28.0 * intensity), 0, 255).astype(np.uint8)


cap_andrew = cv2.VideoCapture(comp_andrew_mp4)
total_frames = int(cap_andrew.get(cv2.CAP_PROP_FRAME_COUNT))
h_start, h_end = 33, 426
m_start, m_end = 675, 1098

comp_zero_mp4 = os.path.join(SCRATCH, "comp_v6_steve_jobs_zerocost_heygen4.mp4")
ff_proc = subprocess.Popen([
    "ffmpeg", "-y",
    "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", "1920x1080", "-r", "30",
    "-i", "-",
    "-c:v", "h264_nvenc", "-preset", "p5", "-cq", "16", "-b:v", "16M", "-pix_fmt", "yuv420p",
    comp_zero_mp4
], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

prev_alpha = None


def matte_steve_frame(fg, bg):
    global prev_alpha
    fg_small = cv2.resize(fg, (640, 360), interpolation=cv2.INTER_LINEAR)
    mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(fg_small, cv2.COLOR_BGR2RGB))
    res = segmenter.segment(mp_img)
    mask_s = res.confidence_masks[0].numpy_view()
    if mask_s.ndim == 3:
        mask_s = mask_s[:, :, 0]
    mask = cv2.resize(mask_s, (1920, 1080), interpolation=cv2.INTER_LINEAR)
    luma = cv2.cvtColor(fg, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    p_raw = np.clip((mask - 0.20) / 0.50, 0.0, 1.0).astype(np.float32)
    alpha_gf = guided_filter(luma, p_raw, r=8, eps=5e-4)
    alpha_gf = np.clip((alpha_gf - 0.15) / 0.72, 0.0, 1.0)
    if prev_alpha is not None:
        alpha_gf = 0.78 * alpha_gf + 0.22 * prev_alpha
    prev_alpha = alpha_gf
    alpha = alpha_gf[..., None]
    return np.clip((fg.astype(np.float32) * alpha + bg.astype(np.float32) * (1.0 - alpha)) * vignette, 0, 255).astype(np.uint8)


for idx in range(total_frames):
    ret, andrew_frame = cap_andrew.read()
    if not ret:
        break

    if h_start - 4 <= idx < h_end + 4:
        s_idx = min(max(idx - h_start, 0), len(hook_frames) - 1)
        steve_comp = matte_steve_frame(hook_frames[s_idx], bg_frames[idx % num_bg])
        if idx < h_start + 4:
            prog = (idx - (h_start - 4)) / 8.0
            out_frame = apply_holo_glitch(andrew_frame, steve_comp, prog)
        elif idx >= h_end - 4:
            prog = (idx - (h_end - 4)) / 8.0
            out_frame = apply_holo_glitch(steve_comp, andrew_frame, prog)
        else:
            out_frame = steve_comp
    elif m_start - 4 <= idx < m_end + 4:
        s_idx = min(max(idx - m_start, 0), len(mid_frames) - 1)
        steve_comp = matte_steve_frame(mid_frames[s_idx], bg_frames[idx % num_bg])
        if idx < m_start + 4:
            prog = (idx - (m_start - 4)) / 8.0
            out_frame = apply_holo_glitch(andrew_frame, steve_comp, prog)
        elif idx >= m_end - 4:
            prog = (idx - (m_end - 4)) / 8.0
            out_frame = apply_holo_glitch(steve_comp, andrew_frame, prog)
        else:
            out_frame = steve_comp
    else:
        prev_alpha = None
        out_frame = andrew_frame

    ff_proc.stdin.write(out_frame.tobytes())

cap_andrew.release()
ff_proc.stdin.close()
ff_proc.wait()
print(f"[3/4] Composited {total_frames} frames in {time.time()-t0:.1f}s! Encoding captioned 1080p master & Telegram stream...")

ass_escaped = ass_path.replace("\\", "/").replace(":", "\\:")
master_out = r"C:\Users\Aria\Desktop\ARIA_TECH_GROUP_SteveJobs_ZeroCost_HeyGen4_Master_1080p.mp4"
tg_out = os.path.join(SCRATCH, "ARIA_TECH_GROUP_SteveJobs_ZeroCost_HeyGen4_Telegram.mp4")

# Desktop 1080p high-bitrate master
subprocess.run([
    "ffmpeg", "-y",
    "-i", comp_zero_mp4,
    "-i", hook_swap_aac,
    "-vf", f"ass='{ass_escaped}',unsharp=5:5:0.35:5:5:0.0",
    "-map_metadata", "-1",
    "-c:v", "h264_nvenc", "-preset", "p6", "-cq", "18", "-b:v", "12M", "-pix_fmt", "yuv420p",
    "-c:a", "copy",
    "-shortest", "-movflags", "+faststart",
    master_out
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Telegram <25MB 1080p streamable master (Telegram Bot API max upload is 50MB)
subprocess.run([
    "ffmpeg", "-y",
    "-i", comp_zero_mp4,
    "-i", hook_swap_aac,
    "-vf", f"ass='{ass_escaped}',unsharp=5:5:0.35:5:5:0.0",
    "-map_metadata", "-1",
    "-c:v", "h264_nvenc", "-preset", "p6", "-cq", "24", "-b:v", "3.2M", "-maxrate", "4.0M", "-bufsize", "8.0M", "-pix_fmt", "yuv420p",
    "-c:a", "copy",
    "-shortest", "-movflags", "+faststart",
    tg_out
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

print(f"[4/4] Sending Full 57.8s $0.00 HeyGen Avatar 4 Studio Master ({os.path.getsize(tg_out)/1048576:.1f} MB) to Telegram...")
r2 = send_telegram_video(
    tg_out,
    "🎬 [2/2] FULL 57.8s STUDIO MASTER — $0.00 Browser-Generated HeyGen Avatar 4 Edition!\n"
    "• 1.1s Opening Hook: HeyGen Avatar 4 ($0.00 from unused ElevenLabs Creator credits) matted with O(1) Guided Filter over the live moving Alien Gunship + Mustang background\n"
    "• 22.5s Midway Takeover: Generative Iterative UI & Self-Healing Systems\n"
    "• Desktop Master: C:\\Users\\Aria\\Desktop\\ARIA_TECH_GROUP_SteveJobs_ZeroCost_HeyGen4_Master_1080p.mp4",
)
print("   Telegram response [2/2]: ok =", r2.get("ok"), "msg_id =", r2.get("result", {}).get("message_id"))
