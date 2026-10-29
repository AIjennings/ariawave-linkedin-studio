#!/usr/bin/env python3
"""
Build the complete 57.8s LinkedIn Master Video with the Midway Steve Jobs Character & Voice Swap (22.50s - 36.60s)!
- Segment 1 (0.00s - 22.50s): Andrew Jennings (comp_v3_natural.mp4 + single_mic_dry.wav)
- Segment 2 (22.50s - 36.60s): Steve Jobs (lip-synced via OmniHuman v1.5 / Kling Avatar v2, matted onto the
  continuously moving Alien Gunship + Mustang background via O(1) Guided Filter so the background never freezes,
  with cyber-holographic RGB scanline swap transition effects at t=22.50s and t=36.60s)
- Segment 3 (36.60s - 57.80s): Andrew Jennings close (ariawave.tech + Aria Technology Group consulting)
"""
import os
import sys
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
ass_path = os.path.join(SCRATCH, "linkedin_captions_steve_jobs.ass")

# Pick best available lip-sync video (prefer kling_pro or omnihuman, or whichever completed first)
candidates = [
    os.path.join(SCRATCH, "steve_jobs_lipsync_omnihuman.mp4"),
    os.path.join(SCRATCH, "steve_jobs_lipsync_kling_pro.mp4"),
    os.path.join(SCRATCH, "steve_jobs_lipsync_kling_std.mp4"),
]
steve_mp4 = None
for c in candidates:
    if os.path.exists(c) and os.path.getsize(c) > 100000:
        steve_mp4 = c
        break

if not steve_mp4:
    raise FileNotFoundError("No Steve Jobs lip-sync MP4 found yet!")
print(f"[1/4] Using Steve Jobs lip-sync video: {steve_mp4}")

# 1. Build the spliced 48kHz Audio Master (0..22.50s Andrew + 22.50..36.60s Steve Jobs STS + 36.60..57.80s Andrew)
# First convert single_mic_dry.aac and steve_jobs_sts_midway.mp3 to 48kHz mono WAVs with matched -15 LUFS loudness
andrew_norm_wav = os.path.join(SCRATCH, "andrew_full_norm48.wav")
steve_norm_wav = os.path.join(SCRATCH, "steve_midway_norm48.wav")

subprocess.run([
    "ffmpeg", "-y", "-i", os.path.join(SCRATCH, "single_mic_dry.aac"),
    "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", andrew_norm_wav
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

steve_eq_chain = (
    "highpass=f=80,"
    "equalizer=f=160:width_type=q:w=1.2:g=2.5,"
    "equalizer=f=3500:width_type=q:w=1.2:g=2.0,"
    "acompressor=threshold=-18dB:ratio=2.2:attack=15:release=180:makeup=2,"
    "loudnorm=I=-15:TP=-1.5:LRA=11"
)
subprocess.run([
    "ffmpeg", "-y", "-i", os.path.join(SCRATCH, "steve_jobs_sts_midway.mp3"),
    "-af", steve_eq_chain,
    "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", steve_norm_wav
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def read_wav_mono(path):
    with wave.open(path, "rb") as wf:
        return np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float64)

a_Full = read_wav_mono(andrew_norm_wav)
s_Mid = read_wav_mono(steve_norm_wav)

sr = 48000
idx_start = int(22.50 * sr)
idx_end = int(36.60 * sr)
target_len = idx_end - idx_start

# Pad or trim s_Mid to exact target_len (14.10s = 676,800 samples)
if len(s_Mid) < target_len:
    s_Mid = np.pad(s_Mid, (0, target_len - len(s_Mid)))
else:
    s_Mid = s_Mid[:target_len]

# Subtle futuristic holographic swap whoosh/chime at 22.50s and 36.60s (180ms each, clean sci-fi synth sweep)
def make_swap_sfx(dur=0.22, sr=48000):
    t = np.linspace(0, dur, int(dur * sr), endpoint=False)
    env = np.sin(np.pi * t / dur) ** 1.5
    # Frequency sweep 240Hz -> 960Hz + harmonic shimmer
    phase = 2 * np.pi * (240 * t + (720 / (2 * dur)) * (t ** 2))
    sig = 0.45 * np.sin(phase) + 0.25 * np.sin(2.0 * phase) + 0.15 * np.sin(3.0 * phase)
    return sig * env * 4200.0

sfx = make_swap_sfx(0.22, sr)
half_sfx = len(sfx) // 2

# Crossfade 25ms at boundaries
xfade = int(0.025 * sr)
out_audio = a_Full.copy()
out_audio[idx_start:idx_end] = s_Mid

# Smooth crossfade at idx_start and idx_end
fade_in = np.linspace(0.0, 1.0, xfade)
fade_out = 1.0 - fade_in
out_audio[idx_start:idx_start+xfade] = a_Full[idx_start:idx_start+xfade] * fade_out + s_Mid[:xfade] * fade_in
out_audio[idx_end-xfade:idx_end] = s_Mid[-xfade:] * fade_out + a_Full[idx_end-xfade:idx_end] * fade_in

# Mix subtle sci-fi holographic morph chime at swap points
out_audio[idx_start-half_sfx : idx_start-half_sfx+len(sfx)] += sfx
out_audio[idx_end-half_sfx : idx_end-half_sfx+len(sfx)] += sfx[::-1]

out_audio_i16 = np.clip(out_audio, -32767, 32767).astype(np.int16)
swap_wav = os.path.join(SCRATCH, "audio_steve_jobs_swap.wav")
with wave.open(swap_wav, "wb") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(sr)
    wf.writeframes(out_audio_i16.tobytes())

swap_aac = os.path.join(SCRATCH, "audio_steve_jobs_swap.aac")
subprocess.run([
    "ffmpeg", "-y", "-i", swap_wav,
    "-c:a", "aac", "-b:a", "192k", swap_aac
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"[2/4] Spliced Andrew <-> Steve Jobs audio master ready ({time.time()-t0:.1f}s)")

# 2. Normalize Steve Jobs lip-sync video to 30.00 fps, 1920x1080, exact 423 frames (14.10s)
steve_30fps_mp4 = os.path.join(SCRATCH, "steve_jobs_midway_30fps_1080p.mp4")
subprocess.run([
    "ffmpeg", "-y", "-i", steve_mp4,
    "-vf", "fps=30,scale=1920:1080:flags=lanczos",
    "-t", "14.10",
    "-an", "-c:v", "h264_nvenc", "-preset", "p5", "-cq", "15", "-pix_fmt", "yuv420p",
    steve_30fps_mp4
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Load moving background frames so the Alien Gunship + Mustang behind Steve Jobs keep moving seamlessly!
cap_bg = cv2.VideoCapture(bg_mp4)
bg_frames = []
while True:
    ret, frame = cap_bg.read()
    if not ret:
        break
    bg_frames.append(frame)
cap_bg.release()
num_bg = len(bg_frames)

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

cap_steve = cv2.VideoCapture(steve_30fps_mp4)
steve_raw_frames = []
while True:
    ret, f = cap_steve.read()
    if not ret:
        break
    steve_raw_frames.append(f)
cap_steve.release()

vignette = np.ones((1080, 1920, 1), dtype=np.float32)
vignette[840:1080, :, :] = np.linspace(1.0, 0.45, 240, dtype=np.float32)[:, None, None]

# Composite all frames: 0..675 = Andrew, 675..1098 = Steve Jobs over moving Alien Gunship BG, 1098..end = Andrew
cap_andrew = cv2.VideoCapture(comp_andrew_mp4)
total_frames = int(cap_andrew.get(cv2.CAP_PROP_FRAME_COUNT))
swap_start_f = 675   # 22.50s * 30fps
swap_end_f = 1098    # 36.60s * 30fps

comp_swap_mp4 = os.path.join(SCRATCH, "comp_v4_steve_jobs_swap.mp4")
ff_proc = subprocess.Popen([
    "ffmpeg", "-y",
    "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", "1920x1080", "-r", "30",
    "-i", "-",
    "-c:v", "h264_nvenc", "-preset", "p5", "-cq", "16", "-b:v", "18M", "-pix_fmt", "yuv420p",
    comp_swap_mp4
], stdin=subprocess.PIPE)

def apply_holo_glitch(frame_a, frame_b, progress):
    """
    Crisp futuristic holographic character-swap effect over 8 frames (~0.26s):
    blends frame_a -> frame_b with chromatic RGB shift, cyan/green holographic scanlines, and brief luma flash.
    """
    blended = cv2.addWeighted(frame_a, 1.0 - progress, frame_b, progress, 0.0).copy()
    intensity = np.sin(np.pi * progress)
    shift = int(22 * intensity)
    if shift > 0:
        # Horizontal RGB chromatic split
        blended[:, shift:, 2] = blended[:, :-shift, 2]   # Red channel right
        blended[:, :-shift, 0] = blended[:, shift:, 0]   # Blue channel left
    # Holographic horizontal scanlines + subtle cyan/green digital flash
    scan = np.zeros_like(blended, dtype=np.float32)
    scan[::4, :, 1] = 75.0 * intensity  # Green/cyan scanline
    scan[::4, :, 0] = 65.0 * intensity
    res = np.clip(blended.astype(np.float32) + scan + (28.0 * intensity), 0, 255).astype(np.uint8)
    return res

prev_alpha = None
for idx in range(total_frames):
    ret, andrew_frame = cap_andrew.read()
    if not ret:
        break

    if swap_start_f - 4 <= idx < swap_end_f + 4:
        # Compute matted Steve Jobs frame over the live moving Alien Gunship + Mustang background
        s_idx = min(max(idx - swap_start_f, 0), len(steve_raw_frames) - 1)
        fg = steve_raw_frames[s_idx]
        bg = bg_frames[idx % num_bg]

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

        steve_comp = np.clip((fg.astype(np.float32) * alpha + bg.astype(np.float32) * (1.0 - alpha)) * vignette, 0, 255).astype(np.uint8)

        # Apply holographic transition across the 8 frames centered on swap_start_f and swap_end_f
        if idx < swap_start_f + 4:
            prog = (idx - (swap_start_f - 4)) / 8.0
            out_frame = apply_holo_glitch(andrew_frame, steve_comp, prog)
        elif idx >= swap_end_f - 4:
            prog = (idx - (swap_end_f - 4)) / 8.0
            out_frame = apply_holo_glitch(steve_comp, andrew_frame, prog)
        else:
            out_frame = steve_comp
    else:
        out_frame = andrew_frame

    ff_proc.stdin.write(out_frame.tobytes())

cap_andrew.release()
ff_proc.stdin.close()
ff_proc.wait()
print(f"[3/4] Composited {total_frames} frames with Midway Steve Jobs Swap in {time.time()-t0:.1f}s")

# 4. Burn ASS captions + export 1080p and 2K QHD masters to Desktop!
ass_escaped = ass_path.replace("\\", "/").replace(":", "\\:")
final_1080p = r"C:\Users\Aria\Desktop\ARIA_TECH_GROUP_LinkedIn_SteveJobs_Swap_1080p.mp4"
final_2k = r"C:\Users\Aria\Desktop\ARIA_TECH_GROUP_LinkedIn_SteveJobs_Swap_2K.mp4"

subprocess.run([
    "ffmpeg", "-y",
    "-i", comp_swap_mp4,
    "-i", swap_aac,
    "-vf", f"ass='{ass_escaped}',unsharp=5:5:0.35:5:5:0.0",
    "-map_metadata", "-1",
    "-c:v", "h264_nvenc", "-preset", "p6", "-cq", "16", "-b:v", "16M", "-pix_fmt", "yuv420p",
    "-c:a", "copy",
    "-shortest", "-movflags", "+faststart",
    final_1080p
], check=True)

subprocess.run([
    "ffmpeg", "-y",
    "-i", comp_swap_mp4,
    "-i", swap_aac,
    "-vf", f"ass='{ass_escaped}',scale=2560:1440:flags=lanczos,unsharp=5:5:0.5:5:5:0.0",
    "-map_metadata", "-1",
    "-c:v", "h264_nvenc", "-preset", "p6", "-cq", "16", "-b:v", "24M", "-pix_fmt", "yuv420p",
    "-c:a", "copy",
    "-shortest", "-movflags", "+faststart",
    final_2k
], check=True)

# Extract verification keyframes during Steve Jobs takeover (t=25.0s and t=33.5s) and transition (t=22.5s)
for ts, name in [("22.5", "verify_steve_transition_22_5s.jpg"), ("25.0", "verify_steve_takeover_25s.jpg"), ("33.5", "verify_steve_takeover_33_5s.jpg")]:
    subprocess.run([
        "ffmpeg", "-y", "-ss", ts, "-i", final_1080p, "-frames:v", "1", "-update", "1",
        os.path.join(SCRATCH, name)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

print(f"[4/4] ALL DONE in {time.time()-t0:.1f}s! Saved:\n  - {final_1080p}\n  - {final_2k}")
