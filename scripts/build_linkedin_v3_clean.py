import cv2
import numpy as np
import wave
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import subprocess
import os
import time

t0 = time.time()
scratch = r"C:\Users\Aria\.gemini\antigravity\scratch"
vid_trimmed = os.path.join(scratch, "trimmed_fg_30fps.mp4")
bg_mp4 = r"C:\Users\Aria\Desktop\ZOOM_BG_Alien_Mustang_Master_1080p.mp4"
ass_path = os.path.join(scratch, "linkedin_captions.ass")

# 1. Build 100% Dry Single-Mic Audio via Stereo Difference (L - R cancels mono USB Mic Backup!)
w = wave.open(os.path.join(scratch, "orig48.wav"))
raw = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).reshape(-1, 2).astype(np.float64)

KEEP_SEGMENTS = [
    (1.65, 8.38),
    (8.92, 11.42),
    (12.56, 17.65),
    (18.72, 62.20),
]

chunks = []
for s, e in KEEP_SEGMENTS:
    L = raw[int(s*48000):int(e*48000), 0]
    R = raw[int(s*48000):int(e*48000), 1]
    # L - R cancels the mono USB Mic Backup (which is identical on L & R) while preserving the stereo Insta360 X5 voice!
    diff = (L - R) * 0.80
    fade_len = int(0.015 * 48000)
    diff[:fade_len] *= np.linspace(0, 1, fade_len)
    diff[-fade_len:] *= np.linspace(1, 0, fade_len)
    chunks.append(diff)

sig_dry = np.clip(np.concatenate(chunks), -32767, 32767).astype(np.int16)
dry_wav = os.path.join(scratch, "single_mic_dry.wav")
with wave.open(dry_wav, "wb") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(48000)
    wf.writeframes(sig_dry.tobytes())

audio_dry_aac = os.path.join(scratch, "single_mic_dry.aac")
# Pure analog-style EQ + compressor + loudnorm (ZERO spectral/FFT denoise = ZERO wateriness!)
eq_chain = (
    "highpass=f=85,"
    "equalizer=f=145:width_type=q:w=1.1:g=3.0,"
    "equalizer=f=330:width_type=q:w=1.5:g=-2.5,"
    "equalizer=f=4000:width_type=q:w=1.2:g=2.0,"
    "acompressor=threshold=-18dB:ratio=2.2:attack=15:release=180:makeup=2,"
    "loudnorm=I=-15:TP=-1.5:LRA=11"
)
subprocess.run([
    "ffmpeg", "-y", "-i", dry_wav,
    "-af", eq_chain,
    "-c:a", "aac", "-b:a", "192k", audio_dry_aac
], check=True)
print(f"[1/3] Single-mic dry audio mastered in {time.time()-t0:.1f}s")

# 2. Load dry-interior Alien Mustang background frames
cap_bg = cv2.VideoCapture(bg_mp4)
bg_frames = []
while True:
    ret, frame = cap_bg.read()
    if not ret:
        break
    bg_frames.append(frame)
cap_bg.release()
num_bg = len(bg_frames)

# Fast O(1) Guided Filter for natural, non-distorted face/ear/hair matting
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

base_options = python.BaseOptions(model_asset_path=os.path.join(scratch, "selfie_segmenter.tflite"))
options = vision.ImageSegmenterOptions(base_options=base_options, output_confidence_masks=True)
segmenter = vision.ImageSegmenter.create_from_options(options)

cap_fg = cv2.VideoCapture(vid_trimmed)
total_frames = int(cap_fg.get(cv2.CAP_PROP_FRAME_COUNT))
print(f"[2/3] Compositing {total_frames} frames with Guided Matting (zero face distortion)...")

comp_clean = os.path.join(scratch, "comp_v3_natural.mp4")
ff_proc = subprocess.Popen([
    "ffmpeg", "-y",
    "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", "1920x1080", "-r", "30",
    "-i", "-",
    "-c:v", "h264_nvenc", "-preset", "p5", "-cq", "16", "-b:v", "18M", "-pix_fmt", "yuv420p",
    comp_clean
], stdin=subprocess.PIPE)

vignette = np.ones((1080, 1920, 1), dtype=np.float32)
vignette[840:1080, :, :] = np.linspace(1.0, 0.45, 240, dtype=np.float32)[:, None, None]

prev_alpha = None
idx = 0
while True:
    ret, fg = cap_fg.read()
    if not ret:
        break

    bg = bg_frames[idx % num_bg]

    # Segment at 640x360 and upsample to 1920x1080 before Guided Filter at full 1080p!
    # That gives full 1080p edge precision at 3x the speed!
    fg_small = cv2.resize(fg, (640, 360), interpolation=cv2.INTER_LINEAR)
    mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(fg_small, cv2.COLOR_BGR2RGB))
    res = segmenter.segment(mp_img)
    mask_s = res.confidence_masks[0].numpy_view()
    if mask_s.ndim == 3:
        mask_s = mask_s[:, :, 0]
    mask = cv2.resize(mask_s, (1920, 1080), interpolation=cv2.INTER_LINEAR)

    b, g, r_ch = fg[:,:,0].astype(np.float32), fg[:,:,1].astype(np.float32), fg[:,:,2].astype(np.float32)
    luma_255 = 0.114*b + 0.587*g + 0.299*r_ch
    luma = luma_255 / 255.0
    skin_ness = np.clip((r_ch - b - 14.0) / 25.0, 0.0, 1.0)
    dark_ness = np.clip((122.0 - luma_255) / 30.0, 0.0, 1.0)
    is_room_bg = (1.0 - np.maximum(skin_ness, dark_ness))

    # Suppress room wall in outer boundary while keeping 100% of ears, hair, and face
    p_raw = np.clip((mask - 0.22) / 0.45, 0.0, 1.0).astype(np.float32)
    p_cleaned = p_raw * (1.0 - 0.88 * is_room_bg * np.clip((0.92 - mask) / 0.45, 0.0, 1.0))

    guide = np.clip(luma - 0.45 * skin_ness, 0.0, 1.0).astype(np.float32)
    alpha_gf = guided_filter(guide, p_cleaned, r=10, eps=5e-4)
    alpha_gf = np.clip((alpha_gf - 0.18) / 0.68, 0.0, 1.0)

    if prev_alpha is not None:
        alpha_gf = 0.75 * alpha_gf + 0.25 * prev_alpha
    prev_alpha = alpha_gf

    alpha = alpha_gf[..., None]

    # Natural, untouched face pixels with gentle global white-balance correction (no plastic bilateral blur!)
    fg_f = fg.astype(np.float32)
    fg_f[:, :, 0] = np.clip(fg_f[:, :, 0] * 1.05 + 3.0, 0, 255)
    fg_f[:, :, 1] = np.clip(fg_f[:, :, 1] * 1.03 + 2.0, 0, 255)
    fg_f[:, :, 2] = np.clip(fg_f[:, :, 2] * 1.00 + 1.0, 0, 255)

    comp = (fg_f * alpha + bg.astype(np.float32) * (1.0 - alpha)) * vignette
    out_frame = np.clip(comp, 0, 255).astype(np.uint8)

    ff_proc.stdin.write(out_frame.tobytes())
    idx += 1

cap_fg.release()
ff_proc.stdin.close()
ff_proc.wait()
print(f"[2/3] Composited {idx} frames in {time.time()-t0:.1f}s")

# 3. Burn ASS captions + export 1080p and 2K QHD masters
ass_escaped = ass_path.replace("\\", "/").replace(":", "\\:")
final_1080p = r"C:\Users\Aria\Desktop\ARIA_TECH_GROUP_LinkedIn_Final_1080p.mp4"
final_2k = r"C:\Users\Aria\Desktop\ARIA_TECH_GROUP_LinkedIn_Upscaled_2K.mp4"

subprocess.run([
    "ffmpeg", "-y",
    "-i", comp_clean,
    "-i", audio_dry_aac,
    "-vf", f"ass='{ass_escaped}',unsharp=5:5:0.35:5:5:0.0",
    "-c:v", "h264_nvenc", "-preset", "p6", "-cq", "16", "-b:v", "16M", "-pix_fmt", "yuv420p",
    "-c:a", "copy",
    "-shortest", "-movflags", "+faststart",
    final_1080p
], check=True)

subprocess.run([
    "ffmpeg", "-y",
    "-i", comp_clean,
    "-i", audio_dry_aac,
    "-vf", f"ass='{ass_escaped}',scale=2560:1440:flags=lanczos,unsharp=5:5:0.5:5:5:0.0",
    "-c:v", "h264_nvenc", "-preset", "p6", "-cq", "16", "-b:v", "24M", "-pix_fmt", "yuv420p",
    "-c:a", "copy",
    "-shortest", "-movflags", "+faststart",
    final_2k
], check=True)

subprocess.run([
    "ffmpeg", "-y", "-ss", "2.0", "-i", final_1080p, "-frames:v", "1", "-update", "1",
    os.path.join(scratch, "verify_v3_2s.jpg")
], check=True)

print(f"[3/3] ALL DONE in {time.time()-t0:.1f}s!")
