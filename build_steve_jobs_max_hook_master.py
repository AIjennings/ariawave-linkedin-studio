#!/usr/bin/env python3
"""
Build the Ultimate Maximum-Hook Steve Jobs Edition (57.8s):
- 0.00s - 1.10s: Andrew opens ("Before you ask —")
- 1.10s - 14.20s: INSTANT HOLOGRAPHIC MORPH INTO STEVE JOBS for the viral opening hook!
  ("yes, that's an alien gunship firing plasma outside my window next to my Mustang... and yes, our AI agents built my studio background too. What's happening behind me is nothing compared to what we just deployed at Aria Technology Group.")
- 14.20s - 22.50s: Morph back to Andrew ("We rolled out a new Agentic Video Waiver software to brand-new employees... with ZERO training. No manuals. No onboarding sessions.")
- 22.50s - 36.60s: Second Holographic Morph into STEVE JOBS for the Generative Iterative UI / Self-Healing core!
  ("Instead of a rigid legacy screen, the system runs on generative, iterative UI managed by autonomous agents. We hire an employee — they hit an edge case — it doesn't crash. It self-heals and adapts in real time. It's amazing.")
- 36.60s - 57.80s: Morph back to Andrew for the ariawave.tech open-source announcement + Aria Technology Group consulting close!
"""
import os
import cv2
import wave
import time
import subprocess
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

t0 = time.time()
SCRATCH = r"C:\Users\Aria\.gemini\antigravity\scratch"
comp_andrew_mp4 = os.path.join(SCRATCH, "comp_v3_natural.mp4")
bg_mp4 = r"C:\Users\Aria\Desktop\ZOOM_BG_Alien_Mustang_Master_1080p.mp4"
ass_path = os.path.join(SCRATCH, "linkedin_captions_steve_jobs_hook.ass")

# Locate opening hook lip-sync video (1.10s .. 14.20s)
hook_candidates = [
    os.path.join(SCRATCH, "steve_jobs_hook_kling_pro.mp4"),
    os.path.join(SCRATCH, "steve_jobs_hook_kling_std.mp4"),
]
steve_hook_mp4 = None
for c in hook_candidates:
    if os.path.exists(c) and os.path.getsize(c) > 100000:
        steve_hook_mp4 = c
        break
if not steve_hook_mp4:
    raise FileNotFoundError("Opening hook lip-sync MP4 not found!")

# Locate midway lip-sync video (22.50s .. 36.60s)
mid_candidates = [
    os.path.join(SCRATCH, "steve_jobs_lipsync_kling_pro.mp4"),
    os.path.join(SCRATCH, "steve_jobs_lipsync_kling_std.mp4"),
]
steve_mid_mp4 = None
for c in mid_candidates:
    if os.path.exists(c) and os.path.getsize(c) > 100000:
        steve_mid_mp4 = c
        break

print(f"[1/4] Hook video: {steve_hook_mp4}\n      Mid video:  {steve_mid_mp4}")

# 1. Normalize Steve Jobs Hook STS audio to 48kHz mono WAV (-15 LUFS)
steve_eq_chain = (
    "highpass=f=80,"
    "equalizer=f=160:width_type=q:w=1.2:g=2.5,"
    "equalizer=f=3500:width_type=q:w=1.2:g=2.0,"
    "acompressor=threshold=-18dB:ratio=2.2:attack=15:release=180:makeup=2,"
    "loudnorm=I=-15:TP=-1.5:LRA=11"
)
steve_hook_wav = os.path.join(SCRATCH, "steve_hook_norm48.wav")
subprocess.run([
    "ffmpeg", "-y", "-i", os.path.join(SCRATCH, "steve_jobs_sts_hook.mp3"),
    "-af", steve_eq_chain,
    "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", steve_hook_wav
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def read_wav_mono(path):
    with wave.open(path, "rb") as wf:
        return np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float64)

a_Full = read_wav_mono(os.path.join(SCRATCH, "andrew_full_norm48.wav"))
s_Hook = read_wav_mono(steve_hook_wav)
s_Mid = read_wav_mono(os.path.join(SCRATCH, "steve_midway_norm48.wav"))

sr = 48000
def make_swap_sfx(dur=0.22, sr=48000):
    t = np.linspace(0, dur, int(dur * sr), endpoint=False)
    env = np.sin(np.pi * t / dur) ** 1.5
    phase = 2 * np.pi * (240 * t + (720 / (2 * dur)) * (t ** 2))
    sig = 0.45 * np.sin(phase) + 0.25 * np.sin(2.0 * phase) + 0.15 * np.sin(3.0 * phase)
    return sig * env * 4200.0

sfx = make_swap_sfx(0.22, sr)
half_sfx = len(sfx) // 2
xfade = int(0.025 * sr)
fade_in = np.linspace(0.0, 1.0, xfade)
fade_out = 1.0 - fade_in

out_audio = a_Full.copy()

def splice_segment(t_start, t_end, seg_wav):
    i0 = int(t_start * sr)
    i1 = int(t_end * sr)
    tlen = i1 - i0
    if len(seg_wav) < tlen:
        seg = np.pad(seg_wav, (0, tlen - len(seg_wav)))
    else:
        seg = seg_wav[:tlen]
    out_audio[i0:i1] = seg
    out_audio[i0:i0+xfade] = a_Full[i0:i0+xfade] * fade_out + seg[:xfade] * fade_in
    out_audio[i1-xfade:i1] = seg[-xfade:] * fade_out + a_Full[i1-xfade:i1] * fade_in
    out_audio[i0-half_sfx : i0-half_sfx+len(sfx)] += sfx
    out_audio[i1-half_sfx : i1-half_sfx+len(sfx)] += sfx[::-1]

splice_segment(1.10, 14.20, s_Hook)
splice_segment(22.50, 36.60, s_Mid)

out_audio_i16 = np.clip(out_audio, -32767, 32767).astype(np.int16)
hook_swap_wav = os.path.join(SCRATCH, "audio_steve_jobs_hook_swap.wav")
with wave.open(hook_swap_wav, "wb") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(sr)
    wf.writeframes(out_audio_i16.tobytes())

hook_swap_aac = os.path.join(SCRATCH, "audio_steve_jobs_hook_swap.aac")
subprocess.run([
    "ffmpeg", "-y", "-i", hook_swap_wav,
    "-c:a", "aac", "-b:a", "192k", hook_swap_aac
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"[2/4] Spliced Opening Hook + Midway Steve Jobs audio master ready ({time.time()-t0:.1f}s)")

# 2. Normalize Steve Jobs Hook video to 30fps 1920x1080 (13.10s = 393 frames)
steve_hook_30fps = os.path.join(SCRATCH, "steve_jobs_hook_30fps_1080p.mp4")
subprocess.run([
    "ffmpeg", "-y", "-i", steve_hook_mp4,
    "-vf", "fps=30,scale=1920:1080:flags=lanczos",
    "-t", "13.10",
    "-an", "-c:v", "h264_nvenc", "-preset", "p5", "-cq", "15", "-pix_fmt", "yuv420p",
    steve_hook_30fps
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

steve_mid_30fps = os.path.join(SCRATCH, "steve_jobs_midway_30fps_1080p.mp4")

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

bg_frames = load_frames(bg_mp4)
num_bg = len(bg_frames)
hook_frames = load_frames(steve_hook_30fps)
mid_frames = load_frames(steve_mid_30fps)

def guided_filter(I, p, r=10, eps=5e-4):
    ksize = (2*r+1, 2*r+1)
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

# Frame indices at 30fps:
# Window 1 (Opening Hook): 1.10s (f=33) .. 14.20s (f=426)
# Window 2 (Midway Core):  22.50s (f=675) .. 36.60s (f=1098)
h_start, h_end = 33, 426
m_start, m_end = 675, 1098

comp_hook_mp4 = os.path.join(SCRATCH, "comp_v5_steve_jobs_max_hook.mp4")
ff_proc = subprocess.Popen([
    "ffmpeg", "-y",
    "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", "1920x1080", "-r", "30",
    "-i", "-",
    "-c:v", "h264_nvenc", "-preset", "p5", "-cq", "16", "-b:v", "18M", "-pix_fmt", "yuv420p",
    comp_hook_mp4
], stdin=subprocess.PIPE)

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
print(f"[3/4] Composited {total_frames} frames with Instant Hook + Midway Steve Jobs Swap in {time.time()-t0:.1f}s")

ass_escaped = ass_path.replace("\\", "/").replace(":", "\\:")
final_1080p = r"C:\Users\Aria\Desktop\ARIA_TECH_GROUP_LinkedIn_SteveJobs_MaxHook_1080p.mp4"
final_2k = r"C:\Users\Aria\Desktop\ARIA_TECH_GROUP_LinkedIn_SteveJobs_MaxHook_2K.mp4"
# Also overwrite ARIA_TECH_GROUP_LinkedIn_SteveJobs_Swap_1080p.mp4 so both filenames have the MaxHook master!
swap_1080p = r"C:\Users\Aria\Desktop\ARIA_TECH_GROUP_LinkedIn_SteveJobs_Swap_1080p.mp4"

subprocess.run([
    "ffmpeg", "-y",
    "-i", comp_hook_mp4,
    "-i", hook_swap_aac,
    "-vf", f"ass='{ass_escaped}',unsharp=5:5:0.35:5:5:0.0",
    "-map_metadata", "-1",
    "-c:v", "h264_nvenc", "-preset", "p6", "-cq", "16", "-b:v", "16M", "-pix_fmt", "yuv420p",
    "-c:a", "copy",
    "-shortest", "-movflags", "+faststart",
    final_1080p
], check=True)

import shutil
shutil.copy2(final_1080p, swap_1080p)

subprocess.run([
    "ffmpeg", "-y",
    "-i", comp_hook_mp4,
    "-i", hook_swap_aac,
    "-vf", f"ass='{ass_escaped}',scale=2560:1440:flags=lanczos,unsharp=5:5:0.5:5:5:0.0",
    "-map_metadata", "-1",
    "-c:v", "h264_nvenc", "-preset", "p6", "-cq", "16", "-b:v", "24M", "-pix_fmt", "yuv420p",
    "-c:a", "copy",
    "-shortest", "-movflags", "+faststart",
    final_2k
], check=True)

for ts, name in [("1.1", "verify_hook_morph_1_1s.jpg"), ("3.5", "verify_hook_steve_3_5s.jpg"), ("11.0", "verify_hook_steve_11s.jpg")]:
    subprocess.run([
        "ffmpeg", "-y", "-ss", ts, "-i", final_1080p, "-frames:v", "1", "-update", "1",
        os.path.join(SCRATCH, name)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

print(f"[4/4] ALL DONE in {time.time()-t0:.1f}s! Saved:\n  - {final_1080p}\n  - {final_2k}")
