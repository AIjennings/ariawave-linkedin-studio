#!/usr/bin/env python3
"""
Render the 9:16 Vertical Split-Stage / Token-Arbitrage Master (1080x1920, 57.8s)
from comp_v6_steve_jobs_zerocost_heygen4.mp4 for YouTube Shorts, TikTok, Instagram Reels, and X!
"""
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

SCRATCH = r"C:\Users\Aria\.gemini\antigravity\scratch"
src_clean_mp4 = os.path.join(SCRATCH, "comp_v6_steve_jobs_zerocost_heygen4.mp4")
src_audio_aac = os.path.join(SCRATCH, "audio_steve_jobs_hook_swap.aac")
ass_9x16 = os.path.join(SCRATCH, "steve_jobs_9x16_captions.ass")

ov_png = os.path.join(SCRATCH, "steve_jobs_zerocost_9x16_hud.png")
img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

def load_font(names, size):
    for n in names:
        try:
            return ImageFont.truetype(n, size)
        except Exception:
            pass
    return ImageFont.load_default()

f_hook1 = load_font(["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf"], 35)
f_hook2 = load_font(["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf"], 37)
f_badge = load_font(["C:/Windows/Fonts/consolab.ttf", "C:/Windows/Fonts/arialbd.ttf"], 21)
f_term_title = load_font(["C:/Windows/Fonts/consolab.ttf", "C:/Windows/Fonts/arialbd.ttf"], 23)
f_term_cta = load_font(["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf"], 28)
f_term_sub = load_font(["C:/Windows/Fonts/consolab.ttf", "C:/Windows/Fonts/arialbd.ttf"], 22)

# Top Banner: Token Management & $0.00 Subscription Arbitrage Hook
draw.rectangle([0, 0, 1080, 260], fill=(5, 8, 15, 245))
draw.rounded_rectangle([28, 28, 1052, 236], radius=22, fill=(10, 16, 28, 250), outline=(136, 255, 0, 255), width=4)
draw.text((540, 76), "HOW WE DROPPED THIS AI VIDEO FROM $3.24 TO $0.00", font=f_hook1, fill=(255, 255, 255, 255), anchor="mm")
draw.text((540, 130), "USING UNUSED SUBSCRIPTION TOKENS + WEBBRIDGE", font=f_hook2, fill=(136, 255, 0, 255), anchor="mm")
draw.text((540, 192), "HEYGEN AVATAR 4 (8,484 UNUSED CREDITS) • GEMINI 2.5 FLASH ROUTER", font=f_badge, fill=(0, 232, 255, 255), anchor="mm")

# Bottom Conversion Terminal Card: Why You Need Aria to Manage Your AI Tokens
draw.rectangle([0, 1540, 1080, 1920], fill=(5, 8, 15, 248))
draw.rounded_rectangle([28, 1560, 1052, 1888], radius=22, fill=(6, 14, 12, 252), outline=(0, 232, 255, 255), width=4)
draw.text((60, 1605), "> TOKEN MANAGEMENT STRATEGY: STOP PAYING TWICE FOR AI", font=f_term_title, fill=(136, 255, 0, 255))
draw.text((60, 1662), "LET ARIA MANAGE YOUR AI STACK: ARIAWAVE.TECH/#CONTACT", font=f_term_cta, fill=(255, 255, 255, 255))
draw.text((60, 1725), "> OPEN-SOURCE REPO: github.com/AIjennings/ariawave-linkedin-studio", font=f_term_sub, fill=(0, 232, 255, 255))
draw.text((60, 1775), "> BOOK 1-ON-1 AUDIT: scheduler.zoom.us/andrew-jennings-rzou8s", font=f_term_sub, fill=(255, 168, 216, 255))
draw.text((60, 1828), "> 85% OF SAAS AI CREDITS EXPIRE UNUSED — WE HARVEST THEM", font=f_term_title, fill=(136, 255, 0, 255))

img.save(ov_png)

ass_escaped = ass_9x16.replace("\\", "/").replace(":", "\\:")
out_9x16 = r"C:\Users\Aria\Desktop\ARIA_TECH_GROUP_SteveJobs_ZeroCost_TokenStrategy_9x16.mp4"
out_9x16_fast = os.path.join(SCRATCH, "STEVE_JOBS_ZEROCOST_TOKEN_9x16_FAST.mp4")

filter_complex = (
    f"[0:v]scale=2276:1280:flags=lanczos,crop=1080:1280:598:0[center];"
    f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=24:4[bg];"
    f"[bg][center]overlay=0:260[v1];"
    f"[v1][1:v]overlay=0:0[v2];"
    f"[v2]ass='{ass_escaped}',unsharp=5:5:0.35:5:5:0.0[vout]"
)

subprocess.run([
    "ffmpeg", "-y",
    "-i", src_clean_mp4,
    "-i", ov_png,
    "-i", src_audio_aac,
    "-filter_complex", filter_complex,
    "-map", "[vout]", "-map", "2:a",
    "-c:v", "h264_nvenc", "-preset", "p6", "-cq", "19", "-b:v", "8M", "-pix_fmt", "yuv420p",
    "-c:a", "copy", "-shortest", "-movflags", "+faststart",
    out_9x16
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

subprocess.run([
    "ffmpeg", "-y",
    "-i", out_9x16,
    "-c:v", "h264_nvenc", "-preset", "p6", "-cq", "24", "-b:v", "3.5M", "-maxrate", "4.5M", "-bufsize", "8M", "-pix_fmt", "yuv420p",
    "-c:a", "copy", "-movflags", "+faststart",
    out_9x16_fast
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

print("Rendered 9:16 Token Strategy Master:", out_9x16, os.path.getsize(out_9x16))
print("Rendered 9:16 Fast Upload Stream:", out_9x16_fast, os.path.getsize(out_9x16_fast))
